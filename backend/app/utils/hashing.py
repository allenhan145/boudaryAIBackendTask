from __future__ import annotations

import hashlib


def normalize_description(description: str) -> str:
    """Normalize the description by trimming, lowering, and collapsing spaces."""
    return " ".join(description.strip().lower().split())


def hash_description(description: str) -> str:
    normalized = normalize_description(description)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
