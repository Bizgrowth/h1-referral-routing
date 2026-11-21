"""Load a referral export, keeping only the allowlisted columns.

Non-allowlisted columns are never loaded: only the header row is read to name them,
then the file is read again with just the allowed columns.
"""

from dataclasses import dataclass
from pathlib import Path
import re

import pandas as pd

from h1 import scrub

ALLOWED = ["insurance_company_city", "referral_source", "Expr1002", "product_group", "quantity",
           "vendor_name", "hcpcs_code", "DATE", "diag_code_2", "diag_code_4", "product_description"]
TEXT_FIELDS = ["insurance_company_city", "referral_source", "product_name", "product_group",
               "product_description"]
FORBIDDEN = re.compile(
    r"patient|claimant|first_?name|last_?name|^f_?name$|^l_?name$|^name$|adjuster|"
    r"order_?(no|num|number|id)|ssn|social_?sec|zip|postal|address|addr|phone|mobile|fax|"
    r"e_?mail|dob|birth|claim|member", re.IGNORECASE)
INPUT_NAMES = ["Referrals.xlsx", "Referrals.txt", "Referrals.tsv"]


@dataclass
class ImportResult:
    rows: pd.DataFrame        # answer key is in the "answer_vendor" column
    messages: list            # safe to print: column names and counts only, never values
    forbidden_columns: list
    scrubbed_values: int
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
        messages.append("WARNING: dropped identifier columns: " + ", ".join(forbidden))
    if other:
        messages.append(f"Dropped {len(other)} other non-allowlisted column(s): " + ", ".join(other))

    raw = _read(path, header_only=False)
    for col in ALLOWED:
        if col not in raw.columns:
            raw[col] = ""
            messages.append(f"Column {col} not found; treated as blank.")
    df = raw[ALLOWED].map(_text)
    df.insert(0, "row_id", range(1, len(df) + 1))

    # Expr1002 is an Access alias for the product name.
    if (df["Expr1002"] == df["product_description"]).all():
        df = df.drop(columns="Expr1002")
        messages.append("Expr1002 matches product_description on every row; dropped.")
    else:
        df = df.rename(columns={"Expr1002": "product_name"})

    # DATE must already be a 4-digit year.
    years = df["DATE"].map(_year)
    rejected = int(years.isna().sum())
    if rejected:
        messages.append(f"Rejected {rejected} row(s) whose DATE is not a 4-digit year.")
    df = df[years.notna()].copy()
    df["year"] = years[years.notna()].astype(int)
    df = df.drop(columns="DATE")

    scrubbed = 0
    df["product_description"] = df["product_description"].map(scrub.strip_description)
    for col in (c for c in TEXT_FIELDS if c in df.columns):
        hits = df[col].map(scrub.has_identifier)
        scrubbed += int(hits.sum())
        df.loc[hits, col] = ""
    if scrubbed:
        messages.append(f"Blanked {scrubbed} value(s) matching an SSN, phone, email or ZIP pattern.")

    for col in ("hcpcs_code", "diag_code_2", "diag_code_4"):
        df[col] = df[col].str.upper()
    sources = _labels(df["referral_source"], lambda i: "Source " + _letters(i))
    vendors = _labels(df["vendor_name"], lambda i: f"Vendor {i + 1:02d}")
    df["referral_source"] = df["referral_source"].map(lambda v: sources.get(v, ""))
    df["answer_vendor"] = df["vendor_name"].map(lambda v: vendors.get(v, ""))
    df = df.drop(columns="vendor_name").reset_index(drop=True)
    return ImportResult(df, messages, forbidden, scrubbed, rejected)
