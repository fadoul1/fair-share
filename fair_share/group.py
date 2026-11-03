from decimal import ROUND_DOWN, Decimal

from fair_share.money import CENT, Money


def _key(name: str) -> str:
    """The single place where names are cleaned: "ben " and "Ben" are the same."""
    if not isinstance(name, str):
        raise ValueError(f"name must be text, got {type(name).__name__}: {name!r}")
    key = " ".join(name.split()).casefold()
    if not key:
        raise ValueError("name must not be empty")
    return key


class Group:
    """A group of people who share expenses."""

    def __init__(self, members: list[str]) -> None:
        self._balances: dict[str, Decimal] = {}
        for name in members:
            key = _key(name)
            if key in self._balances:
                raise ValueError(f"duplicate member: {name!r}")
            self._balances[key] = Decimal(0)

    def _member(self, name: str, role: str) -> str:
        key = _key(name)
        if key not in self._balances:
            raise ValueError(f"unknown {role}: {name!r}")
        return key

    def add_expense(
        self,
        paid_by: str,
        amount: Money | Decimal | str | int,
        split_between: list[str],
    ) -> None:
        """Record an expense paid by `paid_by`, split between `split_between`."""
        # All validation happens before any balance is modified.
        money = Money.parse(amount).amount
        payer = self._member(paid_by, "payer")
        if not split_between:
            raise ValueError("split_between must contain at least one person")
        participants = [self._member(name, "member") for name in split_between]
        if len(set(participants)) != len(participants):
            raise ValueError(f"duplicate names in split: {split_between!r}")

        # Base share rounded down to the cent; leftover cents are handed out
        # one by one so the shares always add up exactly to the total.
        count = len(participants)
        base = (money / count).quantize(CENT, rounding=ROUND_DOWN)
        remainder_cents = int((money - base * count) / CENT)

        self._balances[payer] += money
        for index, key in enumerate(participants):
            share = base + (CENT if index < remainder_cents else Decimal(0))
            self._balances[key] -= share

    def balance(self, name: str) -> Decimal:
        """Balance of a person: positive if owed money, negative if owing."""
        return self._balances[self._member(name, "member")]
