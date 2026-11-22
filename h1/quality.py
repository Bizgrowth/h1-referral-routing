"""Intake quality report: missing or invalid details, by type of service (product_group). Totals only.

Uses the same importer (allowlist, privacy filter) and the same rules as the review queue,
plus one record-keeping check: no vendor recorded.
"""

from collections import Counter

from h1 import importer
from h1.validate import CHECKS as INTAKE_CHECKS, find_issues

VENDOR = "No vendor recorded"
CHECKS = [*(label for _, label in INTAKE_CHECKS), VENDOR]
MIN_GROUP = 20  # smaller service types are combined so no small group stands out
NO_TYPE = "No service type recorded"


def problems(row) -> list:
    found = find_issues(row)
    if not str(row.get("answer_vendor", "")).strip():
        found.append(VENDOR)
    return found


def load(path) -> tuple:
    result = importer.load(path)
    return result.rows, result.messages


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
        "by_field": {label: by_field[label] for label in CHECKS},
        "by_service_type": [{"service_type": name, "referrals": g["referrals"], "with_problem": g["with_problem"],
                             "fields": {label: g["fields"][label] for label in CHECKS}} for name, g in rows],
    }
