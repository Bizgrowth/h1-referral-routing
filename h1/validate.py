"""Missing-information check. Fixed rules, not AI. The same rules drive the review queue and the
intake quality report."""

import re

CHECKS = [  # (field, plain-language problem)
    ("referral_source", "No referral source"),
    ("product_description", "No product"),
    ("product_group", "No service type"),
    ("hcpcs_code", "HCPCS code blank or invalid"),
    ("patient_state", "No state"),
    ("diag_code_1", "Diagnosis code not valid"),  # blank is allowed; only a malformed code counts
]
HCPCS = re.compile(r"[A-Z]\d{4}")
ICD9 = re.compile(r"\d{3}(?:\.?\d{1,2})?|V\d{2}(?:\.?\d{1,2})?|E\d{3}(?:\.?\d)?")


def issues_by_field(row) -> dict:
    """{field: problem} for one referral (a dict or pandas row)."""
    privacy = str(row.get("_privacy", "")).split(",")
    found = {}
    for field, label in CHECKS:
        if field in privacy:  # blanked by our privacy filter, not missing at intake
            continue
        value = str(row.get(field, "")).strip().upper()
        if field == "hcpcs_code":
            bad = not HCPCS.fullmatch(value)
        elif field == "diag_code_1":
            bad = bool(value) and not ICD9.fullmatch(value)
        else:
            bad = not value
        if bad:
            found[field] = label
    return found


def find_issues(row) -> list:
    return list(issues_by_field(row).values())
