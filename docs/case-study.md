# Case study: Workers' Comp Referral Intake & Vendor Routing

**Headline:** Missing details caught before routing, a vendor shortlist with reasons, and a coordinator approves every match
**Status:** MVP tested on 20 de-identified referrals from my own company's records

## The problem
Equipment and supply referrals arrive with gaps. Coordinators chase missing details after the case has already stalled, and pick vendors from memory or old spreadsheets. Each delay pushes back the injured worker's equipment.

## What I built
- **Intake:** reads a de-identified referral export and keeps only 11 approved fields. Everything else is dropped before any other step sees the file.
- **Missing-information rules:** every referral is checked against a required-field list (referral source, product, product group, HCPCS code, quantity, carrier city) and format rules before it can be routed.
- **Vendor shortlist:** up to 3 vendors, ranked from the company's own past referrals, each with a plain-language reason such as "Used for this product in this carrier city 4 times".
- **Coordinator approval screen:** Approve, Change vendor or Reject. Nothing is assigned without a person, and every decision is logged with the time it took.
- **Reporting:** a four-totals report built from the decision log. No individual records ever leave the machine.

[Diagram: 04-workflow.png]

## Rules and safeguards
- **Local only:** runs on the client's own computer, with no cloud AI, no tracking and no hosted database. A test fails the build if any code tries to reach the internet.
- **Identifiers never kept:** patient, adjuster, claim, order, SSN, ZIP and contact columns are dropped at import. Any value that looks like an SSN, phone number, email or ZIP code is blanked.
- **A person decides:** the system suggests; the coordinator approves, changes or rejects.
- **Data can't leak into the code repository:** data files are blocked from every commit automatically.

## Results
*Measured on 20 de-identified referrals from my own company's records, learning from 54 earlier referrals. Totals only.*
- **Missing information caught:** 2 of the 20 referrals had a missing or invalid required item, and both were flagged before routing, before the case could stall.
- **Vendor shortlist:** the vendor actually used was in the 3 suggestions for 10 of 18 referrals, compared with 7 of 18 for the simple rule "use the most common vendor for this product". Two referrals had no recorded vendor and were not scored.
- **Review time per referral, before vs. with the tool:** *being measured. Added once timed; never estimated.*

## Relevant experience
[Daniel's own words on real referral-intake work, client unnamed]

## Who it's for
Workers' comp managed care networks, TPAs, case management and DME intake teams.
