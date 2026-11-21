"""Missing-information check. Fixed rules, not AI."""

import re

REQUIRED = ["referral_source", "product_description", "product_group", "hcpcs_code", "quantity",
            "insurance_company_city"]
HCPCS = re.compile(r"[A-Z]\d{4}")
ICD9 = re.compile(r"\d{3}(?:\.?\d{1,2})?|V\d{2}(?:\.?\d{1,2})?|E\d{3}(?:\.?\d)?")


def find_issues(row) -> list:
    """Return plain-language flags for one referral (a dict or pandas row)."""
    issues = [f"Missing {field}" for field in REQUIRED if not str(row.get(field, "")).strip()]
    hcpcs = str(row.get("hcpcs_code", "")).strip()
    if hcpcs and not HCPCS.fullmatch(hcpcs):
        issues.append("Invalid hcpcs_code (expected a letter and 4 digits)")
    quantity = str(row.get("quantity", "")).strip()
    if quantity:
        try:
            if float(quantity) <= 0:
                issues.append("Invalid quantity (must be more than 0)")
        except ValueError:
            issues.append("Invalid quantity (not a number)")
    for field in ("diag_code_2", "diag_code_4"):
        code = str(row.get(field, "")).strip()
        if code and not ICD9.fullmatch(code):  # blank diagnosis codes are never flagged
            issues.append(f"Invalid {field} (not an ICD-9 code)")
    return issues
