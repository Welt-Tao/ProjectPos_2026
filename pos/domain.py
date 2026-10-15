"""Domain values and business validation. Money uses integer cents."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


class BusinessError(ValueError):
    """A request violates a business rule."""


def quantity(value):
    if type(value) is not int or not 1 <= value <= 999:
        raise BusinessError("Quantity must be a whole number between 1 and 999.")
    return value


def money(value):
    if not isinstance(value, str) or len(value) > 20:
        raise BusinessError("Enter a cash amount with at most two decimal places.")
    try:
        amount = Decimal(value)
        if not amount.is_finite() or amount < 0 or amount > 1000000 or amount.as_tuple().exponent < -2:
            raise ValueError()
        return int(amount * 100)
    except (InvalidOperation, ValueError):
        raise BusinessError("Enter a valid non-negative cash amount with at most two decimal places.")


@dataclass(frozen=True)
class SaleLine:
    sku: str
    name: str
    unit_price: int
    quantity: int

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


@dataclass(frozen=True)
class Sale:
    lines: tuple[SaleLine, ...]

    @property
    def total(self):
        return sum(line.subtotal for line in self.lines)


@dataclass(frozen=True)
class CashPayment:
    tendered: int

    def change_for(self, total):
        if self.tendered < total:
            raise BusinessError("Insufficient cash. Increase the amount received.")
        return self.tendered - total
