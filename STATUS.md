# Status: H1 Referral Routing

**Updated:** 2026-11-24 | **Phase:** built and live; Upwork portfolio hand-back in progress | **Branch:** main (pushed, nothing open)

## Done so far
- Local app (Python + Streamlit) runs on the scrubbed v4 sheet: 2,836 referrals, 71 tests pass.
- Static demo page is live at https://referrals.aiopsexpert.com with HTTPS enforced (GitHub Pages, main /docs, `docs/CNAME`).
- Results are published as totals only: 38% of referrals flagged at intake, top vendor suggestion right for 940 of 970 (97%) vs 754 (78%) for the simple rule, review time median 6 s over 12 logged decisions (a measurement, never "time saved").

## Next task (one sentence)
Get the full referral export file path from Daniel (or the missing `claude-code-prompt-replay-v4.md`), then build the scrubbed AI-routing extract on his computer and stop before any commit or push.

## Waiting on Daniel
- The file path to the full referral export, and the file `claude-code-prompt-replay-v4.md` (it is not in this folder).
- Replace this project's old `CLAUDE.md` rules with the new SOP version (the replacement never landed).
- Record the walkthrough video; confirm the 5 Upwork skill names; decide when to publish `portfolio-handoff/`.
- Separate project: DNS record for `leasing.aiopsexpert.com` still missing at last check.

## Not in this repo (on purpose)
- `data/`, `logs/`, `output/` and the spreadsheets stay local and gitignored.
- `portfolio-handoff/` (Upwork text, case-study PDF, screens, QA report) is local and untracked. `links.txt` is not written yet.

## Next-chat starter (works from main)
"Read STATUS.md and CLAUDE.md in the H1 folder, then do the next task. Work only on this computer. Stop before any commit, push or upload."
