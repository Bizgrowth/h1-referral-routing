# H1 Referral Routing
**Owner:** Daniel Schley
**Client:** Internal (Upwork portfolio piece)
**Started:** 2026-11-20
**Stack:** Python, Streamlit (coordinator screen), pytest. Local only.

---

## What This Is
A local-only MVP that takes de-identified workers' comp DME and supply referrals, flags missing information, suggests up to 3 vendors with reasons, and has a coordinator approve every match.

## How to Run
```
python -m venv .venv && .venv\Scripts\python -m pip install -r requirements.txt
git config core.hooksPath .githooks              # once per clone: blocks data files from commits
.venv\Scripts\python -m pytest                   # all tests
.venv\Scripts\python scripts\quality_report.py   # intake totals by type of service -> output\quality.json
.venv\Scripts\streamlit run app.py               # coordinator screen at http://localhost:8501
.venv\Scripts\python scripts\totals.py --baseline-seconds <manual median>
```

## Current Status
2026-11-21: the app runs on ONE sheet, `data/Referrals-v4.xlsx` (2,836 referrals, 2025: 1,860, 2026: 976; gitignored).
Allowlist = the 8 v4 columns; `patient_name` is never loaded. 69 tests pass. Public totals approved by Daniel.
Published results: intake quality by type of service (1,091 of 2,836 = 38% flagged; by-field counts as the supporting line).
Vendor accuracy is NOT published: in v4 the year follows row order, every HCPCS code appears exactly twice (once per year)
and 427 2026 rows copy a 2025 row, so a 2025->2026 test is not fair. `scripts\score.py`/`totals.py` still work for a
client export with real referral dates. Manual baseline **165 s** (2.75 min); time with the tool not yet logged.
Older sheets (`Referrals.xlsx`, `Referrals-v2-filtered.xlsx`, `Referrals-v3.xlsx`) are no longer used.
Plan and assumptions: `docs/plans/2026-11-20-h1-build-plan.md`. Spec: `docs/plans/claude-code-build-brief.md`.
Portfolio images: `docs/01-cover.png`, `docs/04-workflow.png` (sources in `docs/images-src/`; re-render with headless Edge at 1600x1200).

## Key Docs
- `docs/plans/claude-code-build-brief.md`: the build spec, with hard rules, tests and "done means"
- `docs/plans/intake-fields.md`: de-identification rules for each field
- `docs/plans/private-test-steps.md`: how to run it on real data privately
- `docs/case-study.md`: portfolio case study, with results waiting for the four totals

## Rules
- Never commit .env or credentials
- Read CLAUDE.md before every session
- This repo will be public. Never commit referral data, exports, logs or output (`data/`, `output/`, `logs/`, `*.csv`, `*.xlsx`, `*.accdb`, `*.mdb`, `*.db`)
- No data leaves this machine: no cloud AI API, no telemetry, no hosted database
- No contact details, email, phone or booking links anywhere in the repo
- Never estimate results; only report measured totals
