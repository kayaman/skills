# Template: Python Aggregate

Copy and adapt. Replace `Order`, `OrderId`, `LineItem`, etc. with the
concrete domain terms. Remove what doesn't apply.

```python
# domain/aggregates.py
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import NewType, override
from uuid import UUID, uuid4

from .events import DomainEvent, OrderPlaced, OrderShipped, OrderCancelled
from .value_objects import Money, LineItem


# ── Identifiers (branded) ────────────────────────────────────────────
OrderId    = NewType("OrderId", UUID)
CustomerId = NewType("CustomerId", UUID)


# ── Aggregate root ───────────────────────────────────────────────────
@dataclass(eq=False, slots=True)
class Order:
    """Aggregate root for a customer's order.

    Protects the invariants:
      • must contain at least one line item.
      • total equals sum of line item subtotals.
      • can only be shipped from 'paid'.
      • can only be cancelled before 'shipped'.
    """
    id: OrderId
    customer_id: CustomerId
    _items: list[LineItem] = field(default_factory=list)
    _status: str = "placed"        # placed | paid | shipped | cancelled
    _events: list[DomainEvent] = field(default_factory=list)

    # -- construction --------------------------------------------------
    @classmethod
    def place(
        cls, customer_id: CustomerId, items: list[LineItem],
    ) -> "Order":
        if not items:
            raise ValueError("Order requires at least one line item")
        order_id = OrderId(uuid4())
        order = cls(id=order_id, customer_id=customer_id,
                    _items=list(items))
        order._events.append(
            OrderPlaced(order_id=order_id,
                        customer_id=customer_id,
                        total=order.total)
        )
        return order

    # -- commands ------------------------------------------------------
    def mark_paid(self) -> None:
        if self._status != "placed":
            raise ValueError(f"Cannot pay order in state {self._status}")
        self._status = "paid"

    def ship(self) -> None:
        if self._status != "paid":
            raise ValueError("Cannot ship unpaid order")
        self._status = "shipped"
        self._events.append(OrderShipped(order_id=self.id))

    def cancel(self, reason: str) -> None:
        if self._status == "shipped":
            raise ValueError("Cannot cancel shipped order")
        self._status = "cancelled"
        self._events.append(OrderCancelled(order_id=self.id,
                                           reason=reason))

    # -- queries -------------------------------------------------------
    @property
    def total(self) -> Money:
        assert self._items, "invariant: items not empty"
        total = self._items[0].subtotal
        for item in self._items[1:]:
            total = total + item.subtotal
        return total

    @property
    def status(self) -> str:
        return self._status

    # -- event collection ---------------------------------------------
    def pull_events(self) -> list[DomainEvent]:
        events, self._events = self._events, []
        return events

    # -- identity equality --------------------------------------------
    @override
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Order) and self.id == other.id

    @override
    def __hash__(self) -> int:
        return hash(self.id)
```

```python
# domain/value_objects.py
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Money cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be ISO 4217 code")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add {self.currency} to {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, n: int | Decimal) -> "Money":
        return Money(self.amount * Decimal(n), self.currency)


@dataclass(frozen=True, slots=True)
class LineItem:
    sku: str
    quantity: int
    unit_price: Money

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity
```

```python
# domain/events.py
from dataclasses import dataclass
from datetime import datetime, timezone

from .value_objects import Money


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Base marker. Concrete events are subclasses."""
    occurred_at: datetime = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        # Frozen: can't assign normally — use object.__setattr__.
        if self.occurred_at is None:
            object.__setattr__(self, "occurred_at",
                               datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class OrderPlaced(DomainEvent):
    order_id: "OrderId" = None  # type: ignore[assignment]
    customer_id: "CustomerId" = None  # type: ignore[assignment]
    total: Money = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class OrderShipped(DomainEvent):
    order_id: "OrderId" = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class OrderCancelled(DomainEvent):
    order_id: "OrderId" = None  # type: ignore[assignment]
    reason: str = ""
```

```python
# domain/ports.py
from typing import Protocol

from .aggregates import Order, OrderId, CustomerId


class OrderRepository(Protocol):
    def get(self, order_id: OrderId) -> Order: ...
    def add(self, order: Order) -> None: ...
    def find_by_customer(
        self, customer_id: CustomerId,
    ) -> list[Order]: ...
```

---

## Notes on customization

- **Identity generation.** `uuid4()` is fine for most systems. For
  time-ordered IDs, use UUID v7 (available from `uuid-utils` or
  implemented by hand). Never use auto-incrementing DB IDs in the
  domain — it couples identity to persistence.
- **Events with fields.** The trick above (`field = None` with type
  ignore, set via `__post_init__`) is necessary because frozen
  dataclass inheritance with mandatory fields is awkward. If you have
  many event types, consider separate frozen dataclasses without a
  common base.
- **Money precision.** `Decimal` for accounting. Never float.
- **Status as enum.** Once you have three or more statuses, promote
  `_status: str` to a `StrEnum` (3.11+) or a `Literal` type.
- **Invariants in pydantic.** If you want richer validation (regex,
  ranges), use Pydantic *for DTOs only*. Keep the domain plain.
