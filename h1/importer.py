"""Load the referral export (data/Referrals-v4.xlsx), keeping only the allowlisted columns.

Non-allowlisted columns (such as patient_name) are never loaded: only the header row is read
to name them, then the file is read again with just the allowed columns.
"""

from dataclasses import dataclass
from pathlib import Path
import re

import pandas as pd

from h1 import scrub

YEAR_COLUMN = "date of referral"
ALLOWED = ["hcpcs_code", "vendor_name", "product_description", "product_group", "referral_source",
           "patient_state", "diag_code_1", YEAR_COLUMN]
TEXT_FIELDS = ["referral_source", "product_group", "product_description", "patient_state"]
FORBIDDEN = re.compile(
    r"patient|claimant|first_?name|last_?name|^f_?name$|^l_?name$|^name$|adjuster|"
    r"order_?(no|num|number|id)|ssn|social_?sec|zip|postal|address|addr|phone|mobile|fax|"
    r"e_?mail|dob|birth|claim|member", re.IGNORECASE)
INPUT_NAMES = ["Referrals-v4.xlsx", "Referrals-v4.txt", "Referrals-v4.tsv"]


@dataclass
class ImportResult:
    rows: pd.DataFrame        # answer key is in the "answer_vendor" column
    messages: list            # safe to print: column names and counts only, never values
    forbidden_columns: list
    scrubbed_values: int      # rows with a value blanked by the privacy filter
    rejected_dates: int


def default_input(data_dir: Path) -> Path:
    for name in INPUT_NAMES:
        if (data_dir / name).exists():
            return data_dir / name
    return data_dir / INPUT_NAMES[0]


def _is_excel(path: Path) -> bool:
    return path.suffix.lower() in (".xlsx", ".xls")


def _read(path: Path, header_only: bool, allowed=ALLOWED) -> pd.DataFrame:
    keep = None if header_only else (lambda c: c in allowed)
    nrows = 0 if header_only else None
    if _is_excel(path):
        return pd.read_excel(path, sheet_name="Sheet1", dtype=object, usecols=keep, nrows=nrows)
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, usecols=keep,
                               nrows=nrows, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not read the text export as UTF-8 or Windows-1252.")


def _text(value) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _year(value: str):
    return int(value) if re.fullmatch(r"\d{4}", value) else None


def _letters(i: int) -> str:
    out = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        out = chr(65 + r) + out
    return out


def _labels(values, fmt) -> dict:
    return {v: fmt(i) for i, v in enumerate(sorted({v for v in values if v}))}


def load(path) -> ImportResult:
    path = Path(path)
    headers = [str(h) for h in _read(path, header_only=True).columns]
    extra = [h for h in headers if h not in ALLOWED]
    key = lambda h: re.sub(r"[^a-z0-9]+", "_", h.strip().lower()).strip("_")
    forbidden = [h for h in extra if FORBIDDEN.search(key(h))]
    other = [h for h in extra if h not in forbidden]

    messages = []
    if forbidden:
        messages.append("Dropped identifier column(s), never loaded: " + ", ".join(forbidden))
    if other:
        messages.append(f"Dropped {len(other)} other non-allowlisted column(s): " + ", ".join(other))

    raw = _read(path, header_only=False)
    for col in ALLOWED:
        if col not in raw.columns:
            raw[col] = ""
            messages.append(f"Column {col} not found; treated as blank.")
    df = raw[ALLOWED].map(_text)
    df.insert(0, "row_id", range(1, len(df) + 1))

    # The referral date must already be a 4-digit year.
    years = df[YEAR_COLUMN].map(_year)
    rejected = int(years.isna().sum())
    if rejected:
        messages.append(f"Rejected {rejected} row(s) whose {YEAR_COLUMN} is not a 4-digit year.")
    df = df[years.notna()].copy()
    df["year"] = years[years.notna()].astype(int)
    df = df.drop(columns=YEAR_COLUMN)

    # Values blanked by the privacy filter are recorded in _privacy so they are not reported as missing.
    df["_privacy"] = ""
    df["product_description"] = df["product_description"].map(scrub.strip_description)
    for col in TEXT_FIELDS:
        hits = df[col].map(scrub.has_identifier)
        df.loc[hits, col] = ""
        df.loc[hits, "_privacy"] += col + ","
    scrubbed = int((df["_privacy"] != "").sum())
    if scrubbed:
        messages.append(f"Blanked a value matching an SSN, phone, email or ZIP pattern on {scrubbed} row(s) "
                        "(not counted as missing).")

    for col in ("hcpcs_code", "diag_code_1"):
        df[col] = df[col].str.upper()
    sources = _labels(df["referral_source"], lambda i: "Source " + _letters(i))
    vendors = _labels(df["vendor_name"], lambda i: f"Vendor {i + 1:02d}")
    df["referral_source"] = df["referral_source"].map(lambda v: sources.get(v, ""))
    df["answer_vendor"] = df["vendor_name"].map(lambda v: vendors.get(v, ""))
    df = df.drop(columns="vendor_name").reset_index(drop=True)
    return ImportResult(df, messages, forbidden, scrubbed, rejected)
