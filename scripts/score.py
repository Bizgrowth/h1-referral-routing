"""Run the scoring pass and save aggregate counts to output/scoring.json.

Usage: python scripts/score.py [--input data/Referrals.xlsx]
"""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from h1 import importer, scoring  # noqa: E402

DEFAULT_OUTPUT = ROOT / "output" / "scoring.json"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=importer.default_input(ROOT / "data"))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    if not args.input.exists():
        parser.error(f"Input not found: {args.input}")
    result = importer.load(args.input)
    for message in result.messages:  # column names and counts only
        print(message)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(scoring.score(result.rows), indent=2), encoding="utf-8")
    print(f"Saved aggregate scoring to {args.output}")


if __name__ == "__main__":
    main()
