# Clean Architecture

Clean Architecture, Hexagonal / Ports-and-Adapters, Onion Architecture,
and Screaming Architecture are variations on one idea: **organize code
so the business rules do not depend on the delivery mechanism.** You
could swap the web framework, the database, or the message broker and
the domain layer would not notice.

Canonical references: Martin, *Clean Architecture* (2017); Cockburn's
*Hexagonal Architecture* essay (2005); Percival & Gregory, *Architecture
Patterns with Python* (2020) — the clearest practical treatment in
Python.

---

## The Dependency Rule

> Source code dependencies must point only inward, toward higher-level
> policy.
>
> — Martin, *Clean Architecture*, Ch. 22.

This is *the* rule. Everything else follows.

**Concretely:** the domain layer can't import from application. The
application layer can't import from infrastructure. The infrastructure
layer can't be imported by either. If you ever need to go "the wrong
way" — an inner layer needing something an outer layer provides —
define an interface in the inner layer and implement it in the outer
one. This is the Dependency Inversion Principle in action (see
`solid.md` § DIP).

**Enforce in CI.** The rule is easy to violate by accident — an import
slips in during a quick fix. Use:

- Python: [`import-linter`](https://import-linter.readthedocs.io)
  contracts forbidding cross-layer imports.
- TypeScript: [`dependency-cruiser`](https://github.com/sverweij/dependency-cruiser)
  or `eslint-plugin-boundaries`.

A linter failure at PR time is vastly cheaper than a reviewer catching
it at month six.

---

## The four layers

```
┌──────────────────────────────────────────────────────┐
│  Infrastructure / Frameworks / Drivers               │
│  (DB, HTTP framework, message broker, CLI, cache)    │
│  ┌────────────────────────────────────────────────┐  │
│  │  Interface Adapters                            │  │
│  │  (controllers, presenters, gateways, mappers)  │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │  Application (Use Cases)                 │  │  │
│  │  │  (interactors, command/query handlers)   │  │  │
│  │  │  ┌────────────────────────────────────┐  │  │  │
│  │  │  │  Domain (Entities)                 │  │  │  │
│  │  │  │  Business rules + invariants       │  │  │  │
│  │  │  └────────────────────────────────────┘  │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### Domain (innermost)

The business model. Entities, value objects, aggregates, domain events,
domain services, specifications. Knows **nothing** about how it's
persisted, served, or invoked.

- No imports from application, interface, or infrastructure.
- No imports from ORM, HTTP framework, or async runtime.
- `datetime`, `decimal`, `uuid`, `typing`, plain standard library — fine.

Test without anything else loaded.

### Application (use cases)

Orchestrates domain operations to fulfill a single user intent. Each use
case is typically one command or one query.

- Imports from domain.
- Depends on **ports** (interfaces) for external concerns; never on
  concrete infrastructure.
- Encapsulates a transaction boundary. One use case ≈ one unit of work.

```python
# application/place_order.py
class PlaceOrder:
    def __init__(self, orders: OrderRepository, uow: UnitOfWork,
                 events: EventBus):
        self._orders = orders
        self._uow = uow
        self._events = events

    def execute(self, cmd: PlaceOrderCommand) -> OrderId:
        with self._uow:
            order = Order.create(cmd.customer_id, cmd.items)
            self._orders.add(order)
            self._uow.commit()
        for event in order.pull_events():
            self._events.publish(event)
        return order.id
```

Notice: no Flask/FastAPI/Express types. No SQLAlchemy session. No HTTP
request object. The use case is testable without any of them.

### Interface Adapters

Translate between the use case's world (commands, domain objects) and
the outside world (HTTP requests, JSON, database rows).

- **Controllers / presenters:** transform HTTP payloads into commands;
  serialize results back to JSON or templates.
- **Gateways / repository implementations:** implement the ports the
  application layer depends on. SQLAlchemy repository goes here, not in
  the domain.
- **Mappers:** convert between ORM entities and domain objects.

### Infrastructure (outermost)

Everything that could be swapped: the specific database, the specific
HTTP framework, the message broker, the cache, the email provider.
Contains the wiring (dependency injection container) that plugs
adapters into ports.

---

## Ports and Adapters

Ports are **interfaces defined by the inner layer**. Adapters are
**implementations defined by the outer layer**.

Two kinds of ports (Cockburn):

- **Driven / output ports:** the application *drives* these
  outward — repositories, email senders, event publishers. Inner layer
  says "I need to save an Order"; outer layer provides the "how".
- **Driving / input ports:** the application is *driven* by these —
  typically the use case interfaces themselves, invoked by HTTP
  handlers, CLI commands, message consumers.

Pictorially:

```
  HTTP      CLI      Worker      Test harness
    │        │         │               │
    ▼        ▼         ▼               ▼          [driving adapters]
  ┌────────────────────────────────────────┐
  │   INPUT PORTS (use case interfaces)    │
  ├────────────────────────────────────────┤
  │        Application layer               │
  ├────────────────────────────────────────┤
  │   OUTPUT PORTS (repositories, etc.)    │
  └────────────────────────────────────────┘
    │        │         │               │
    ▼        ▼         ▼               ▼          [driven adapters]
   PG       SMTP   Kafka            In-memory
```

### Key properties

- Adding a new way to invoke the system = add a driving adapter. Don't
  touch the domain.
- Swapping the database = swap the driven adapter. Don't touch the
  domain.
- Testing the application layer = plug in in-memory fakes for every
  driven port. Fast, deterministic, framework-free.

Ref: Percival & Gregory, Ch. 2–4 for an extended Python walkthrough;
Martin, Ch. 23–24.

---

## DTOs at every boundary

A **Data Transfer Object** is a dumb, serializable structure whose job
is to cross a boundary. Never leak ORM entities or domain objects
outside their layer.

**Why:** domain objects carry behavior and invariants that have no
meaning outside the domain. Serializing them to JSON accidentally
exposes internal state. Letting a controller hold a domain object
invites the controller to invoke methods it shouldn't.

**Where DTOs appear:**

- HTTP request → `PlaceOrderRequest` DTO → translated to
  `PlaceOrderCommand` inside the controller.
- Use case result → `OrderView` DTO → serialized to JSON.
- ORM row → `OrderRecord` → mapped to `Order` domain aggregate inside
  the repository adapter.

Pydantic (Python) and Zod (TypeScript) are common DTO toolkits.
Pydantic v2: `model_config = ConfigDict(frozen=True)` to forbid mutation
after construction.

---

## Testability as a litmus test

If you can't test your use cases without starting a web server or a
database, the Dependency Rule has been violated somewhere. The
symptoms:

- Tests need to boot Flask / FastAPI / Express / Nest.
- Tests need a running Postgres / MySQL / Redis.
- Tests need fixtures that mirror the ORM schema.

A well-layered system runs application-layer tests in memory with in-
memory fakes. They execute in milliseconds. The database gets its own
integration tests *separately*, verifying that the adapter correctly
maps between rows and aggregates.

Ref: Percival & Gregory, Ch. 5; Freeman & Pryce, *Growing Object-
Oriented Software, Guided by Tests*.

---

## Layer variants — same idea, different diagrams

The literature has several names for overlapping ideas. All rest on the
Dependency Rule.

| Variant | Key emphasis | Source |
|---|---|---|
| Hexagonal / Ports & Adapters | symmetry of driving vs driven sides | Cockburn, 2005 |
| Onion Architecture | concentric rings with domain at the center | Palermo, 2008 |
| Clean Architecture | Martin's synthesis; adds use case layer explicitly | Martin, 2017 |
| Screaming Architecture | top-level packages should reveal the domain, not the framework | Martin, 2011 |

Pick one vocabulary for the project and stay consistent. The specifics
matter less than the dependency discipline.

**Screaming Architecture test.** Look at the top-level folder of the
repo. Does it say `accounts/`, `orders/`, `invoicing/` — or does it say
`controllers/`, `models/`, `views/`? The first screams the domain; the
second screams the framework. The first is Clean.

---

## Putting it together: a Python repo layout

```
src/
├── orders/                     # bounded context
│   ├── domain/                 # innermost
│   │   ├── aggregates.py       # Order aggregate
│   │   ├── value_objects.py    # Money, LineItem, etc.
│   │   ├── events.py           # OrderPlaced, OrderShipped
│   │   ├── services.py         # rare domain services
│   │   └── ports.py            # OrderRepository Protocol, etc.
│   ├── application/            # use cases
│   │   ├── place_order.py
│   │   ├── ship_order.py
│   │   └── commands.py         # PlaceOrderCommand dataclasses
│   ├── adapters/               # interface adapters
│   │   ├── http.py             # FastAPI controller
│   │   ├── repositories.py     # SQLAlchemy implementation
│   │   └── mappers.py
│   └── infrastructure/         # outermost
│       ├── db.py               # SQLAlchemy setup
│       └── container.py        # DI wiring
└── shared/
    └── …
```

And in TypeScript:

```
src/
├── orders/
│   ├── domain/
│   │   ├── order.ts
│   │   ├── money.ts
│   │   ├── events.ts
│   │   └── ports.ts
│   ├── application/
│   │   ├── placeOrder.ts
│   │   └── commands.ts
│   ├── adapters/
│   │   ├── http/
│   │   ├── repositories/
│   │   └── mappers/
│   └── infrastructure/
│       ├── db.ts
│       └── container.ts
```

---

## Common violations and fixes

**Violation:** `from django.db import models` inside the domain layer.
**Fix:** the domain aggregate is plain Python. The ORM entity is a
separate class in the adapter. A mapper converts between them at the
repository boundary.

**Violation:** the use case receives an HTTP request object.
**Fix:** the controller extracts fields and constructs a command DTO.
The use case never sees HTTP types.

**Violation:** the application layer imports `requests` to call an
external API.
**Fix:** the application defines a `PaymentGateway` port. An adapter in
infrastructure implements it using `requests`. The use case depends on
the port only.

**Violation:** the domain knows about the database transaction ("I'll
save myself when you call `.persist()`").
**Fix:** domain objects do not know about persistence. The use case
drives the Unit of Work, which commits the aggregate through the
repository.

**Violation:** 80% of tests require a running database.
**Fix:** introduce in-memory fake repositories implementing the same
Protocol. Use them for the application-layer tests. Keep a small set
of integration tests for the real adapter.

---

## When simpler layering is fine

Not every project needs four rings. A small CLI, a scheduled job, a
prototype — these thrive on a flatter structure. Khononov and Martin
both acknowledge this. The Dependency Rule is valuable at any scale, but
the number of layers scales with the complexity of the core subdomain.

A reasonable gradient:

- **CRUD admin panel**: a single layer is fine; use a framework ORM
  directly.
- **Feature with some rules**: two layers (domain + infrastructure).
- **Core subdomain with nontrivial invariants**: full four-layer
  clean architecture.

Choose deliberately. Under-engineering is as much a design choice as
over-engineering; both have costs.
