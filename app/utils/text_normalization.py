# app/utils/text_normalization.py
from __future__ import annotations

import re
import unicodedata
from typing import Optional


def normalize_text(value: Optional[str]) -> str:
    """
    Normalize text for robust comparisons.

    Steps:
    - Treats None or empty as empty string.
    - Converts to lowercase.
    - Strips accents (e.g., 'á' -> 'a').
    - Removes all non-alphanumeric characters (keeps only a-z and 0-9).

    This is useful for:
    - Enforcing uniqueness ignoring case, accents and punctuation.
    - Implementing fuzzy-like equality checks for names and addresses.
    """
    if not value:
        return ""

    # Lowercase
    value = value.lower()

    # Remove accents
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")

    # Keep only alphanumeric characters
    value = re.sub(r"[^a-z0-9]", "", value)

    return value
