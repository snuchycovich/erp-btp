from decimal import Decimal

import pytest

from app.domain import (
    QuoteItem,
    calculate_item_total,
    calculate_quote_total,
    calculate_tax,
)


# QuoteItem validation
@pytest.mark.parametrize("quantity", [Decimal(0), Decimal(-10)])
def test_quote_item_rejects_non_positive_quantity(quantity: Decimal) -> None:
    """Reject zero and negative item quantities."""
    with pytest.raises(ValueError):
        QuoteItem(
            description="Pose de carrlage",
            quantity=quantity,
            unit_price=Decimal("45.50"),
        )


@pytest.mark.parametrize("unit_price", [Decimal("-45.50")])
def test_quote_item_rejects_negative_unit_price(unit_price: Decimal) -> None:
    """Reject negative item prices."""
    with pytest.raises(ValueError):
        QuoteItem(
            description="Pose de carrlage", quantity=Decimal(10), unit_price=unit_price
        )


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


# Tax calculation and validation
def test_calculate_tax() -> None:
    """Calculate and round tax to two decimal places."""
    result = calculate_tax(Decimal("806.95"), Decimal("5.50"))
    assert result == Decimal("44.38")


@pytest.mark.parametrize("tax_rate", [Decimal(0), Decimal(100)])
def test_calculate_tax_accepts_boundary_rates(tax_rate: Decimal) -> None:
    """Accept tax rates at the inclusive zero and one-hundred boundaries."""
    calculate_tax(Decimal(100), tax_rate)


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
    """Reject tax rates outside the valid finite range from zero to one hundred."""
    with pytest.raises(ValueError):
        calculate_tax(Decimal(100), tax_rate)
