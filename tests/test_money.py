from decimal import Decimal

import pytest

from fair_share.money import Money


@pytest.mark.parametrize("bad", ["ten", "", "  ", "1,5", "abc12", "NaN", "Infinity"])
def test_rejects_non_numbers(bad: str) -> None:
    with pytest.raises(ValueError, match="number"):
        Money.parse(bad)


@pytest.mark.parametrize("bad", ["0", "-5.00", Decimal("0"), Decimal("-0.01"), -3, 0])
def test_rejects_zero_and_negative(bad: str | Decimal | int) -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        Money.parse(bad)


@pytest.mark.parametrize("bad", ["10.005", Decimal("0.001"), "1.234"])
def test_rejects_more_than_two_decimals(bad: str | Decimal) -> None:
    with pytest.raises(ValueError, match="2 decimal places"):
        Money.parse(bad)


@pytest.mark.parametrize("bad", [10.5, 0.1, None, [1], True])
def test_rejects_floats_and_other_types(bad: object) -> None:
    with pytest.raises(ValueError, match="must be a number"):
        Money.parse(bad)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("10", "10.00"),
        (" 10.5 ", "10.50"),
        ("10.00", "10.00"),
        ("10.0000", "10.00"),
        (7, "7.00"),
        (Decimal("0.01"), "0.01"),
    ],
)
def test_accepts_valid_amounts(raw: str | int | Decimal, expected: str) -> None:
    assert Money.parse(raw).amount == Decimal(expected)


def test_money_is_stored_as_decimal() -> None:
    assert isinstance(Money.parse("1.50").amount, Decimal)


def test_parse_is_idempotent() -> None:
    money = Money.parse("3.00")
    assert Money.parse(money) is money
