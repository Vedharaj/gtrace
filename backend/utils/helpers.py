"""Small, pure, reusable helper functions with no side effects on state."""

from __future__ import annotations

import math
import uuid
from pathlib import Path


def generate_file_id() -> str:
    """Generate a unique identifier for an uploaded file.

    Returns:
        A UUID4 hex string.
    """
    return uuid.uuid4().hex


def has_allowed_extension(filename: str, allowed: frozenset[str]) -> bool:
    """Check whether a filename has an allowed extension.

    Args:
        filename: The original filename supplied by the client.
        allowed: A set of allowed extensions, e.g. {".txt"}.

    Returns:
        True if the file's suffix is in ``allowed``.
    """
    return Path(filename).suffix.lower() in allowed


def safe_float(raw: str) -> float:
    """Parse a numeric string, tolerating gem5's nan/inf tokens.

    Args:
        raw: The raw numeric token extracted from a stats line.

    Returns:
        The parsed float value. ``nan``/``inf``/``-inf`` are parsed to
        their corresponding IEEE-754 special values.
    """
    lowered = raw.strip().lower()
    if lowered == "nan":
        return math.nan
    if lowered in ("inf", "+inf"):
        return math.inf
    if lowered == "-inf":
        return -math.inf
    return float(raw)


def is_finite_number(value: float) -> bool:
    """Return True if value is a real, finite number (not NaN/Inf)."""
    return math.isfinite(value)


def safe_divide(numerator: float, denominator: float) -> float | None:
    """Divide two numbers, returning None instead of raising on zero division.

    Args:
        numerator: Dividend.
        denominator: Divisor.

    Returns:
        The quotient, or None if the denominator is zero or either
        operand is not finite.
    """
    if denominator == 0 or not (is_finite_number(numerator) and is_finite_number(denominator)):
        return None
    return numerator / denominator