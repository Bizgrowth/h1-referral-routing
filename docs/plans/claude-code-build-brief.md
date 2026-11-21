# Claude Code build brief: H1 Workers' Comp Referral Intake & Routing

Paste everything below the line into Claude Code on your own computer, in a new empty folder. Put your exported spreadsheet in that folder's `data/` subfolder only after step 1 is done. Never paste referral rows into any chat.

---

## What you're building

A local-only MVP for workers' comp DME and supply referral intake. For each referral row it:

1. Reads one de-identified referral (one row of a CSV or Excel export).
2. Extracts and normalizes the allowed fields.
3. Flags missing or invalid required information.
4. Suggests up to 3 vendors, ranked, with the reason for each (product, HCPCS code, diagnosis codes when present, carrier city, referral source).
5. Shows a coordinator approval screen: Approve, Change vendor, or Reject. Nothing is assigned without a person, and every decision is logged with the time spent.
6. Outputs only four totals for the portfolio. Never row-level data.

This is the build behind an Upwork portfolio item. The repo will be public on GitHub as proof of work, so it must never contain any referral data.

## Hard rules (non-negotiable)

1. **Local only.** No data goes to any outside service: no cloud AI API, no telemetry, no analytics, no hosted database. Everything runs on this machine. If you use Streamlit, set `gatherUsageStats = false` in `.streamlit/config.toml`. Add a test that fails if the code imports an HTTP client or calls an AI API on the data path.
2. **Allowlist import.** The input file is `data/Referrals.xlsx` (Sheet1; a tab-separated text export with the same headers must also work). The importer loads only these 11 columns, using the exact header names below, and drops everything else before any other code sees the file:

| Exact header | How it's used | Handling |
|---|---|---|
| insurance_company_city | Routing feature | Keep (carrier location, not patient). Optional; blank on some rows |
| referral_source | Routing feature | Keep; map to "Source A", "Source B", … if names identify a person |
| Expr1002 | Product name | An Access query alias. In the current export it is identical to product_description on every row. Rename it to `product_name`; if it matches product_description on all rows, drop it and print one line saying so |
| product_group | Routing feature | Keep |
| quantity | Validity check | Keep |
| vendor_name | Answer key only | Map to "Vendor 01", "Vendor 02", … at import; never an input feature. Rows with a blank vendor_name are excluded from scoring (no answer key) but still go through intake |
| hcpcs_code | Routing feature | Keep; validate format (letter + 4 digits) |
| DATE | Year | Already year only in the export; reject any value that isn't a 4-digit year |
| diag_code_2 | Optional feature | ICD-9 codes. Blank on most rows, so never required. Validate ICD-9 format only when present |
| diag_code_4 | Optional feature | Same as diag_code_2 |
| product_description | Routing feature | Keep; strip anything that looks like a name, phone, email or number longer than 6 digits |

3. **Refuse or strip identifiers.** If the file contains any column for patient name, patient city, adjuster name, order number, SSN or ZIP (or obvious variants: first/last name, address, phone, email, DOB, claim number, member ID), drop it at import and print a warning listing only the column names, never their values. If any kept text field matches an SSN, phone, email or ZIP pattern, blank that value and count it. Add tests for each.
4. **No data in the repo.** `.gitignore` must exclude `data/`, `output/`, `logs/`, `*.csv`, `*.xlsx`, `*.accdb`, `*.mdb` and `*.db`. Add a pre-commit check that blocks any of these files.
5. **Test fixtures are abstract.** Unit tests use tiny made-up values like `PRODUCT_A`, `E0000`, `Vendor 01`. They are code fixtures only, never shown as referrals, and never used for results.
6. **Fair scoring.** Split the data by year: build vendor suggestions from 2024 and 2025, and score on 2026 only. Never score on rows the suggester learned from. The current export has 74 rows, so the test year is small: always report counts ("17 of 20"), not percentages alone.
7. **Honest match score.** In this data the vendor is mostly set by the product: most products have only one vendor, and one product group carries most of the vendor choice. A high match rate can therefore come from the product alone. totals.py must report:
   - Match agreement for the tool, next to a simple baseline: "most common vendor for this product in the training years"
   - The same two numbers broken out per product_group, with the row count for each
   - Match agreement only on rows where the product had more than one vendor in training (the real routing decisions), next to the baseline
   - If the tool doesn't beat the baseline, it says so plainly

## How suggestions work (no outside AI)

- Build a local lookup from the training years: for each combination of hcpcs_code, product_group, diagnosis codes, referral_source and insurance_company_city, count which vendor was used. Start from product (product_description), since that settles the vendor for most products; the other fields only break ties where a product has several vendors.
- Rank vendors by that history, backing off to fewer fields when a combination is rare (HCPCS + product group, then product group alone).
- Show the reason in plain words, e.g. "Used for this HCPCS code in this city 84 times".
- Optional: a free-text field reader using a model running on this machine (e.g. Ollama). It's off by default, and data must never leave localhost.

## Missing information check

Required fields: referral_source, product_description, product_group, hcpcs_code, quantity, insurance_company_city. Flag blank, malformed or out-of-range values (quantity of 0 or less, a bad HCPCS format). Diagnosis codes are optional: flag only a malformed ICD-9 code when one is present, never a blank one.

Spotting a blank field is a fixed rule, not AI, so report this measure as a plain count ("X of N referrals had a missing or invalid item; all X were flagged before routing"), not as an accuracy score.

## Coordinator screen

A local web page (Streamlit is fine) that shows one referral at a time: the fields, the missing-info flags, and the top 3 vendors with reasons. It has Approve, Change vendor and Reject buttons. Log the decision, the chosen vendor ID, and the seconds from screen open to decision into `logs/` (gitignored). Put a visible label on the page: "Local only · de-identified data".

## The four totals (the only output that leaves the machine)

`python scripts/totals.py` reads the logs and the scoring run and prints exactly:

1. **N:** referrals scored
2. **Review time:** median seconds per referral with the tool, next to the manual baseline you enter (`--baseline-seconds`, from timing 10 referrals done by hand)
3. **Missing info caught:** referrals with a missing or invalid item, and how many of those were flagged, as counts
4. **Match agreement:** top-1 and top-3 matches against vendor_name (the answer key), next to the "most common vendor for this product" baseline, overall, per product_group, and on multi-vendor products only (see hard rule 7)

Print nothing else: no rows, no vendor names, no examples.

## Tests (pytest)

- Importer drops every non-allowlisted column, including all forbidden ones
- Pattern scrub blanks SSN, phone, email and ZIP values in kept text
- DATE becomes year only
- vendor_name is never an input feature
- Train/test split by year has no overlap (train 2024 to 2025, test 2026)
- Expr1002 is renamed to product_name, or dropped when it duplicates product_description
- Blank diagnosis codes never raise a missing-info flag
- Rows with a blank vendor_name are excluded from match scoring
- totals.py always prints the baseline next to the tool's match rate
- Missing-info rules flag each bad case
- totals.py output contains only the four totals
- No network or AI API calls on the data path
- .gitignore and the pre-commit check block data files

## README (written for Upwork buyers, not developers)

1. One-line pitch: "AI-assisted referral intake and vendor routing for workers' comp, with a coordinator approving every match."
2. The problem: referrals pile up, details go missing, vendors get picked from memory.
3. How it works: the 6 steps above, with `docs/04-workflow.png`.
4. Safeguards: local only, allowlisted de-identified fields, human approval, decision log.
5. Results: "Tested on N de-identified referrals from my own company's records," followed by the four totals. Leave this as a placeholder until the numbers are measured. Never estimate.
6. What a client gets: setup on their own data and rules, the approval screen, and a measurement report.
7. No contact details, email, phone or booking links anywhere in the repo.
8. Cover image `docs/01-cover.png` at the top.

## Assets to drop into docs/

- `01-cover.png` and `04-workflow.png` (from the H1 portfolio folder)
- Update both images and any wording from "clinic" to "vendor" if you change them

## Done means

- `pytest` passes
- Running the app on a fresh export shows the coordinator screen end to end
- `scripts/totals.py` prints only the four totals
- A fresh clone of the GitHub repo contains no data, logs or exports

---

## Reference: what was already made for the portfolio (in this folder)

- **item.md:** Upwork title, role, description and skills. Currently "Solution design"; it becomes "MVP tested on N de-identified referrals" once the four totals exist, and "clinic" becomes "vendor".
- **readiness.md:** blocking rules (no referral content in any asset, no estimated numbers, no contact details).
- **case-study.md:** 2-page case study with a results section waiting for the four totals.
- **intake-fields.md** and **private-test-steps.md:** de-identification rules and steps.
- **assets/01-cover.png** and **assets/04-workflow.png:** cover and workflow images.
- After the build, send back only N and the four totals. The title, description, case study and a results image get updated from those.
