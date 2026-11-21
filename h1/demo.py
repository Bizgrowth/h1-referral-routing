"""Fictional demo referrals so the app can be shown without real data.

Every product, vendor, source and city combination here is invented for the demo.
HCPCS and ICD-9 codes are public code-set values, not patient data.
The demo file is written under output/ (gitignored) and loaded through the normal importer.
"""

from pathlib import Path
import random

import pandas as pd

CITIES = ["Jacksonville", "Orlando", "Tampa", "Miami", "Atlanta"]
NORTH = {"Jacksonville", "Orlando", "Atlanta"}
SOURCES = ["Carrier intake line", "Nurse case manager", "Adjuster portal", "Employer clinic"]
# product, group, HCPCS, diagnosis options, vendor picker(city)
PRODUCTS = [
    ("Lumbar-sacral orthosis, prefabricated", "Orthotics", "L0650", ["724.2", "722.10"],
     lambda city, r: "Northline Orthotics"),
    ("Knee orthosis, hinged", "Orthotics", "L1833", ["844.9", "836.0"],
     lambda city, r: "Northline Orthotics" if r < .65 else "Coastal Brace Co"),
    ("Cervical collar, semi-rigid", "Orthotics", "L0174", ["847.0"], lambda city, r: "Coastal Brace Co"),
    ("TENS unit, 4 lead", "Electrotherapy", "E0730", ["724.2", "729.1"], lambda city, r: "Relief Devices Inc"),
    ("Electrode pads, 4-pack", "Electrotherapy", "A4595", [], lambda city, r: "Relief Devices Inc"),
    ("Cold therapy unit with pad", "Cold therapy", "E0218", ["840.9", "844.9"],
     lambda city, r: "Polar Recovery Supply" if r < .75 else "Relief Devices Inc"),
    ("Standard wheelchair", "Mobility", "K0001", ["824.8"],
     lambda city, r: ("Harbor Mobility" if city in NORTH else "Summit Medical Equipment") if r < .85
     else ("Summit Medical Equipment" if city in NORTH else "Harbor Mobility")),
    ("Knee walker", "Mobility", "E0118", ["825.20", "824.8"],
     lambda city, r: ("Harbor Mobility" if city in NORTH else "Summit Medical Equipment") if r < .8
     else ("Summit Medical Equipment" if city in NORTH else "Harbor Mobility")),
    ("Shower chair with back", "Bathroom safety", "E0240", [], lambda city, r: "Summit Medical Equipment"),
]
YEARS = {2024: 110, 2025: 130, 2026: 24}


def rows(seed: int = 7) -> list:
    rng = random.Random(seed)
    out = []
    for year, n in YEARS.items():
        for _ in range(n):
            product, group, hcpcs, diags, pick = rng.choice(PRODUCTS)
            city = rng.choice(CITIES)
            diag = rng.choice(diags) if diags and rng.random() < .35 else ""
            out.append({
                "insurance_company_city": city, "referral_source": rng.choice(SOURCES), "Expr1002": product,
                "product_group": group, "quantity": rng.choice([2, 4]) if hcpcs == "A4595" else 1,
                "vendor_name": pick(city, rng.random()), "hcpcs_code": hcpcs, "DATE": year,
                "diag_code_2": diag, "diag_code_4": "", "product_description": product,
            })
    # Realistic intake problems in the review year, so the missing-info check has work to do.
    review = [r for r in out if r["DATE"] == 2026]
    review[2]["insurance_company_city"] = ""
    review[5]["hcpcs_code"] = "E73"
    review[9]["quantity"] = 0
    review[13]["product_group"] = ""
    review[17]["diag_code_2"] = "72.4"
    review[20]["vendor_name"] = ""  # no recorded vendor: reviewed, but not scored
    return out


def write(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows()).to_excel(path, sheet_name="Sheet1", index=False)
    return path
