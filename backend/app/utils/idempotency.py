from __future__ import annotations

from .hashing import hash_description, normalize_description


def compute_hash(description: str) -> tuple[str, str]:
    """Return normalized description and its hash."""
    normalized = normalize_description(description)
    return normalized, hash_description(description)
