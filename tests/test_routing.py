import pytest

from h1 import importer, scoring, suggest
from h1.validate import find_issues, issues_by_field

GOOD = {"referral_source": "Source A", "product_description": "PRODUCT_A", "product_group": "GROUP_1",
        "hcpcs_code": "E0000", "patient_state": "ST_A", "diag_code_1": ""}


def test_good_row_has_no_flags():
    assert find_issues(GOOD) == []


def test_blank_diagnosis_code_never_flagged():
    assert find_issues({**GOOD, "diag_code_1": ""}) == []
    assert find_issues({**GOOD, "diag_code_1": "724.2"}) == find_issues({**GOOD, "diag_code_1": "V54.81"}) == []


@pytest.mark.parametrize("change, expected", [
    ({"referral_source": ""}, "No referral source"),
    ({"product_description": ""}, "No product"),
    ({"product_group": ""}, "No service type"),
    ({"hcpcs_code": ""}, "HCPCS code blank or invalid"),
    ({"hcpcs_code": "E00"}, "HCPCS code blank or invalid"),
    ({"hcpcs_code": "99213"}, "HCPCS code blank or invalid"),
    ({"patient_state": ""}, "No state"),
    ({"diag_code_1": "ABC"}, "Diagnosis code not valid"),
])
def test_each_bad_case_is_flagged(change, expected):
    assert find_issues({**GOOD, **change}) == [expected]


def test_privacy_blanked_field_is_not_flagged_as_missing():
    row = {**GOOD, "product_description": "", "_privacy": "product_description,"}
    assert issues_by_field(row) == {}


def test_train_test_split_has_no_overlap(xlsx_path):
    train, test = scoring.split(importer.load(xlsx_path).rows)
    assert set(train["year"]) == {2025} and set(test["year"]) == {2026}
    assert not set(train["row_id"]) & set(test["row_id"])


def test_vendor_name_is_never_an_input_feature(xlsx_path):
    assert "answer_vendor" not in suggest.FEATURES and "vendor_name" not in suggest.FEATURES
    train, test = scoring.split(importer.load(xlsx_path).rows)
    model = suggest.Suggester.fit(train)
    query = test.to_dict("records")[0]
    before = model.suggest(query)
    after = model.suggest({**query, "answer_vendor": "Vendor 99", "vendor_name": "VENDOR_Q"})
    assert before == after


def test_suggestions_use_context_and_backoff(xlsx_path):
    train, _ = scoring.split(importer.load(xlsx_path).rows)
    model = suggest.Suggester.fit(train)
    state_b = {**GOOD, "product_description": "PRODUCT_B", "product_group": "GROUP_2", "hcpcs_code": "E0001",
               "patient_state": "ST_B"}
    top = model.suggest(state_b)
    assert [s.vendor for s in top] == ["Vendor 03", "Vendor 02"]
    assert "state" in top[0].reason and "2 times" in top[0].reason
    unseen = model.suggest({**GOOD, "product_description": "PRODUCT_C"})
    assert unseen[0].vendor == "Vendor 01" and "HCPCS code in this service type" in unseen[0].reason


def test_blank_vendor_rows_excluded_from_scoring(xlsx_path):
    result = scoring.score(importer.load(xlsx_path).rows)
    assert result["overall"]["n"] == 5         # the blank-vendor row is not scored
    assert result["intake"] == {"n": 6, "with_issue": 1, "flagged": 1}


def test_scoring_reports_baseline_and_multi_vendor(xlsx_path):
    result = scoring.score(importer.load(xlsx_path).rows)
    assert result["overall"] == {"n": 5, "tool_top1": 5, "tool_top3": 5, "base_top1": 3, "base_top3": 4}
    assert result["multi_vendor"] == {"n": 2, "tool_top1": 2, "tool_top3": 2, "base_top1": 1, "base_top3": 2}
    assert set(result["by_group"]) == {"GROUP_1", "GROUP_2"}
