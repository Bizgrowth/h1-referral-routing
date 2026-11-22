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
.venv\Scripts\python scripts\score.py            # reads data\Referrals.xlsx -> output\scoring.json
.venv\Scripts\streamlit run app.py               # coordinator screen at http://localhost:8501
.venv\Scripts\python scripts\totals.py --baseline-seconds <manual median>
```

## Current Status
MVP built 2026-11-21; 60 tests pass; checked end to end on synthetic fixtures only.
Real export loaded 2026-11-21 (74 rows, `data/Referrals.xlsx`, gitignored). Manual baseline: **165 s** per referral
(2.75 min, given by Daniel). Review time with the tool: not yet logged. Run totals with `--baseline-seconds 165`.
Public totals need the data owner's written OK before pushing.
Full export (2,836 rows, 8 columns, no year) at `data/Referrals-v3.xlsx`: run `scripts\quality_report.py` for the
intake-quality totals by type of service (app tab "Intake quality"). `Referrals-v2-filtered.xlsx` is a filtered subset; unused.
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
