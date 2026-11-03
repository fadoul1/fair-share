from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

CENT = Decimal("0.01")


@dataclass(frozen=True)
class Money:
    """Strictly positive amount with at most two decimals, stored as a Decimal."""

    amount: Decimal

    @classmethod
    def parse(cls, value: "Money | Decimal | str | int") -> "Money":
        """Single entry point: turn raw input into Money or raise ValueError."""
        if isinstance(value, Money):
            return value
        # bool is a subclass of int, so reject it explicitly.
        if isinstance(value, bool) or not isinstance(value, Decimal | str | int):
            raise ValueError(
                f"amount must be a number, a numeric string or a Decimal, "
                f"got {type(value).__name__}: {value!r}"
            )

        try:
            if isinstance(value, str):
                value = value.strip()
            amount = value if isinstance(value, Decimal) else Decimal(value)
        except InvalidOperation:
            raise ValueError(f"amount is not a number: {value!r}") from None

        if not amount.is_finite():
            raise ValueError(f"amount must be a finite number: {value!r}")
        if amount <= 0:
            raise ValueError(f"amount must be greater than zero: {value!r}")

        try:
            rounded = amount.quantize(CENT)
        except InvalidOperation:
            raise ValueError(f"amount is too large: {value!r}") from None
        if rounded != amount:
            raise ValueError(f"amount must have at most 2 decimal places: {value!r}")

        return cls(rounded)
