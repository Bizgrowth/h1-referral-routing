import pandas as pd

from h1 import quality
from scripts import quality_report


def make(rows, path):
    pd.DataFrame(rows).to_excel(path, sheet_name="Sheet1", index=False)
    return path


def ref(group="GROUP_1", source="SRC_1", hcpcs="E0000", vendor="VENDOR_X", state="ST", diag="", product="PRODUCT_A",
        patient="17"):
    return {"hcpcs_code": hcpcs, "vendor_name": vendor, "patient_name": patient, "product_description": product,
            "product_group": group, "referral_source": source, "patient_state": state, "diag_code_1": diag}


def test_patient_column_never_loaded(tmp_path):
    df, messages = quality.load(make([ref(patient="PATIENT_SECRET")], tmp_path / "r.xlsx"))
    assert "patient_name" not in df.columns and "PATIENT_SECRET" not in df.to_string()
    assert any("patient_name" in m for m in messages) and not any("PATIENT_SECRET" in m for m in messages)


def test_each_problem_counted():
    assert quality.problems(ref()) == []
    assert quality.problems(ref(diag="")) == []                      # blank diagnosis is allowed
    assert quality.problems(ref(source="")) == ["No referral source"]
    assert quality.problems(ref(hcpcs="99213")) == ["HCPCS code blank or invalid"]
    assert quality.problems(ref(vendor="")) == ["No vendor assigned"]
    assert quality.problems(ref(group="")) == ["No service type"]
    assert quality.problems(ref(diag="ABC")) == ["Diagnosis code not valid"]


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
    for forbidden in ("VENDOR_X", "PRODUCT_A", "SRC_1", "E0000", "17"):
        assert forbidden not in out
