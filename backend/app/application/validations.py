"""Validation helpers for domain values and business constraints."""

from decimal import Decimal


def validate_required(name: str, value: object) -> None:
    """Reject a missing value while allowing valid empty collections."""
    if value is None:
        raise ValueError(f"{name} cannot be empty, given value {value}")


def validate_positive_integer(name: str, value: int) -> None:
    """Reject values that are not positive integers, including booleans."""
    if isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be strictly positive, given value {value}")


def validate_non_negative_integer(name: str, value: int) -> None:
    """Reject values that are not non-negative integers, including booleans."""
    if isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be non-negative, given value {value}")


def validate_not_empty(name: str, value: str) -> None:
    """Reject empty strings and strings containing only whitespace."""
    if not value.strip():
        raise ValueError(f"{name} cannot be empty, given value {value}")


def validate_positive_decimal(
    name: str, value: Decimal, allow_zero: bool = False
) -> None:
    """Reject non-finite and negative values, and reject zero unless explicitly allowed."""
    if not value.is_finite() or value < 0 or (not allow_zero and value == 0):
        constraint = "non-negative" if allow_zero else "strictly positive"
        raise ValueError(f"{name} must be {constraint}, given value {value}")
