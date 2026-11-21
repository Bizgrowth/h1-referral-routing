# H1 Referral Routing
**Owner:** Daniel Schley
**Client:** Internal (Upwork portfolio piece)
**Started:** 2026-11-20
**Stack:** Python, Streamlit (coordinator screen), pytest. Local only.

---

## What This Is
A local-only MVP that takes de-identified workers' comp DME and supply referrals, flags missing information, suggests up to 3 vendors with reasons, and has a coordinator approve every match.

## How to Run
[placeholder — fill in after first build]

## Current Status
Planning — not started. The full spec is in `docs/plans/claude-code-build-brief.md`.

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
