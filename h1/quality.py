"""Intake quality report for the full referral export (no year column).

Checks every referral for missing or invalid details and counts the problems by
type of service (product_group) and by field. Output is totals only.
Same safeguards as the main importer: allowlisted columns only, identifier columns
(such as patient_name) are never loaded, and text matching an SSN/phone/email/ZIP is blanked.
"""

from collections import Counter
from pathlib import Path
import re

from h1 import importer, scrub
from h1.validate import HCPCS, ICD9

ALLOWED = ["hcpcs_code", "vendor_name", "product_description", "product_group", "referral_source",
           "patient_state", "diag_code_1"]
TEXT_FIELDS = ["product_description", "product_group", "referral_source", "patient_state"]
CHECKS = [  # (field, plain-language problem)
    ("referral_source", "No referral source"),
    ("product_description", "No product"),
    ("product_group", "No service type"),
    ("hcpcs_code", "HCPCS code blank or invalid"),
    ("vendor_name", "No vendor assigned"),
    ("patient_state", "No state"),
    ("diag_code_1", "Diagnosis code not valid"),  # blank is allowed; only a malformed code counts
]
MIN_GROUP = 20  # smaller service types are combined so no small group stands out
NO_TYPE = "No service type recorded"


def problems(row) -> list:
    found = []
    privacy = row.get("_privacy", "").split(",")
    for field, label in CHECKS:
        if field in privacy:  # blanked by our privacy filter, not missing at intake
            continue
        value = row.get(field, "")
        if field == "hcpcs_code":
            bad = not HCPCS.fullmatch(value.upper())
        elif field == "diag_code_1":
            bad = bool(value) and not ICD9.fullmatch(value.upper())
        else:
            bad = not value
        if bad:
            found.append(label)
    return found


def load(path) -> tuple:
    path = Path(path)
    headers = [str(h) for h in importer._read(path, header_only=True).columns]
    extra = [h for h in headers if h not in ALLOWED]
    messages = [f"Dropped column(s) not used by this report: {', '.join(extra)}"] if extra else []
    df = importer._read(path, header_only=False, allowed=ALLOWED)
    for col in ALLOWED:
        if col not in df.columns:
            df[col] = ""
    df = df[ALLOWED].map(importer._text)
    scrubbed = 0
    df["_privacy"] = ""
    df["product_description"] = df["product_description"].map(scrub.strip_description)
    for col in TEXT_FIELDS:
        hits = df[col].map(scrub.has_identifier)
        scrubbed += int(hits.sum())
        df.loc[hits, col] = ""
        df.loc[hits, "_privacy"] += col + ","
    if scrubbed:
        messages.append(f"Blanked {scrubbed} value(s) matching an SSN, phone, email or ZIP pattern "
                        "(not counted as missing).")
    return df, messages


def report(df) -> dict:
    by_field, groups = Counter(), {}
    with_problem = 0
    for row in df.to_dict("records"):
        found = problems(row)
        with_problem += bool(found)
        by_field.update(found)
        name = row["product_group"].strip() or NO_TYPE
        g = groups.setdefault(name, {"referrals": 0, "with_problem": 0, "fields": Counter()})
        g["referrals"] += 1
        g["with_problem"] += bool(found)
        g["fields"].update(found)
    shown, other = {}, {"referrals": 0, "with_problem": 0, "fields": Counter(), "types": 0}
    for name, g in groups.items():
        if g["referrals"] >= MIN_GROUP or name == NO_TYPE:
            shown[name] = g
        else:
            other["types"] += 1
            for key in ("referrals", "with_problem"):
                other[key] += g[key]
            other["fields"].update(g["fields"])
    rows = sorted(shown.items(), key=lambda kv: -kv[1]["with_problem"] / kv[1]["referrals"])
    if other["referrals"]:
        rows.append((f"Other service types ({other['types']} combined)", other))
    return {
        "referrals": len(df), "with_problem": with_problem,
        "privacy_blanked": int((df["_privacy"] != "").sum()) if "_privacy" in df else 0,
        "by_field": {label: by_field[label] for _, label in CHECKS},
        "by_service_type": [{"service_type": name, "referrals": g["referrals"], "with_problem": g["with_problem"],
                             "fields": {label: g["fields"][label] for _, label in CHECKS}} for name, g in rows],
    }
