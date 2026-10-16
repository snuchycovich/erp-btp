from decimal import Decimal

import pytest

from app.domain import (
    QuoteItem,
    calculate_item_total,
    calculate_quote_total,
    calculate_tax,
)


@pytest.mark.parametrize("description", ["", "    "])
def test_quote_item_rejects_empty_description(description: str | None) -> None:
    """Reject missing, empty, or whitespace-only descriptions."""
    with pytest.raises(ValueError, match="description"):
        QuoteItem(
            description=description,
            quantity=Decimal(10),
            unit_price=Decimal("45.50"),
        )


@pytest.mark.parametrize(
    "quantity",
    [
        Decimal(0),
        Decimal(-10),
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_quote_item_rejects_non_positive_quantity(quantity: Decimal) -> None:
    """Reject zero, negative, and non-finite item quantities."""
    with pytest.raises(ValueError, match="quantity"):
        QuoteItem(
            description="Pose de carrlage",
            quantity=quantity,
            unit_price=Decimal("45.50"),
        )


@pytest.mark.parametrize(
    "unit_price",
    [Decimal("-45.50"), Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")],
)
def test_quote_item_rejects_negative_unit_price(unit_price: Decimal) -> None:
    """Reject negative and non-finite item prices."""
    with pytest.raises(ValueError, match="unit_price"):
        QuoteItem(
            description="Pose de carrlage", quantity=Decimal(10), unit_price=unit_price
        )


# Item validation
def test_quote_item_accept_zero_unit_price() -> None:
    """Allow an item to have a zero unit price."""
    item = QuoteItem(
        description="Pose de carrlage", quantity=Decimal(10), unit_price=Decimal(0)
    )

    assert item.unit_price == Decimal(0)


# Total calculations
def test_calculate_item_total() -> None:
    """Calculate the total for one quoted item."""
    item = QuoteItem(
        description="Pose de carrlage",
        quantity=Decimal(10),
        unit_price=Decimal("45.50"),
    )

    result = calculate_item_total(item)

    assert result == Decimal("455.00")
    # assert result.as_tuple().exponent == 2


def test_calculate_item_total_preserves_precision() -> None:
    """Preserve Decimal precision when calculating an item total."""
    item = QuoteItem(
        description="Prestation",
        quantity=Decimal(3),
        unit_price=Decimal("0.335"),
    )

    result = calculate_item_total(item)

    assert result == Decimal("1.005")


def test_calculate_quote_total() -> None:
    """Sum the item totals in a quote."""
    items = (
        QuoteItem(
            description="Pose de carrlage",
            quantity=Decimal(10),
            unit_price=Decimal("45.50"),
        ),
        QuoteItem(
            description="Pose de fenetre",
            quantity=Decimal(2),
            unit_price=Decimal("100.85"),
        ),
        QuoteItem(
            description="Isolation", quantity=Decimal(1), unit_price=Decimal("150.25")
        ),
    )

    result = calculate_quote_total(items)
    assert result == Decimal("806.95")


def test_calculate_quote_total_returns_zero_for_empty_quote() -> None:
    """Return Decimal zero when the quote has no items."""
    assert calculate_quote_total(()) == Decimal(0)


# Tax calculation
def test_calculate_tax() -> None:
    """Calculate and round tax to two decimal places."""
    result = calculate_tax(Decimal("806.95"), Decimal("5.50"))
    assert result == Decimal("44.38")


@pytest.mark.parametrize(
    ("tax_rate", "expected"),
    [
        (Decimal(0), Decimal("0.00")),
        (Decimal(100), Decimal("100.00")),
    ],
)
def test_calculate_tax_accepts_boundary_rates(
    tax_rate: Decimal, expected: Decimal
) -> None:
    """Accept tax rates at the inclusive zero and one-hundred boundaries."""
    result = calculate_tax(Decimal(100), tax_rate)

    assert result == expected


# Tax input validation
@pytest.mark.parametrize(
    "total_ht",
    [
        Decimal("-0.01"),
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_calculate_tax_rejects_invalid_total(total_ht: Decimal) -> None:
    """Reject negative or non-finite pre-tax totals."""
    with pytest.raises(ValueError):
        calculate_tax(total_ht, Decimal("20.00"))


@pytest.mark.parametrize(
    "tax_rate",
    [
        Decimal("-0.01"),
        Decimal("100.01"),
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_calculate_tax_rejects_invalid_rate(tax_rate: Decimal) -> None:
    """Reject non-finite tax rates and rates outside the inclusive 0-to-100 range."""
    with pytest.raises(ValueError):
        calculate_tax(Decimal(100), tax_rate)
