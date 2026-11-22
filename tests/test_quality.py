import pandas as pd

from h1 import quality
from scripts import quality_report


def make(rows, path):
    pd.DataFrame(rows).to_excel(path, sheet_name="Sheet1", index=False)
    return path


def ref(group="GROUP_1", source="SRC_1", hcpcs="E0000", vendor="VENDOR_X", state="ST", diag="", product="PRODUCT_A",
        patient="17", year=2025):
    return {"hcpcs_code": hcpcs, "vendor_name": vendor, "patient_name": patient, "product_description": product,
            "product_group": group, "referral_source": source, "patient_state": state, "diag_code_1": diag,
            "date of referral": year}


def problems(**change):
    row = {"hcpcs_code": "E0000", "answer_vendor": "Vendor 01", "product_description": "PRODUCT_A",
           "product_group": "GROUP_1", "referral_source": "Source A", "patient_state": "ST", "diag_code_1": ""}
    return quality.problems({**row, **change})


def test_patient_column_never_loaded(tmp_path):
    df, messages = quality.load(make([ref(patient="PATIENT_SECRET")], tmp_path / "r.xlsx"))
    assert "patient_name" not in df.columns and "PATIENT_SECRET" not in df.to_string()
    assert any("patient_name" in m for m in messages) and not any("PATIENT_SECRET" in m for m in messages)


def test_each_problem_counted():
    assert problems() == []
    assert problems(diag_code_1="") == []                      # blank diagnosis is allowed
    assert problems(referral_source="") == ["No referral source"]
    assert problems(hcpcs_code="99213") == ["HCPCS code blank or invalid"]
    assert problems(answer_vendor="") == ["No vendor recorded"]
    assert problems(product_group="") == ["No service type"]
    assert problems(diag_code_1="ABC") == ["Diagnosis code not valid"]


def test_privacy_blanked_values_are_not_counted_as_missing(tmp_path):
    df, _ = quality.load(make([ref(product="Brace model 12345")], tmp_path / "r.xlsx"))
    assert df.loc[0, "product_description"] == ""
    result = quality.report(df)
    assert result["with_problem"] == 0 and result["privacy_blanked"] == 1


def test_report_groups_by_service_type_and_combines_small_groups(tmp_path):
    rows = [ref(group="BIG")] * 15 + [ref(group="BIG", source="")] * 5 \
        + [ref(group="SMALL_A")] * 3 + [ref(group="SMALL_B", vendor="")] * 2 + [ref(group="")]
    result = quality.report(quality.load(make(rows, tmp_path / "r.xlsx"))[0])
    assert result["referrals"] == 26 and result["with_problem"] == 8
    names = [g["service_type"] for g in result["by_service_type"]]
    assert names == [quality.NO_TYPE, "BIG", "Other service types (2 combined)"]
    assert "SMALL_A" not in str(result)


def test_printed_report_has_totals_only(tmp_path, capsys):
    rows = [ref(group="BIG")] * 25
    quality_report.main(["--input", str(make(rows, tmp_path / "r.xlsx")), "--output", str(tmp_path / "q.json")])
    out = capsys.readouterr().out
    for forbidden in ("VENDOR_X", "PRODUCT_A", "SRC_1", "E0000", "PATIENT"):
        assert forbidden not in out
