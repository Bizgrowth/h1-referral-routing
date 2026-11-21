"""Rank vendors from local history. No outside AI.

The product settles the vendor for most rows, so every product-level vendor is a candidate.
More specific contexts (city, source, HCPCS, diagnosis codes) only reorder vendors when they
have enough history. When the product was never seen, back off to HCPCS + product group,
then product group alone. The answer key (answer_vendor) is never an input feature.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass

MIN_SUPPORT = 2  # rows a specific context needs before it can reorder vendors
DIAG = ("diag_code_2", "diag_code_4")
LEVELS = [
    (("product_description", "hcpcs_code", "product_group", *DIAG, "referral_source", "insurance_company_city"),
     "product, HCPCS code, diagnosis codes, referral source and carrier city"),
    (("product_description", "referral_source", "insurance_company_city"),
     "product from this referral source and carrier city"),
    (("product_description", "insurance_company_city"), "product in this carrier city"),
    (("product_description", "referral_source"), "product from this referral source"),
    (("product_description", "hcpcs_code"), "product and HCPCS code"),
    (("product_description",), "product"),
    (("hcpcs_code", "product_group"), "HCPCS code in this product group"),
    (("product_group",), "product group"),
]
PRODUCT_LEVEL = 5
FEATURES = sorted({f for fields, _ in LEVELS for f in fields})


@dataclass
class Suggestion:
    vendor: str
    reason: str


def _key(row, fields):
    values = tuple(str(row.get(f, "")).strip() for f in fields)
    # A blank context field (other than diagnosis codes) can't define a context.
    if any(not v for f, v in zip(fields, values) if f not in DIAG):
        return None
    return values


class Suggester:
    def __init__(self):
        self.tables = [defaultdict(Counter) for _ in LEVELS]

    @classmethod
    def fit(cls, train_rows):
        model = cls()
        for row in train_rows.to_dict("records"):
            vendor = row.get("answer_vendor", "")
            if not vendor:
                continue
            for table, (fields, _) in zip(model.tables, LEVELS):
                key = _key(row, fields)
                if key is not None:
                    table[key][vendor] += 1
        return model

    def suggest(self, row, k=3) -> list:
        row = {f: row.get(f, "") for f in FEATURES}  # only feature fields are ever read
        product = self.tables[PRODUCT_LEVEL].get(_key(row, LEVELS[PRODUCT_LEVEL][0]) or (), Counter())
        picked = []
        for i, (table, (fields, label)) in enumerate(zip(self.tables, LEVELS)):
            key = _key(row, fields)
            counts = table.get(key) if key is not None else None
            if not counts or (i < PRODUCT_LEVEL and sum(counts.values()) < MIN_SUPPORT):
                continue
            for vendor, n in sorted(counts.items(), key=lambda kv: (-kv[1], -product[kv[0]], kv[0])):
                if vendor not in {s.vendor for s in picked}:
                    picked.append(Suggestion(vendor, f"Used for this {label} {n} time{'s' if n != 1 else ''}"))
                if len(picked) == k:
                    return picked
        return picked


class Baseline:
    """Most common vendor for this product in the training years."""

    def __init__(self, train_rows):
        self.counts = defaultdict(Counter)
        for row in train_rows.to_dict("records"):
            if row.get("answer_vendor") and row.get("product_description"):
                self.counts[row["product_description"]][row["answer_vendor"]] += 1

    def predict(self, row, k=3) -> list:
        counts = self.counts.get(row.get("product_description", ""), Counter())
        return [v for v, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]]

    def vendor_count(self, product) -> int:
        return len(self.counts.get(product, ()))
