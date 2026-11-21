"""Fair scoring: learn from 2024-2025, score on 2026 only. Aggregate counts only."""

from collections import defaultdict

from h1.suggest import Baseline, Suggester
from h1.validate import find_issues

TRAIN_YEARS = (2024, 2025)
TEST_YEAR = 2026


def split(rows):
    return rows[rows["year"].isin(TRAIN_YEARS)], rows[rows["year"] == TEST_YEAR]


def route(row, suggester) -> dict:
    """The intake pipeline for one referral: flag missing info first, then suggest vendors."""
    return {"flags": find_issues(row), "suggestions": suggester.suggest(row)}


def _blank():
    return {"n": 0, "tool_top1": 0, "tool_top3": 0, "base_top1": 0, "base_top3": 0}


def _add(bucket, answer, tool, base):
    bucket["n"] += 1
    bucket["tool_top1"] += int(tool[:1] == [answer])
    bucket["tool_top3"] += int(answer in tool[:3])
    bucket["base_top1"] += int(base[:1] == [answer])
    bucket["base_top3"] += int(answer in base[:3])


def score(rows) -> dict:
    train, test = split(rows)
    suggester, baseline = Suggester.fit(train), Baseline(train)
    intake = {"n": 0, "with_issue": 0, "flagged": 0}
    overall, multi, groups = _blank(), _blank(), defaultdict(_blank)
    for row in test.to_dict("records"):
        result = route(row, suggester)  # every referral goes through intake
        intake["n"] += 1
        intake["with_issue"] += int(bool(find_issues(row)))
        intake["flagged"] += int(bool(result["flags"]))
        answer = row["answer_vendor"]
        if not answer:  # no answer key: excluded from match scoring
            continue
        tool = [s.vendor for s in result["suggestions"]]
        base = baseline.predict(row)
        _add(overall, answer, tool, base)
        _add(groups[row["product_group"] or "(blank)"], answer, tool, base)
        if baseline.vendor_count(row["product_description"]) > 1:
            _add(multi, answer, tool, base)
    return {"train_years": list(TRAIN_YEARS), "test_year": TEST_YEAR, "intake": intake,
            "overall": overall, "by_group": dict(sorted(groups.items())), "multi_vendor": multi}
