from decimal import Decimal

import pytest

from fair_share.group import Group
from fair_share.money import Money


def make_group() -> Group:
    return Group(["Ana", "Ben", "Cy"])


def test_rejects_negative_amount() -> None:
    with pytest.raises(ValueError):
        make_group().add_expense(
            paid_by="Ana", amount=Decimal("-5.00"), split_between=["Ana", "Ben"]
        )


def test_rejects_unknown_payer() -> None:
    with pytest.raises(ValueError):
        make_group().add_expense(
            paid_by="Zoe", amount=Decimal("5.00"), split_between=["Ana"]
        )


def test_balances_always_sum_to_zero() -> None:
    group = make_group()
    group.add_expense(
        paid_by="Ana", amount=Decimal("10.00"), split_between=["Ana", "Ben", "Cy"]
    )
    assert sum(group.balance(name) for name in ["Ana", "Ben", "Cy"]) == 0


# --- Amount ------------------------------------------------------------------


def test_rejects_amount_typed_as_text() -> None:
    with pytest.raises(ValueError, match="not a number"):
        make_group().add_expense("Ana", "ten", ["Ben"])


def test_rejects_zero_amount() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        make_group().add_expense("Ana", Decimal("0"), ["Ben"])


def test_rejects_three_decimals() -> None:
    with pytest.raises(ValueError, match="2 decimal places"):
        make_group().add_expense("Ana", "10.005", ["Ben"])


def test_rejects_float_amount() -> None:
    with pytest.raises(ValueError, match="must be a number"):
        make_group().add_expense("Ana", 10.5, ["Ben"])  # type: ignore[arg-type]


def test_accepts_numeric_text_and_money() -> None:
    group = make_group()
    group.add_expense("Ana", "10.00", ["Ben"])
    group.add_expense("Ana", Money.parse("5"), ["Ben"])
    assert group.balance("Ben") == Decimal("-15.00")


# --- Participants ------------------------------------------------------------


def test_rejects_empty_split() -> None:
    with pytest.raises(ValueError, match="at least one person"):
        make_group().add_expense("Ana", "5.00", [])


def test_rejects_unknown_participant() -> None:
    with pytest.raises(ValueError, match="unknown member"):
        make_group().add_expense("Ana", "5.00", ["Ben", "Zoe"])


def test_rejects_duplicate_in_split() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        make_group().add_expense("Ana", "5.00", ["Ben", "Ben"])


# --- Names -------------------------------------------------------------------


@pytest.mark.parametrize("variant", ["ben ", " BEN", "Ben", "bEn"])
def test_name_variants_are_the_same_person(variant: str) -> None:
    group = make_group()
    group.add_expense("Ana", "10.00", [variant])
    assert group.balance("Ben") == Decimal("-10.00")
    assert group.balance(variant) == Decimal("-10.00")


def test_name_variants_in_split_are_detected_as_duplicates() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        make_group().add_expense("Ana", "5.00", ["Ben", "ben "])


def test_rejects_duplicate_members_in_group() -> None:
    with pytest.raises(ValueError, match="duplicate member"):
        Group(["Ben", "ben "])


def test_rejects_blank_member_name() -> None:
    with pytest.raises(ValueError, match="empty"):
        Group(["Ana", "   "])


# --- Invariants --------------------------------------------------------------


def test_leftover_cents_are_spread() -> None:
    group = make_group()
    group.add_expense("Ana", "10.00", ["Ana", "Ben", "Cy"])
    # Ana pays 10.00 and bears the 3.34 share (she gets the leftover cent).
    assert group.balance("Ana") == Decimal("6.66")
    assert group.balance("Ben") == Decimal("-3.33")
    assert group.balance("Cy") == Decimal("-3.33")


@pytest.mark.parametrize("amount", ["0.01", "0.02", "10.00", "99.99", "100.01"])
@pytest.mark.parametrize("count", [1, 2, 3, 7])
def test_balances_sum_to_zero_for_any_split(amount: str, count: int) -> None:
    names = ["Ana", "Ben", "Cy", "Di", "Eli", "Flo", "Gus"]
    group = Group(names)
    group.add_expense("Ana", amount, names[:count])
    assert sum(group.balance(n) for n in names) == 0


def test_failed_expense_leaves_balances_untouched() -> None:
    group = make_group()
    with pytest.raises(ValueError):
        group.add_expense("Ana", "5.00", ["Ben", "Zoe"])
    assert all(group.balance(n) == 0 for n in ["Ana", "Ben", "Cy"])
