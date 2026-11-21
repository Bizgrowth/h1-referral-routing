# H1 intake fields and how each must be handled (Nov 20)

Rule: no referral record, image or field value from the database goes into the portfolio, the PDF, the video, or this chat. Real data is used only privately, de-identified, to run the MVP and measure the three numbers. Only aggregate numbers (e.g. "median review time fell from X to Y on N referrals") appear publicly, and only with the data owner's written OK.
De-identification follows HIPAA Safe Harbor (the 18 identifiers removed). Have whoever owns the data confirm it.

## Never use (remove entirely or replace with a generated ID)
| Field | Why |
|---|---|
| Claimant name | Direct identifier |
| SSN | Direct identifier |
| Claimant address, phone, email | Direct identifiers (keep first 3 ZIP digits only if allowed, see below) |
| Claim number, member ID, case ID | Record numbers; replace with a new random ID |
| Employer contact name, phone, email | Personal contact details |
| Adjuster / nurse case manager name and contact | Third-party personal details |
| Referring physician name, NPI, contact | Third-party personal details |
| Scanned referral image, fax or PDF | Can't be reliably de-identified |
| Free-text notes | Often hide names, dates and details; drop or redact by hand |

## Generalize
| Field | Keep as |
|---|---|
| Date of birth | Age in years (group 90+ together) |
| Date of injury, referral date | Days between injury and referral, or year only |
| Location | State, or first 3 ZIP digits (not if that area has under 20,000 people) |
| Employer name | Industry (e.g. "warehouse", "construction") |
| Carrier / TPA name | "Carrier A", "Carrier B" |
| Clinic names in the network | "Clinic 01", "Clinic 02" unless the network owner OKs real names |

## Safe to keep (after the above)
| Field | Used for |
|---|---|
| Injury type / description (cleaned) | Extraction and specialty match |
| ICD-10 code | Specialty match |
| Body part | Specialty match |
| Service requested (eval, PT, imaging, etc.) | Clinic match |
| Jurisdiction (state) | Network rules |
| Urgency / priority | Routing order |
| Which required fields were missing | "Missing information caught" measure |
| Clinic: network status, specialty, distance band | Clinic match |
| Coordinator's actual clinic choice | "Match agreement" measure |
| Time the coordinator spent per referral | "Review time" measure |
