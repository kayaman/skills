# Python Idioms for Architecture & Design (3.12+)

Modern Python — 3.12 and later — has every primitive needed to express
DDD, Clean Architecture, SOLID, and the patterns in idiomatic code with
no framework required. This reference shows the specific constructs
that map best to each design concept.

Tested against Python 3.12, 3.13, and 3.14. Notes on pre-3.12 fallbacks
where relevant.

Canonical references: Ramalho, *Fluent Python* (2nd ed., 2022);
Percival & Gregory, *Architecture Patterns with Python* (2020).

---

## Value Objects

Frozen dataclasses are the default. `slots=True` saves memory and
prevents accidental attribute assignment.

```python
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
            raise ValueError(f"Cannot add {self.currency} to {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, n: Decimal | int) -> "Money":
        return Money(self.amount * Decimal(n), self.currency)
```

**Key points:**

- `frozen=True` — no `__setattr__`, enforces immutability.
- `slots=True` — blocks new attributes, saves ~40% memory per instance.
- `__post_init__` — validates invariants after dataclass-generated
  `__init__` runs.
- `__eq__` and `__hash__` come for free from `frozen=True`.
- Operations return *new* instances. No mutation.

**For more complex value objects** where you need richer validation
(nested structures, custom serializers), Pydantic v2 is a good fit at
layer boundaries (DTOs). Keep it out of the pure domain if you can —
it's a big dependency, and domain objects benefit from being plain.

### Newtype and brands for IDs

A bare `str` for `UserId` loses type safety — any string is assignable
to the parameter. Use `NewType` for compile-time distinction:

```python
from typing import NewType
from uuid import UUID

UserId = NewType("UserId", UUID)
OrderId = NewType("OrderId", UUID)

def ship_order(order_id: OrderId) -> None: ...

user = UserId(UUID("..."))
ship_order(user)  # type checker: error — expected OrderId, got UserId
```

---

## Entities

Entities have identity and mutable state, protected by methods.

```python
from dataclasses import dataclass, field
from uuid import UUID, uuid4

@dataclass(eq=False, slots=True)  # eq by identity, not attributes
class Order:
    id: UUID
    customer_id: UUID
    _items: list["LineItem"] = field(default_factory=list)
    _status: str = "draft"
    _events: list["DomainEvent"] = field(default_factory=list)

    @classmethod
    def create(cls, customer_id: UUID, items: list["LineItem"]) -> "Order":
        if not items:
            raise ValueError("Order requires at least one line item")
        order = cls(id=uuid4(), customer_id=customer_id, _items=list(items))
        order._events.append(OrderPlaced(order_id=order.id,
                                         customer_id=customer_id))
        return order

    def ship(self) -> None:
        if self._status != "paid":
            raise ValueError("Cannot ship unpaid order")
        self._status = "shipped"
        self._events.append(OrderShipped(order_id=self.id))

    def pull_events(self) -> list["DomainEvent"]:
        events, self._events = self._events, []
        return events

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Order) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

**Key points:**

- `eq=False` disables attribute-based equality — define by identity.
- No public setters. `ship()` is intent-named; it encodes a rule.
- Events queue inside the aggregate; the use case pulls them after a
  successful transaction.
- `@classmethod create(...)` for creation with invariants.

### `@override` for LSP safety

```python
from typing import override

class Base:
    def greet(self) -> str:
        return "hello"

class Sub(Base):
    @override
    def greet(self) -> str:
        return "hi"
```

`@override` (PEP 698, 3.12+) makes the intent explicit and lets type
checkers flag typos in the method name — catching silent LSP drift.
Apply it everywhere you intend to override.

---

## Ports with `Protocol`

Structural typing fits ISP naturally: implementations don't need to
inherit the Protocol. They satisfy it by having the right methods.

```python
from typing import Protocol, runtime_checkable

class OrderRepository(Protocol):
    def get(self, order_id: OrderId) -> Order: ...
    def add(self, order: Order) -> None: ...
```

An in-memory test fake and the SQLAlchemy implementation both satisfy
this without inheriting from `OrderRepository`. You can still inherit
explicitly for documentation purposes; structural typing is the default.

**When to use `abc.ABC` instead.** When you need shared concrete
behavior in the base class (a template method with some hooks), use
ABC — Protocol is about structure, not inheritance. The two solve
different problems.

**`runtime_checkable`** is optional. It enables `isinstance(x, Protocol)`
checks but bypasses strict typing. Use sparingly.

---

## Dependency injection

Python doesn't need a DI container. Constructor injection is enough and
is the clearest expression of DIP.

```python
class PlaceOrder:
    def __init__(
        self,
        orders: OrderRepository,
        uow: UnitOfWork,
        events: EventBus,
        clock: Callable[[], datetime] = datetime.utcnow,
    ) -> None:
        self._orders = orders
        self._uow = uow
        self._events = events
        self._clock = clock

    def execute(self, cmd: PlaceOrderCommand) -> OrderId:
        with self._uow:
            order = Order.create(cmd.customer_id, cmd.items)
            self._orders.add(order)
            self._uow.commit()
        for event in order.pull_events():
            self._events.publish(event)
        return order.id
```

Wiring happens once at startup in a composition root (`infrastructure/
container.py`). If you need more machinery, `dependency-injector` and
`punq` are established libraries; don't reach for them until manual
wiring becomes cumbersome.

---

## DTOs at layer boundaries

Pydantic v2 is the de facto standard for HTTP/JSON DTOs.

```python
from pydantic import BaseModel, ConfigDict, Field

class PlaceOrderRequest(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)

    customer_id: UUID
    items: list["LineItemDTO"] = Field(min_length=1)

class LineItemDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    sku: str
    quantity: int = Field(gt=0)
    unit_price_cents: int = Field(gt=0)
```

**Why here, not in the domain:**

- Pydantic is a heavy dependency; the domain stays light.
- DTOs are shaped for transport; domain objects are shaped for
  behavior. They legitimately differ.
- Validation errors at the boundary are distinct from domain invariant
  violations inside.

---

## Pattern matching for polymorphic dispatch

`match` (PEP 634, 3.10+) is a better fit than `isinstance` chains when
branching on event types or command types.

```python
def apply_event(state: AggregateState, event: DomainEvent) -> AggregateState:
    match event:
        case OrderPlaced(order_id=oid, items=items):
            return state.with_order(oid, items, status="placed")
        case OrderShipped(order_id=oid):
            return state.with_status(oid, "shipped")
        case OrderCancelled(order_id=oid, reason=r):
            return state.with_status(oid, "cancelled")
        case _:
            raise ValueError(f"Unknown event: {type(event).__name__}")
```

Pair with `@dataclass(frozen=True)` for event types to get clean
structural matching.

---

## Self type for fluent APIs

`Self` (PEP 673, 3.11+) makes builder/fluent patterns return the
correct subtype without manual generics.

```python
from typing import Self

class QueryBuilder:
    def where(self, cond: str) -> Self:
        # returns the correct subtype for subclasses
        ...
```

---

## The domain events side of Unit of Work

Percival & Gregory's pattern: aggregates collect events, the unit of
work drains them on commit and dispatches.

```python
class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: Callable[[], Session],
                 bus: EventBus):
        self._session_factory = session_factory
        self._bus = bus
        self.orders: OrderRepository | None = None

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self.orders = SqlAlchemyOrderRepository(self._session)
        return self

    def __exit__(self, *exc) -> None:
        self._session.close()

    def commit(self) -> None:
        events = self._collect_new_events()
        self._session.commit()
        for event in events:
            self._bus.publish(event)

    def _collect_new_events(self) -> list[DomainEvent]:
        events = []
        for aggregate in self.orders.seen:
            events.extend(aggregate.pull_events())
        return events
```

Event dispatch *after* commit guards against publishing events for a
transaction that ultimately rolls back.

---

## Python 3.13+ specifics

- **Free-threaded build** (experimental, 3.13+). If enabled, the GIL
  is disabled. Implications for aggregate concurrency: your in-process
  locks now actually matter; use `threading.Lock` where you previously
  relied on GIL ordering. Still experimental; test carefully.
- **JIT compiler** (experimental, 3.13+). Doesn't change design
  choices, but improves runtime performance enough that Python's
  "performance too low for this" objections are softening in several
  domains.
- **Better REPL** (3.13+). Use `python -i` for quick aggregate
  experiments during design.

---

## Testing domain and application layers

A well-layered Python codebase tests the domain and application layers
**without** any framework or database. `pytest` + in-memory fake
repositories is the pattern:

```python
class FakeOrderRepository:
    def __init__(self):
        self._orders: dict[UUID, Order] = {}
        self.seen: set[Order] = set()

    def get(self, order_id: OrderId) -> Order:
        order = self._orders[order_id]
        self.seen.add(order)
        return order

    def add(self, order: Order) -> None:
        self._orders[order.id] = order
        self.seen.add(order)

def test_place_order_emits_event():
    orders = FakeOrderRepository()
    uow = FakeUnitOfWork(orders=orders)
    events = FakeEventBus()
    use_case = PlaceOrder(orders, uow, events)

    cmd = PlaceOrderCommand(customer_id=..., items=[...])
    use_case.execute(cmd)

    assert any(isinstance(e, OrderPlaced) for e in events.published)
```

Tests that run in milliseconds give fast feedback. Integration tests
(real DB, real broker) exist separately and run less often.

---

## Linting architectural boundaries

Use [`import-linter`](https://import-linter.readthedocs.io/) to enforce
the Dependency Rule in CI:

```ini
# setup.cfg or pyproject-compatible config
[importlinter]
root_packages = orders

[importlinter:contract:layers]
name = Dependency Rule for orders
type = layers
layers =
    orders.adapters
    orders.application
    orders.domain
```

A PR that introduces `from orders.adapters import …` inside
`orders.domain` fails lint. This is cheap insurance.

---

## Common Python-specific anti-patterns

**Using `dict` as a domain object.** `{"customer_id": ..., "status":
"placed"}` floating through the application layer. No types, no
invariants, no auto-completion. Use a dataclass.

**Anemic `class` with only `__init__`.** You've written a C struct.
Move behavior onto the class.

**`isinstance` in business logic.** Usually a hint that you should
either use `match` or split into a separate type with a clearer
interface.

**Importing SQLAlchemy in the domain layer.** Mixing persistence
concerns with domain logic. Use a separate ORM-mapped class in the
adapter and a mapper.

**Global state via `import` side effects.** A module that opens a DB
connection at import time. Makes testing awful. Move to an explicit
setup function called at app startup.
