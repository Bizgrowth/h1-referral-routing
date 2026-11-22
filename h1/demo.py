"""Fictional demo referrals so the app can be shown without real data.

Every product, vendor and source combination here is invented for the demo.
HCPCS and ICD-9 codes are public code-set values, not patient data.
The demo file is written under output/ (gitignored) and loaded through the normal importer.
"""

from pathlib import Path
import random

import pandas as pd

STATES = ["FL", "GA", "TX", "OH", "CA"]
EAST = {"FL", "GA", "OH"}
SOURCES = ["Carrier intake line", "Nurse case manager", "Adjuster portal", "Employer clinic"]
# product, service type, HCPCS, diagnosis options, vendor picker(state)
PRODUCTS = [
    ("Lumbar-sacral orthosis, prefabricated", "ORTHOTICS", "L0650", ["724.2", "722.10"],
     lambda state, r: "Northline Orthotics"),
    ("Knee orthosis, hinged", "ORTHOTICS", "L1833", ["844.9", "836.0"],
     lambda state, r: "Northline Orthotics" if r < .65 else "Coastal Brace Co"),
    ("Cervical collar, semi-rigid", "ORTHOTICS", "L0174", ["847.0"], lambda state, r: "Coastal Brace Co"),
    ("TENS unit, 4 lead", "DME", "E0730", ["724.2", "729.1"], lambda state, r: "Relief Devices Inc"),
    ("Electrode pads, 4-pack", "Medical Supplies", "A4595", [], lambda state, r: "Relief Devices Inc"),
    ("Cold therapy unit with pad", "DME", "E0218", ["840.9", "844.9"],
     lambda state, r: "Polar Recovery Supply" if r < .75 else "Relief Devices Inc"),
    ("Standard wheelchair", "DME", "K0001", ["824.8"],
     lambda state, r: ("Harbor Mobility" if state in EAST else "Summit Medical Equipment") if r < .85
     else ("Summit Medical Equipment" if state in EAST else "Harbor Mobility")),
    ("Knee walker", "DME", "E0118", ["825.20", "824.8"],
     lambda state, r: ("Harbor Mobility" if state in EAST else "Summit Medical Equipment") if r < .8
     else ("Summit Medical Equipment" if state in EAST else "Harbor Mobility")),
    ("Nebulizer with compressor", "Respiratory", "E0570", ["493.90"], lambda state, r: "Summit Medical Equipment"),
]
YEARS = {2025: 240, 2026: 24}


def rows(seed: int = 7) -> list:
    rng = random.Random(seed)
    out = []
    for year, n in YEARS.items():
        for _ in range(n):
            product, group, hcpcs, diags, pick = rng.choice(PRODUCTS)
            state = rng.choice(STATES)
            out.append({
                "hcpcs_code": hcpcs, "vendor_name": pick(state, rng.random()), "product_description": product,
                "product_group": group, "referral_source": rng.choice(SOURCES), "patient_state": state,
                "diag_code_1": rng.choice(diags) if diags and rng.random() < .6 else "",
                "date of referral": year,
            })
    # Realistic intake problems in the review year, so the missing-info check has work to do.
    review = [r for r in out if r["date of referral"] == 2026]
    review[2]["referral_source"] = ""
    review[5]["hcpcs_code"] = "E73"
    review[9]["patient_state"] = ""
    review[13]["product_group"] = ""
    review[17]["diag_code_1"] = "72.4"
    review[20]["vendor_name"] = ""  # no recorded vendor: reviewed, but not scored
    return out


def write(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows()).to_excel(path, sheet_name="Sheet1", index=False)
    return path
