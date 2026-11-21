"""Intake quality report: missing or invalid details, by type of service. Totals only.

Usage: python scripts/quality_report.py [--input data/Referrals-v3.xlsx]
Saves output/quality.json (gitignored) for the app's Intake quality tab.
"""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from h1 import quality  # noqa: E402


def pct(part, whole):
    return f"{round(100 * part / whole)}%" if whole else "0%"


def render(r) -> str:
    lines = [f"Referrals checked: {r['referrals']}",
             f"With at least one missing or invalid detail: {r['with_problem']} ({pct(r['with_problem'], r['referrals'])}); "
             f"all {r['with_problem']} flagged before routing",
             f"Referrals with a value removed by the privacy filter (not counted as missing): {r['privacy_blanked']}",
             "", "By field:"]
    lines += [f"  {label}: {n}" for label, n in r["by_field"].items()]
    lines += ["", "By type of service (referrals with a problem):"]
    lines += [f"  {g['service_type']}: {g['with_problem']} of {g['referrals']} ({pct(g['with_problem'], g['referrals'])})"
              for g in r["by_service_type"]]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "Referrals-v3.xlsx")
    parser.add_argument("--output", type=Path, default=ROOT / "output" / "quality.json")
    args = parser.parse_args(argv)
    if not args.input.exists():
        parser.error(f"Input not found: {args.input}")
    df, messages = quality.load(args.input)
    for message in messages:
        print(message)
    result = quality.report(df)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
