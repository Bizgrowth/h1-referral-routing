import pytest

from h1 import importer, scrub
from tests.conftest import FORBIDDEN_COLUMNS, row, sample_rows, write_tsv, write_xlsx

EXPECTED_COLUMNS = {"row_id", "year", "hcpcs_code", "product_description", "product_group", "referral_source",
                    "patient_state", "diag_code_1", "answer_vendor", "_privacy"}


def test_drops_every_non_allowlisted_column(xlsx_path):
    result = importer.load(xlsx_path)
    assert set(result.rows.columns) == EXPECTED_COLUMNS
    assert sorted(result.forbidden_columns) == sorted(FORBIDDEN_COLUMNS)
    text = result.rows.to_string()
    assert not any(secret in text for secret in [*FORBIDDEN_COLUMNS.values(), "NOTE_SECRET"])


def test_patient_state_is_kept_but_patient_name_is_not(xlsx_path):
    result = importer.load(xlsx_path)
    assert "patient_state" in result.rows.columns and "patient_name" in result.forbidden_columns


def test_warning_lists_column_names_never_values(xlsx_path):
    messages = "\n".join(importer.load(xlsx_path).messages)
    assert all(name in messages for name in FORBIDDEN_COLUMNS)
    assert not any(secret in messages for secret in [*FORBIDDEN_COLUMNS.values(), "NOTE_SECRET"])


def test_tab_separated_export_works(tmp_path):
    xlsx = importer.load(write_xlsx(sample_rows(), tmp_path / "a.xlsx")).rows
    tsv = importer.load(write_tsv(sample_rows(), tmp_path / "Referrals-v4.txt")).rows
    assert xlsx.astype(str).equals(tsv.astype(str))


@pytest.mark.parametrize("text", ["call 555-123-4567", "SSN 123-45-6789", "a.b@example.com", "area 32250",
                                  "(904) 555 1234"])
def test_pattern_scrub_blanks_and_records(tmp_path, text):
    rows = [row(2025, "PRODUCT_A", "GROUP_1", "E0000", "VENDOR_X", source=text)]
    result = importer.load(write_xlsx(rows, tmp_path / "r.xlsx"))
    assert result.rows.loc[0, "referral_source"] == ""
    assert result.rows.loc[0, "_privacy"] == "referral_source,"
    assert result.scrubbed_values == 1


def test_product_description_strips_identifiers():
    cleaned = scrub.strip_description("PRODUCT_A for Dr. Smith patient: Jones call 5551234567 x@y.com 12345678")
    assert cleaned == "PRODUCT_A for call"


def test_referral_date_must_be_year_only(tmp_path):
    rows = [row(year, "PRODUCT_A", "GROUP_1", "E0000", "VENDOR_X") for year in (2025, "2026", "2025-05-01", "25")]
    result = importer.load(write_xlsx(rows, tmp_path / "r.xlsx"))
    assert result.rows["year"].tolist() == [2025, 2026]
    assert result.rejected_dates == 2


def test_vendor_and_source_are_mapped(xlsx_path):
    rows = importer.load(xlsx_path).rows
    assert set(rows["answer_vendor"]) == {"Vendor 01", "Vendor 02", "Vendor 03", ""}
    assert set(rows["referral_source"]) == {"Source A"}
