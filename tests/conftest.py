"""Abstract code fixtures only (PRODUCT_A, E0000, VENDOR_X). Never real referrals; never used for results.

Files are written to pytest's temp folder, never into the repo.
"""

import pandas as pd
import pytest

FORBIDDEN_COLUMNS = {"patient_name": "PATIENT_SECRET", "patient_city": "PCITY_SECRET",
                     "adjuster_name": "ADJ_SECRET", "order_number": "ORDER_SECRET", "SSN": "SSN_SECRET",
                     "zip": "ZIP_SECRET", "DOB": "DOB_SECRET", "claim_number": "CLAIM_SECRET"}


def row(year, product, group, hcpcs, vendor, city="CITY_A", source="SRC_1", qty="1", d2="", d4=""):
    base = {"insurance_company_city": city, "referral_source": source, "Expr1002": product,
            "product_group": group, "quantity": qty, "vendor_name": vendor, "hcpcs_code": hcpcs,
            "DATE": year, "diag_code_2": d2, "diag_code_4": d4, "product_description": product,
            "notes": "NOTE_SECRET"}
    return {**base, **FORBIDDEN_COLUMNS}


def sample_rows():
    train = (
        [row(2024, "PRODUCT_A", "GROUP_1", "E0000", "VENDOR_X")] * 2
        + [row(2025, "PRODUCT_A", "GROUP_1", "E0000", "VENDOR_X")] * 2
        + [row(2024, "PRODUCT_B", "GROUP_2", "E0001", "VENDOR_Y", city="CITY_A")] * 3
        + [row(2025, "PRODUCT_B", "GROUP_2", "E0001", "VENDOR_Z", city="CITY_B")] * 2
    )
    test = [
        row(2026, "PRODUCT_A", "GROUP_1", "E0000", "VENDOR_X"),
        row(2026, "PRODUCT_B", "GROUP_2", "E0001", "VENDOR_Z", city="CITY_B"),
        row(2026, "PRODUCT_B", "GROUP_2", "E0001", "VENDOR_Y", city="CITY_A"),
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
    return write_xlsx(sample_rows(), tmp_path / "Referrals.xlsx")
