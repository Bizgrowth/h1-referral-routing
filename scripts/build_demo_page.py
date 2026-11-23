"""Build docs/index.html: a static, no-server demo page from the scrubbed Referrals-v4 queue.

Run: .venv\Scripts\python scripts\build_demo_page.py
Embeds the 2026 review queue (scrubbed, masked labels, no answer key) with precomputed flags and
vendor suggestions, plus totals. Training rows (2025) are not embedded.
"""

import json
from pathlib import Path
import sys
from statistics import median

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from h1 import importer, quality, scoring  # noqa: E402
from h1.suggest import Baseline, Suggester  # noqa: E402
from h1.validate import issues_by_field  # noqa: E402

KEEP = ["row_id", "year", "product_description", "product_group", "hcpcs_code", "diag_code_1",
        "patient_state", "referral_source"]


def main():
    result = importer.load(importer.default_input(ROOT / "data"))
    rows = result.rows
    train, test = scoring.split(rows)
    suggester, baseline = Suggester.fit(train), Baseline(train)

    queue = []
    for row in test.to_dict("records"):
        item = {k: (int(row[k]) if k in ("row_id", "year") else str(row[k] or "")) for k in KEEP}
        item["flags"] = issues_by_field(row)
        item["privacy"] = str(row.get("_privacy", ""))
        item["suggestions"] = [{"vendor": s.vendor, "reason": s.reason, "count": s.count}
                               for s in suggester.suggest(row)]
        queue.append(item)

    scored = scoring.score(rows)
    seen = new = 0
    seen_tool = new_tool = seen_base = new_base = 0
    for row in test.to_dict("records"):
        answer = row["answer_vendor"]
        if not answer:
            continue
        tool = [s.vendor for s in suggester.suggest(row)][:1] == [answer]
        base = baseline.predict(row)[:1] == [answer]
        if baseline.vendor_count(row["product_description"]) > 0:
            seen, seen_tool, seen_base = seen + 1, seen_tool + tool, seen_base + base
        else:
            new, new_tool, new_base = new + 1, new_tool + tool, new_base + base

    log = ROOT / "logs" / "decisions.jsonl"
    decisions = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines() if x.strip()] if log.exists() else []
    seconds = [d["seconds"] for d in decisions]
    measured = {"n": len(seconds), "median": round(median(seconds)) if seconds else None, "manual": 165,
                "approve": sum(d["decision"] == "approve" for d in decisions),
                "change": sum(d["decision"] == "change" for d in decisions),
                "reject": sum(d["decision"] == "reject" for d in decisions)}

    data = {"quality": quality.report(rows), "queue": queue,
            "vendors": sorted(v for v in rows["answer_vendor"].unique() if v), "measured": measured,
            "match": {"overall": scored["overall"], "multi": scored["multi_vendor"],
                      "seen": {"n": seen, "tool": seen_tool, "base": seen_base},
                      "new": {"n": new, "tool": new_tool, "base": new_base}}}
    template = (ROOT / "scripts" / "demo_page_template.html").read_text(encoding="utf-8")
    page = template.replace("/*DATA*/null", json.dumps(data, separators=(",", ":")).replace("</", "<\/"))
    (ROOT / "docs" / "index.html").write_text(page, encoding="utf-8")
    print(f"docs/index.html written: {len(queue)} queue rows, {len(page) // 1024} KB")


if __name__ == "__main__":
    main()
