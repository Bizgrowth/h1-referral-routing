"""Print the four portfolio totals. The only output meant to leave this machine.

Usage: python scripts/totals.py --baseline-seconds 180
Reads output/scoring.json (from scripts/score.py) and logs/decisions.jsonl (from the app).
"""

import argparse
import json
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent.parent


def _pair(hits, n):
    return f"{hits} of {n}"


def _match(label, b):
    n = b["n"]
    return (f"{label} (n={n}): tool top-1 {_pair(b['tool_top1'], n)}, top-3 {_pair(b['tool_top3'], n)} | "
            f"baseline top-1 {_pair(b['base_top1'], n)}, top-3 {_pair(b['base_top3'], n)}")


def _verdict(label, b):
    if b["n"] == 0:
        return f"{label}: no rows to compare."
    if b["tool_top1"] > b["base_top1"]:
        return f"{label}: the tool beats the baseline on top-1."
    return f"{label}: the tool does NOT beat the baseline on top-1."


def build(scoring, decisions, baseline_seconds):
    seconds = [d["seconds"] for d in decisions if isinstance(d.get("seconds"), (int, float))]
    manual = f"{baseline_seconds:g} s manual baseline" if baseline_seconds else "manual baseline not entered"
    review = (f"median {median(seconds):.0f} s per referral with the tool ({len(seconds)} decisions)"
              if seconds else "no decisions logged yet")
    intake, overall, multi = scoring["intake"], scoring["overall"], scoring["multi_vendor"]
    lines = [
        f"1. N: {overall['n']} referrals scored (trained on {scoring['train_years'][0]}-"
        f"{scoring['train_years'][-1]}, scored on {scoring['test_year']})",
        f"2. Review time: {review} vs {manual}",
        f"3. Missing info caught: {intake['with_issue']} of {intake['n']} referrals had a missing or invalid item; "
        f"{intake['flagged']} of {intake['with_issue']} were flagged before routing",
        "4. Match agreement against vendor_name (baseline = most common vendor for this product in training):",
        "   " + _match("Overall", overall),
    ]
    lines += ["   " + _match(f"product_group {group}", b) for group, b in scoring["by_group"].items()]
    lines += ["   " + _match("Multi-vendor products only", multi),
              "   " + _verdict("Overall", overall),
              "   " + _verdict("Multi-vendor products", multi)]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-seconds", type=float, help="Median seconds per referral done by hand")
    parser.add_argument("--scoring", type=Path, default=ROOT / "output" / "scoring.json")
    parser.add_argument("--log", type=Path, default=ROOT / "logs" / "decisions.jsonl")
    args = parser.parse_args(argv)
    if not args.scoring.exists():
        parser.error("Run python scripts/score.py first.")
    scoring = json.loads(args.scoring.read_text(encoding="utf-8"))
    decisions = []
    if args.log.exists():
        decisions = [json.loads(line) for line in args.log.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(build(scoring, decisions, args.baseline_seconds))


if __name__ == "__main__":
    main()
