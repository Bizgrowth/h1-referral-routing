<!-- Cover image goes here once added: ![Cover](docs/01-cover.png) -->

# H1 Referral Routing

**AI-assisted referral intake and vendor routing for workers' comp, with a coordinator approving every match.**

## The problem
Durable medical equipment and supply referrals pile up. Required details go missing and stall cases, and coordinators pick vendors from memory or spreadsheets. Each delay pushes back care for the injured worker.

## How it works
<!-- Workflow diagram goes here once added: ![Workflow](docs/04-workflow.png) -->
1. Reads one de-identified referral from a spreadsheet export.
2. Extracts and cleans only the allowed fields.
3. Flags missing or invalid required information before routing.
4. Suggests up to 3 vendors, ranked, each with a plain-language reason (product, HCPCS code, diagnosis codes, carrier city, referral source).
5. Shows a coordinator screen: **Approve**, **Change vendor** or **Reject**. Nothing is assigned without a person, and every decision is logged with the time it took.
6. Produces four summary totals for reporting, never individual records.

## Safeguards
- **Local only.** Runs entirely on the client's own computer. No cloud AI, no tracking, no hosted database.
- **Allowlisted, de-identified fields.** The importer keeps 11 approved columns and drops everything else, including any patient, adjuster, claim or contact columns. Values that look like an SSN, phone number, email or ZIP code are blanked.
- **Human approval** on every referral, with a decision log.
- **Honest measurement.** Suggestions are learned from earlier years and scored only on a later year, always next to a simple "most common vendor for this product" baseline.

## Results
*Placeholder: results will be added once measured. Nothing here is estimated.*

Tested on N de-identified referrals from my own company's records:
1. Referrals scored: —
2. Review time per referral, before vs with the tool: —
3. Missing information caught: —
4. Top-vendor match vs the coordinator's choice, next to the baseline: —

## What a client gets
- Setup on the client's own export and routing rules
- The coordinator approval screen
- A measurement report built from these four totals

## Built With
Python, pandas, Streamlit, pytest.

---
Built by Daniel Schley
