# Template: Python Use Case (Interactor)

A use case orchestrates domain operations to fulfill one user intent.
It lives in the application layer, depends only on ports, and knows
nothing about HTTP, SQL, or frameworks.

Copy and adapt. Replace `PlaceOrder` and command fields with the
concrete use case.

```python
# application/commands.py
from __future__ import annotations

from dataclasses import dataclass

from domain.aggregates import CustomerId, OrderId
from domain.value_objects import LineItem


@dataclass(frozen=True, slots=True)
class PlaceOrderCommand:
    """Input DTO for the PlaceOrder use case.

    Immutable — commands should not be mutated after creation.
    Idempotency key is optional but recommended for at-least-once
    delivery from message consumers.
    """
    customer_id: CustomerId
    items: tuple[LineItem, ...]
    idempotency_key: str | None = None
```

```python
# application/place_order.py
from __future__ import annotations

from typing import Protocol

from domain.aggregates import Order, OrderId
from domain.events import DomainEvent
from domain.ports import OrderRepository

from .commands import PlaceOrderCommand


# ── Ports the use case needs (domain-facing abstractions) ────────────
class UnitOfWork(Protocol):
    """Transactional boundary + access to repositories."""
    orders: OrderRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, *exc: object) -> None: ...
    def commit(self) -> None: ...


class EventBus(Protocol):
    def publish(self, event: DomainEvent) -> None: ...


# ── The use case ────────────────────────────────────────────────────
class PlaceOrder:
    """Place a new order.

    Single responsibility: translate a PlaceOrderCommand into domain
    operations, persist the result, and publish emitted events.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        events: EventBus,
    ) -> None:
        self._uow = uow
        self._events = events

    def execute(self, cmd: PlaceOrderCommand) -> OrderId:
        # 1. Enter transaction. Any exception rolls back.
        with self._uow:
            # 2. Domain operation. All invariants enforced inside.
            order = Order.place(
                customer_id=cmd.customer_id,
                items=list(cmd.items),
            )

            # 3. Persist via the repository port.
            self._uow.orders.add(order)

            # 4. Commit. Event publication happens AFTER this succeeds,
            #    so consumers never see events for a rolled-back tx.
            self._uow.commit()

        # 5. Publish collected events. At-least-once semantics —
        #    handlers must be idempotent (see event-driven.md).
        for event in order.pull_events():
            self._events.publish(event)

        return order.id
```

---

## Composition root — wiring at startup

The use case is framework-free. Wiring happens once, at boot.

```python
# infrastructure/container.py
from application.place_order import PlaceOrder
from adapters.repositories import SqlAlchemyUnitOfWork
from adapters.messaging import KafkaEventBus
from infrastructure.db import engine
from infrastructure.kafka import producer


def build_place_order() -> PlaceOrder:
    uow = SqlAlchemyUnitOfWork(engine)
    bus = KafkaEventBus(producer)
    return PlaceOrder(uow=uow, events=bus)
```

---

## HTTP adapter — translating requests to commands

Controllers belong in `adapters/`, not in `application/`. They know
about HTTP; the use case does not.

```python
# adapters/http.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from application.commands import PlaceOrderCommand
from domain.aggregates import CustomerId
from domain.value_objects import LineItem, Money
from decimal import Decimal
from uuid import UUID

from infrastructure.container import build_place_order


class LineItemDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    sku: str
    quantity: int = Field(gt=0)
    unit_price_cents: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)


class PlaceOrderRequest(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)
    customer_id: UUID
    items: list[LineItemDTO] = Field(min_length=1)
    idempotency_key: str | None = None


router = APIRouter()


@router.post("/orders", status_code=201)
def place_order(body: PlaceOrderRequest) -> dict[str, str]:
    # DTO → domain command at the boundary.
    cmd = PlaceOrderCommand(
        customer_id=CustomerId(body.customer_id),
        items=tuple(
            LineItem(
                sku=i.sku,
                quantity=i.quantity,
                unit_price=Money(
                    amount=Decimal(i.unit_price_cents) / 100,
                    currency=i.currency,
                ),
            )
            for i in body.items
        ),
        idempotency_key=body.idempotency_key,
    )
    try:
        order_id = build_place_order().execute(cmd)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"order_id": str(order_id)}
```

---

## Testing — in-memory fakes, no framework

```python
# tests/application/test_place_order.py
from uuid import uuid4
from decimal import Decimal

from application.commands import PlaceOrderCommand
from application.place_order import PlaceOrder
from domain.aggregates import CustomerId, Order, OrderId
from domain.events import DomainEvent, OrderPlaced
from domain.value_objects import LineItem, Money


class FakeOrderRepository:
    def __init__(self) -> None:
        self._orders: dict[OrderId, Order] = {}
        self.added: list[Order] = []

    def get(self, order_id: OrderId) -> Order:
        return self._orders[order_id]

    def add(self, order: Order) -> None:
        self._orders[order.id] = order
        self.added.append(order)

    def find_by_customer(self, customer_id):
        return [o for o in self._orders.values()
                if o.customer_id == customer_id]


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.orders = FakeOrderRepository()
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass

    def commit(self) -> None:
        self.committed = True


class FakeEventBus:
    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published.append(event)


def test_place_order_persists_and_emits_event() -> None:
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    use_case = PlaceOrder(uow=uow, events=bus)

    cmd = PlaceOrderCommand(
        customer_id=CustomerId(uuid4()),
        items=(
            LineItem(
                sku="sku-1",
                quantity=2,
                unit_price=Money(Decimal("19.99"), "USD"),
            ),
        ),
    )

    order_id = use_case.execute(cmd)

    assert uow.committed is True
    assert len(uow.orders.added) == 1
    assert uow.orders.added[0].id == order_id
    assert any(isinstance(e, OrderPlaced) for e in bus.published)


def test_place_order_rejects_empty_items() -> None:
    import pytest
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    use_case = PlaceOrder(uow=uow, events=bus)

    cmd = PlaceOrderCommand(
        customer_id=CustomerId(uuid4()),
        items=(),
    )

    with pytest.raises(ValueError):
        use_case.execute(cmd)

    assert uow.committed is False
    assert bus.published == []
```

Runs in milliseconds. No DB, no broker, no FastAPI. The real adapters
get their own integration tests verifying they map correctly to and
from the domain.

---

## Notes on customization

- **Query vs command.** This template is for a *command* use case
  (mutates state, returns a small confirmation). For queries, skip the
  UnitOfWork and return read-optimized data — often bypassing
  aggregates entirely (see `event-driven.md` § CQRS).
- **Idempotency.** If the command originates from a message consumer
  or an HTTP client with retries, store processed `idempotency_key`s
  and short-circuit duplicates. A dedicated `IdempotencyStore` port
  works well.
- **Cross-aggregate coordination.** Never mutate two aggregates in one
  `with self._uow:` block. Publish a domain event from the first; a
  handler (in a new transaction) mutates the second. See
  `event-driven.md` for the outbox pattern.
- **Decorators for cross-cutting concerns.** Wrap use cases with
  logging, metrics, authorization decorators — see
  `design-patterns.md` § Decorator.
