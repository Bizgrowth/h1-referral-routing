import json

from h1 import importer, scoring
from scripts import totals

DECISIONS = [{"row_id": 1, "decision": "approve", "vendor": "Vendor 01", "seconds": s} for s in (30, 50, 40)]


def run(tmp_path, xlsx_path, capsys, decisions=DECISIONS, extra=()):
    scoring_file = tmp_path / "scoring.json"
    scoring_file.write_text(json.dumps(scoring.score(importer.load(xlsx_path).rows)))
    log = tmp_path / "decisions.jsonl"
    log.write_text("".join(json.dumps(d) + "\n" for d in decisions))
    totals.main(["--scoring", str(scoring_file), "--log", str(log), *extra])
    return capsys.readouterr().out


def test_prints_only_the_four_totals(tmp_path, xlsx_path, capsys):
    out = run(tmp_path, xlsx_path, capsys, extra=["--baseline-seconds", "180"])
    lines = out.strip().splitlines()
    numbered = [line for line in lines if not line.startswith("   ")]
    assert [line[:2] for line in numbered] == ["1.", "2.", "3.", "4."]
    assert lines[0].startswith("1. N: 5 referrals scored")
    assert "median 40 s per referral" in out and "180 s manual baseline" in out
    assert "3. Missing info caught: 1 of 6 referrals had a missing or invalid item; 1 of 1" in out
    # No rows, vendor names or examples.
    for forbidden in ("Vendor", "VENDOR", "PRODUCT_", "E000", "CITY_", "Source", "row_id"):
        assert forbidden not in out


def test_baseline_always_next_to_tool(tmp_path, xlsx_path, capsys):
    out = run(tmp_path, xlsx_path, capsys)
    match_lines = [line for line in out.splitlines() if "tool top-1" in line]
    assert match_lines and all("baseline top-1" in line for line in match_lines)
    assert "Multi-vendor products only" in out
    assert "manual baseline not entered" in out


def test_says_plainly_when_tool_does_not_beat_baseline():
    even = {"n": 4, "tool_top1": 3, "tool_top3": 4, "base_top1": 3, "base_top3": 4}
    scoring_data = {"train_years": [2024, 2025], "test_year": 2026,
                    "intake": {"n": 4, "with_issue": 0, "flagged": 0},
                    "overall": even, "by_group": {"GROUP_1": even}, "multi_vendor": even}
    out = totals.build(scoring_data, [], None)
    assert "the tool does NOT beat the baseline" in out
