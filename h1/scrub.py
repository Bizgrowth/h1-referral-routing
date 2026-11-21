"""Patterns that catch personal identifiers in kept text fields."""

import re

SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b")
PHONE = re.compile(r"(?:\(\d{3}\)\s*|\b\d{3}[-. ])\d{3}[-. ]\d{4}\b|\b\d{10}\b")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
ZIP = re.compile(r"\b\d{5}(?:-\d{4})?\b")
LONG_NUMBER = re.compile(r"\d{7,}")
# "Looks like a name": a title followed by a capitalized word, or a label such as "patient: X".
TITLE_NAME = re.compile(r"\b(?:[Dd]r|[Mm]rs?|[Mm]s|[Mm]iss|[Mm]x)\.?\s+[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+)?")
LABEL_NAME = re.compile(r"\b(?i:patient|pt|claimant|name|adjuster|attn)\s*[:#-]\s*[A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+)?")


def has_identifier(text: str) -> bool:
    """True if the text contains an SSN, phone, email or ZIP pattern."""
    return any(p.search(text) for p in (SSN, PHONE, EMAIL, ZIP))


def strip_description(text: str) -> str:
    """Remove name-like, phone, email and long-number fragments from product_description."""
    for pattern in (EMAIL, PHONE, SSN, TITLE_NAME, LABEL_NAME, LONG_NUMBER):
        text = pattern.sub(" ", text)
    return " ".join(text.split())
