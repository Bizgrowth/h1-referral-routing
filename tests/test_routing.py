import pytest

from h1 import importer, scoring, suggest
from h1.validate import find_issues

GOOD = {"referral_source": "Source A", "product_description": "PRODUCT_A", "product_group": "GROUP_1",
        "hcpcs_code": "E0000", "quantity": "1", "insurance_company_city": "CITY_A",
        "diag_code_2": "", "diag_code_4": ""}


def test_good_row_has_no_flags():
    assert find_issues(GOOD) == []


def test_blank_diagnosis_codes_never_flagged():
    assert find_issues({**GOOD, "diag_code_2": "", "diag_code_4": ""}) == []
    assert find_issues({**GOOD, "diag_code_2": "724.2", "diag_code_4": "V54.81"}) == []


@pytest.mark.parametrize("change, expected", [
    ({"referral_source": ""}, "Missing referral_source"),
    ({"product_description": ""}, "Missing product_description"),
    ({"product_group": ""}, "Missing product_group"),
    ({"hcpcs_code": ""}, "Missing hcpcs_code"),
    ({"quantity": ""}, "Missing quantity"),
    ({"insurance_company_city": ""}, "Missing insurance_company_city"),
    ({"hcpcs_code": "E00"}, "Invalid hcpcs_code"),
    ({"quantity": "0"}, "Invalid quantity"),
    ({"quantity": "-2"}, "Invalid quantity"),
    ({"quantity": "two"}, "Invalid quantity"),
    ({"diag_code_2": "ABC"}, "Invalid diag_code_2"),
    ({"diag_code_4": "12"}, "Invalid diag_code_4"),
])
def test_each_bad_case_is_flagged(change, expected):
    issues = find_issues({**GOOD, **change})
    assert len(issues) == 1 and issues[0].startswith(expected)


def test_train_test_split_has_no_overlap(xlsx_path):
    train, test = scoring.split(importer.load(xlsx_path).rows)
    assert set(train["year"]) == {2024, 2025} and set(test["year"]) == {2026}
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
    rows = importer.load(xlsx_path).rows
    train, _ = scoring.split(rows)
    model = suggest.Suggester.fit(train)
    city_b = {**GOOD, "product_description": "PRODUCT_B", "product_group": "GROUP_2", "hcpcs_code": "E0001",
              "insurance_company_city": "CITY_B"}
    top = model.suggest(city_b)
    assert [s.vendor for s in top] == ["Vendor 03", "Vendor 02"]
    assert "carrier city" in top[0].reason and "2 times" in top[0].reason
    unseen = model.suggest({**GOOD, "product_description": "PRODUCT_C"})
    assert unseen[0].vendor == "Vendor 01" and "HCPCS code in this product group" in unseen[0].reason


def test_blank_vendor_rows_excluded_from_scoring(xlsx_path):
    result = scoring.score(importer.load(xlsx_path).rows)
    assert result["intake"]["n"] == 6          # every 2026 referral goes through intake
    assert result["overall"]["n"] == 5         # the blank-vendor row is not scored
    assert result["intake"] == {"n": 6, "with_issue": 1, "flagged": 1}


def test_scoring_reports_baseline_and_multi_vendor(xlsx_path):
    result = scoring.score(importer.load(xlsx_path).rows)
    assert result["overall"] == {"n": 5, "tool_top1": 5, "tool_top3": 5, "base_top1": 3, "base_top3": 4}
    assert result["multi_vendor"] == {"n": 2, "tool_top1": 2, "tool_top3": 2, "base_top1": 1, "base_top3": 2}
    assert set(result["by_group"]) == {"GROUP_1", "GROUP_2"}
