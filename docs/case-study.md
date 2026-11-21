# Case study v2: Workers' Comp Referral Intake & Routing (2 pages)

**Headline:** Referral in, right clinic out: AI intake with coordinator approval
**Status badge:** SOLUTION DESIGN (no results claimed)

## The problem
Referrals arrive in mixed formats. Coordinators retype fields, chase missing details, and choose clinics from memory or spreadsheets. Each delay pushes back the injured worker's first visit.

## The design
- Intake for PDF, fax image or email referrals
- AI extraction of claimant, injury, body part, date of injury, employer, adjuster and claim fields
- Missing-information check against a required-field list
- Rules-based clinic matching: approved network, specialty, distance
- Coordinator approval screen with an audit log
[Diagram: 04-workflow.png]

## Safeguards
A person approves every assignment; low-confidence fields marked "needs review", never guessed; referral data stays in the client's own systems; routing rules editable by operations.

## Results (fill only with the totals from private-test-steps.md; otherwise keep as what a pilot measures)
Label when filled: "Measured on N de-identified referrals from my own company's records. Totals only."
- Review time per referral, before vs after
- Missing information caught before the case stalls
- How often the top suggestion matches the coordinator's choice

## Relevant experience
[Option 2 only: Daniel's own words on real referral-intake work, client unnamed]

## Who it's for
Workers' comp managed care networks, TPAs, case management and occupational health intake teams.
