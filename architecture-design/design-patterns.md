# Design Patterns

The 23 GoF patterns are a shared vocabulary. When a reviewer says "this
is basically a Strategy", everyone involved knows the shape being
proposed — interface, pluggable implementations, runtime selection —
without a longer description. That's the point: patterns are names, not
prescriptions.

This reference covers the patterns that actually earn their keep in
DDD + Clean Architecture systems. Patterns that were essentially
workarounds for language limitations (many of GoF's creational patterns
in Java) are noted but not spotlighted; in modern Python and TypeScript
they're often one-liners.

Canonical references: Gamma, Helm, Johnson, Vlissides, *Design
Patterns: Elements of Reusable Object-Oriented Software* (1994); Fowler,
*Patterns of Enterprise Application Architecture* (2002) — domain-side
patterns; Freeman & Robson, *Head First Design Patterns* (2nd ed., 2020)
— accessible introductions. For domain-layer patterns specifically, see
`references/ddd.md`.

---

## Two maxims that outweigh any individual pattern

From the GoF book's introduction, and they are the most quoted lines in
the canon for good reason.

> **Program to an interface, not an implementation.**
>
> **Favor object composition over class inheritance.**

Most "bad pattern usage" traces back to violating one of these. Apply
them first; reach for named patterns second.

---

## Patterns that pull real weight in DDD / Clean systems

### Strategy

Encapsulate a family of algorithms behind a common interface; let the
client choose at runtime. This is the pattern behind most DIP
applications in the application layer — swap the concrete
implementation for tests, for different environments, or for runtime
behavior variations.

```python
class PricingStrategy(Protocol):
    def apply(self, order: Order) -> Money: ...

class StandardPricing:
    def apply(self, order: Order) -> Money: ...

class BlackFridayPricing:
    def apply(self, order: Order) -> Money: ...

# Use case composes a strategy
class PlaceOrder:
    def __init__(self, pricing: PricingStrategy, ...): ...
```

Use whenever behavior varies by context and the variation is worth
naming. If you have only one implementation, skip the pattern.

Ref: GoF, p. 315.

### Observer / Domain Events

In-process "when X happens, notify interested parties". Domain events
are the application of Observer at the domain layer — the aggregate
records an event, handlers react.

**Caution.** Observer is an *in-process, synchronous* pattern. When
handlers live across process boundaries or need durability, reach for
event-driven messaging with a broker (see `event-driven.md`); it's a
different scope and conflating them hides coupling.

Ref: GoF, p. 293.

### Adapter

Make an existing class or API conform to an interface the client
expects. Foundational for the Anti-Corruption Layer and for every
driven adapter in Hexagonal architecture.

```python
# Domain port
class PaymentGateway(Protocol):
    def charge(self, amount: Money) -> ChargeResult: ...

# Adapter over a specific vendor
class StripeAdapter:
    def __init__(self, client: stripe.Client):
        self._client = client

    def charge(self, amount: Money) -> ChargeResult:
        result = self._client.Charge.create(
            amount=int(amount.cents), currency=amount.currency.lower()
        )
        return ChargeResult(success=result["paid"], id=result["id"])
```

Ref: GoF, p. 139.

### Facade

Provide a simplified interface to a complex subsystem. Use cases
themselves are facades over domain operations — they hide the
orchestration (load aggregate, call methods, persist, emit events)
behind a single `execute` call.

Ref: GoF, p. 185.

### Decorator

Attach additional behavior to an object dynamically, without
subclassing. Classic use: cross-cutting concerns around use cases —
logging, caching, authorization, retry.

```python
class LoggingUseCase:
    def __init__(self, inner: UseCase, log: Logger):
        self._inner = inner
        self._log = log

    def execute(self, cmd):
        self._log.info("start", cmd=cmd)
        try:
            result = self._inner.execute(cmd)
            self._log.info("ok")
            return result
        except Exception:
            self._log.exception("failed")
            raise
```

Several decorators can compose: `LoggingUseCase(MetricsUseCase(
AuthzUseCase(PlaceOrder(...))))`. This keeps `PlaceOrder` a pure use
case and cross-cutting concerns orthogonal.

Ref: GoF, p. 175.

### Command

Encapsulate a request as an object. Pairs naturally with the
application layer: every use case takes a `Command` DTO as input. Also
enables queuing, undo, logging, and batching.

```python
@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: CustomerId
    items: tuple[LineItem, ...]
    idempotency_key: str
```

Ref: GoF, p. 233.

### Template Method

Define the skeleton of an algorithm in a base class, defer some steps
to subclasses. Useful when genuinely several variations share a stable
sequence of steps with one or two differences — but Strategy via
composition is usually preferable.

*Prefer Strategy when the variation is behavior; prefer Template Method
only when there's a real is-a relationship and the skeleton is
stable.* Template Method uses inheritance; Strategy uses composition.
GoF's own maxim tips the scale.

Ref: GoF, p. 325.

### Chain of Responsibility

Pass a request along a chain of handlers until one handles it. Useful
for pipelines — validation, middleware, authorization checks, command
processing.

Middleware stacks in web frameworks are Chain of Responsibility in
practice.

Ref: GoF, p. 223.

### Factory Method / Abstract Factory

Encapsulate object creation. In modern Python and TypeScript, a
function is usually enough — but Factory as a *named concept* still
matters when creation logic has business significance (enforcing
invariants, consulting policy) rather than being mechanical.

See `references/ddd.md` § Factories for the domain-side use.

Ref: GoF, p. 107 (Factory Method), p. 87 (Abstract Factory).

### Composite

Compose objects into tree structures; treat individual and composite
objects uniformly. Showing up whenever you have genuine hierarchies —
file systems, DOM trees, organizational trees, group policies.

Ref: GoF, p. 163.

---

## PoEAA patterns often pulled into modern systems

Fowler's *Patterns of Enterprise Application Architecture* catalogs
patterns that sit around the domain — persistence, distribution,
concurrency. A few show up constantly.

### Repository

See `references/ddd.md` § Repositories. One repository per aggregate
root; collection-like interface owned by the domain.

Ref: Fowler, Ch. 18; Evans, Ch. 6.

### Unit of Work

Tracks objects loaded during a business transaction and coordinates the
write of changes (commit) or reverts (rollback). Used by the
application layer to frame transactional boundaries.

```python
class UnitOfWork(Protocol):
    orders: OrderRepository
    def __enter__(self) -> Self: ...
    def __exit__(self, *args) -> None: ...  # rollback by default
    def commit(self) -> None: ...
```

Used as `with uow: ... uow.commit()`. Rollback is the safe default if
`commit()` is not called.

Ref: Fowler, Ch. 11; Percival & Gregory, Ch. 6.

### Specification

See `references/ddd.md` § Specifications.

Ref: Evans, Ch. 9.

### Identity Map

Ensure each aggregate is loaded only once per unit of work. ORMs
(SQLAlchemy's session, TypeORM, Prisma) implement this for you. Worth
knowing the name because it explains ORM behavior that otherwise looks
like magic.

Ref: Fowler, Ch. 11.

### Data Mapper vs Active Record

- **Data Mapper:** a separate object knows how to load and save the
  domain object. Domain stays pure. Preferred in DDD / Clean
  architectures.
- **Active Record:** the domain object itself carries persistence
  methods (`order.save()`). Fine for CRUD-style features, but couples
  the domain to persistence — a Dependency Rule violation for anything
  more serious.

Ref: Fowler, Chs. 10, 12.

---

## Patterns to apply carefully

### Singleton

Almost always a mistake in modern systems. Usually what's wanted is
"one instance wired by the DI container" — which is a lifetime
configuration, not a pattern. Classic Singletons introduce global
state, break testability, and make dependency direction invisible.

**When it's actually fine:** truly global, truly stateless (e.g., a
logger configured at boot). Even then, a module-level instance
registered by the container is cleaner than a class that hides its own
global.

Ref: GoF, p. 127 — but read the critique in any modern design book
after.

### Service Locator

A registry that code queries for dependencies. Looks like DI but
reverses the direction — now every caller knows about the locator, so
dependencies are hidden and untestable in isolation. Constructor
injection is almost always better.

Ref: Fowler, *InversionOfControl* essay (critique).

### Observer across process boundaries

Observer is in-process. When events cross processes — services,
workers — use a message broker and the patterns in `event-driven.md`.
Implementing in-process Observer with threads to simulate cross-service
events reinvents a broken version of a message bus.

---

## Functional-style simplifications

Several GoF patterns are primarily workarounds for Java-era
limitations. In Python and modern TypeScript, lighter alternatives
exist:

- **Strategy** is often just passing a function.
- **Command** is often just a small dataclass or a function +
  arguments captured in a closure.
- **Observer** is `callable[[Event], None]` lists or reactive streams.
- **Iterator** is built into both languages (`__iter__`, `Symbol.iterator`).
- **Template Method** loses ground to Strategy via composition in most
  cases.

Name the pattern when it aids communication ("this is a Decorator
around the use case for logging"). Don't invent a class hierarchy when
a function would do — GoF's own maxim says so.

---

## How to select a pattern (and how not to)

**Signals that a pattern is actually needed:**

1. The same structural problem appears in two or three places.
2. The design evolves predictably along an axis (more algorithms, more
   decorations, more validation steps) — a pattern supports extension
   along that axis.
3. A shared vocabulary would clarify a design doc or a PR description.

**Signals that pattern use is ceremonial:**

1. The pattern is applied with only one implementation.
2. An interface exists with a single method called from a single
   place.
3. Patterns compose into multi-level abstraction that obscures the
   underlying simple behavior.

Patterns are most valuable as recognition tools during review: "this
tangled conditional logic is begging to be a Strategy", "this
cross-cutting logging wants a Decorator". They are least valuable when
imposed up front on code that does not yet have a problem the pattern
solves.

Ref: the *Rule of Three* (Fowler): write it once, write it twice,
refactor to pattern on the third.
