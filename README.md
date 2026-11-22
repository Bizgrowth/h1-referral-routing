![Cover](docs/01-cover.png)

# H1 Referral Routing

**Referral intake checks and vendor routing for workers' comp, with a coordinator approving every match.**

## The problem
Durable medical equipment and supply referrals pile up. Required details go missing and stall cases, and coordinators pick vendors from memory or spreadsheets. Each delay pushes back care for the injured worker.

## How it works
![Workflow](docs/04-workflow.png)
1. Reads the referral export the team already keeps, one spreadsheet.
2. Keeps only 8 approved columns and drops everything else, including the patient column.
3. Checks every referral against fixed intake rules: referral source, product, service type, HCPCS code, state and diagnosis code format.
4. Groups the problems by type of service, so the team sees where intake breaks down first.
5. Suggests up to 3 vendors for each new referral, ranked from the company's own past referrals, each with a plain-language reason.
6. Shows a coordinator screen: **Approve**, **Change vendor** or **Reject**. Nothing is assigned without a person, and every decision is logged with the time it took.

## Safeguards
- **Local only.** Runs entirely on the client's own computer. No cloud AI, no tracking, no hosted database.
- **Allowlisted, de-identified fields.** The patient column is never loaded. Values that look like an SSN, phone number, email or ZIP code are blanked, and vendor and source names are replaced with labels such as "Vendor 01".
- **Human approval** on every referral, with a decision log.
- **Honest measurement.** Totals only, never estimated. A number is published only when the data can support it.

## Results
Tested on 2,836 de-identified referrals from my own company's records (2025–2026). Totals only.
- **Intake quality:** 1,091 of 2,836 referrals (38%) had a missing or invalid detail, and all were flagged before routing.
- **Where it breaks down, by type of service:** nursing 73%, respiratory 45%, DME 44%, IV therapy 43%, orthotics 34%, down to hearing aids at 8%.
- **What was missing:** no referral source on 770 referrals, no product on 126, no service type on 111, a blank or invalid HCPCS code on 108.
- **Vendor shortlist:** learned from 2025, tested on 970 referrals from 2026. The top suggestion matched the vendor actually used for 940 (97%), vs 754 (78%) for "use the most common vendor for this product". The gain comes from new products, where the simple rule has no history.
- **Review time per referral:** 2.75 minutes by hand today; time with the tool is being measured.

## What a client gets
- Setup on the client's own export and intake rules
- The intake quality report by type of service
- The coordinator approval screen with vendor suggestions

## Built With
Python, pandas, Streamlit, pytest.

---
Built by Daniel Schley
