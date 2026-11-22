"""Abstract code fixtures only (PRODUCT_A, E0000, VENDOR_X). Never real referrals; never used for results.

Rows use the same columns as data/Referrals-v4.xlsx. Files are written to pytest's temp folder, never into the repo.
"""

import pandas as pd
import pytest

FORBIDDEN_COLUMNS = {"patient_name": "PATIENT_SECRET", "patient_city": "PCITY_SECRET",
                     "adjuster_name": "ADJ_SECRET", "order_number": "ORDER_SECRET", "SSN": "SSN_SECRET",
                     "zip": "ZIP_SECRET", "DOB": "DOB_SECRET", "claim_number": "CLAIM_SECRET"}


def row(year, product, group, hcpcs, vendor, state="ST_A", source="SRC_1", diag=""):
    base = {"hcpcs_code": hcpcs, "vendor_name": vendor, "product_description": product, "product_group": group,
            "referral_source": source, "patient_state": state, "diag_code_1": diag, "date of referral": year,
            "notes": "NOTE_SECRET"}
    return {**base, **FORBIDDEN_COLUMNS}


def sample_rows():
    train = (
        [row(2025, "PRODUCT_A", "GROUP_1", "E0000", "VENDOR_X")] * 4
        + [row(2025, "PRODUCT_B", "GROUP_2", "E0001", "VENDOR_Y", state="ST_A")] * 3
        + [row(2025, "PRODUCT_B", "GROUP_2", "E0001", "VENDOR_Z", state="ST_B")] * 2
    )
    test = [
        row(2026, "PRODUCT_A", "GROUP_1", "E0000", "VENDOR_X"),
        row(2026, "PRODUCT_B", "GROUP_2", "E0001", "VENDOR_Z", state="ST_B"),
        row(2026, "PRODUCT_B", "GROUP_2", "E0001", "VENDOR_Y", state="ST_A"),
        row(2026, "PRODUCT_C", "GROUP_1", "E0000", "VENDOR_X"),          # product never seen in training
        row(2026, "PRODUCT_A", "GROUP_1", "E0000", ""),                  # no answer key
        row(2026, "PRODUCT_A", "GROUP_1", "X12", "VENDOR_X"),            # bad HCPCS
    ]
    return train + test


def write_xlsx(rows, path):
    pd.DataFrame(rows).to_excel(path, sheet_name="Sheet1", index=False)
    return path


def write_tsv(rows, path):
    pd.DataFrame(rows).to_csv(path, sep="\t", index=False)
    return path


@pytest.fixture
def xlsx_path(tmp_path):
    return write_xlsx(sample_rows(), tmp_path / "Referrals-v4.xlsx")
