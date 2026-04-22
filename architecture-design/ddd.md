# Domain-Driven Design

Domain-Driven Design has two halves. **Strategic DDD** is about carving
the system along lines that match the business; **Tactical DDD** is about
expressing each bounded context in code that the domain expert would
recognize. Get the strategic part wrong and no amount of tactical polish
will save the design.

Canonical references throughout: Evans, *Domain-Driven Design* (2003) —
the blue book; Vernon, *Implementing Domain-Driven Design* (2013) — the
red book; Khononov, *Learning Domain-Driven Design* (2021) — the modern
synthesis.

---

## Strategic DDD

### Ubiquitous language

A shared vocabulary between developers and domain experts, used
consistently in conversation, diagrams, and **code**. If the domain
expert says "Member", the class is `Member`, not `User`. If they say
"recognize revenue", the method is `recognize_revenue`, not
`compute_total_after_invoice`.

**Anti-pattern: translation layer in the brain.** Developers
mentally translate between "business speak" and "tech speak" every time
they read the code. This drift compounds and surfaces as bugs where the
code contradicts the business rule because nobody noticed the
divergence. Ref: Evans, Ch. 2.

**Test:** read a method name aloud to the domain expert. If they would
phrase it differently, the name is wrong.

### Subdomains

Not every part of the business deserves the same investment. Classify:

| Subdomain | Characteristics | Strategy |
|---|---|---|
| **Core** | competitive advantage; complex, changes often | invest heavily; DDD pays off here |
| **Supporting** | custom but not differentiating | simpler design; still custom |
| **Generic** | solved commodity problem (auth, payments) | buy or integrate; do not build |

Ref: Khononov, Ch. 3; Evans, Part IV.

### Bounded contexts

A bounded context is an explicit boundary inside which a model applies
with a single, consistent meaning. Outside the boundary, the same word
can mean something different.

*Classic example:* `Customer` in the Sales context carries lead score,
preferred contact, pipeline stage. `Customer` in the Billing context
carries tax ID, credit limit, payment terms. Same English word, two
models, two implementations, two lifecycles. Forcing them into one
shared class creates a god object that serves neither team.

**Heuristics for finding context boundaries:**

- Different teams or language usage → likely different contexts.
- Different lifecycles or change rates → likely different contexts.
- A noun appears in two use cases with materially different attributes
  → likely different contexts.
- Team autonomy and deployment independence desired → must be
  different contexts.

### Context mapping

How contexts relate. Name the relationship — implicit integration is
where coupling accumulates unnoticed. Ref: Evans, Ch. 14; Vernon, Ch. 3.

- **Shared Kernel:** two teams share a small model, coordinate changes.
  High coupling; use sparingly.
- **Customer–Supplier:** upstream team serves downstream; downstream's
  needs influence upstream's roadmap.
- **Conformist:** downstream accepts upstream's model as-is (when
  upstream is external or dominant).
- **Anticorruption Layer (ACL):** downstream translates upstream's
  model into its own. **Default this when integrating with legacy
  systems or external APIs.**
- **Open Host Service:** upstream publishes a protocol any consumer can
  conform to (a public API).
- **Published Language:** a well-documented shared format (OpenAPI
  schema, AsyncAPI, event schema registry).
- **Separate Ways:** two contexts share nothing — fine when integration
  cost exceeds benefit.

**Gotcha.** Missing an ACL against an external system is the #1 way
external schema changes cascade into your domain. Always wrap.

---

## Tactical DDD

Inside a bounded context, these are the building blocks. The order below
reflects the design sequence — start with the aggregate.

### Value Objects

Immutable, defined by attributes (not identity), replaceable as a whole.
Examples: `Money(amount, currency)`, `DateRange(start, end)`, `Email`,
`Coordinates(lat, lng)`.

**Why they matter:** value objects eliminate a huge class of bugs.
`Money` that enforces currency matching at construction prevents the
"add USD to EUR" bug. `Email` that validates at construction prevents
malformed emails from propagating.

**Rules:**

- Immutable (frozen). Any "change" returns a new instance.
- Equality by attribute, not by reference.
- Self-validating at construction. Invariants are type-level facts.
- No identity. Two `Money(10, USD)` values are interchangeable.

Ref: Evans, Ch. 5; Vernon, Ch. 6.

See `references/python.md` § Value Objects and
`references/typescript.md` § Value Objects for idiomatic code.

### Entities

Objects with identity and a lifecycle. Two `Order` objects with
identical attributes are still different orders if their IDs differ.

**Rules:**

- Identity established at creation, immutable thereafter.
- Equality by ID, not by attribute.
- Methods protect invariants; state is never mutated through a public
  setter.

### Aggregates

An aggregate is a cluster of entities and value objects with a single
**aggregate root** that acts as the gatekeeper. Outside code references
the aggregate only through the root. The aggregate is the boundary for
invariants, transactions, and concurrency.

**The four aggregate rules** (Vernon, Ch. 10):

1. **Model true invariants in consistency boundaries.** Put things in the
   same aggregate only if they must change together to maintain an
   invariant. "Order total equals sum of line items" → same aggregate.
   "Customer's preferred color" → separate aggregate.
2. **Design small aggregates.** Ideal: a root entity with a handful of
   value objects. Large aggregates serialize concurrent updates and
   increase contention.
3. **Reference other aggregates by identity only.** Use
   `customer_id: CustomerId`, not a loaded `Customer` object. The
   alternative drags entire object graphs into memory and creates
   implicit transactional coupling.
4. **Update one aggregate per transaction.** If two aggregates must be
   updated together, use an **eventual consistency** mechanism — a
   domain event that triggers the second update in a new transaction.

**Common anti-patterns:**

- *Aggregate that owns everything:* `Customer` aggregate containing
  orders, invoices, addresses, preferences. Concurrent updates to
  unrelated things block each other. Split by invariant.
- *Repository per entity:* you get a `LineItemRepository`, which leaks
  child entities as if they were aggregates. There is one repository
  per aggregate root; child entities are reached through the root.

### Domain events

Something that happened in the domain that the business cares about.
Past-tense, named from the business's perspective.

- ✅ `OrderPlaced`, `PaymentRefunded`, `InventoryReserved`
- ❌ `UpdateOrder`, `DatabaseWriteCompleted`, `HandleClick`

**Facts about the past**, never rejectable. Commands can be rejected
("place this order" — no, out of stock). Events cannot ("order was
placed" — it's already in the log). Mixing the two is a frequent
source of subtle bugs; event-driven.md goes deeper.

**Use domain events to:**

- Decouple side effects from the aggregate's core logic ("when an order
  is placed, send email" — the `Order` aggregate shouldn't know about
  email).
- Communicate across aggregates within a bounded context (preserves the
  one-aggregate-per-transaction rule).
- Communicate across bounded contexts (usually through an outbox →
  message broker).

### Domain services

When an operation does not naturally belong to any entity or value
object — it coordinates several of them. Keep rare. Most code belongs on
entities and value objects (behavior-rich model), not in services.

Classic example: transferring money between two accounts. Neither
account "owns" the transfer. A `TransferService` orchestrates.

**Warning sign:** if your domain layer is mostly services with anemic
entities, you have a procedural design wearing an OO hat. Move behavior
onto the entity that holds the relevant data. Ref: Fowler's
*AnemicDomainModel* essay.

### Repositories

Collection-like interface for accessing aggregates, abstracted from the
persistence mechanism. The domain defines the port; infrastructure
provides the adapter.

```python
# Domain layer — owns the contract
class OrderRepository(Protocol):
    def get(self, order_id: OrderId) -> Order: ...
    def add(self, order: Order) -> None: ...
    def find_by_customer(self, customer_id: CustomerId) -> list[Order]: ...
```

**Rules:**

- One repository per aggregate root.
- Returns fully-reconstructed aggregates, not partial data.
- No leaking ORM types in the signature — take and return domain
  objects only.
- Queries that span aggregates belong elsewhere (a CQRS query model or
  a read-side service), not on the repository.

### Factories

Encapsulate complex aggregate creation — enforcing invariants that
cannot be expressed in a constructor alone (multi-step validation,
cross-aggregate lookups, policy decisions).

Trivial creation does not need a factory; just use the constructor.
Reach for a factory when creation logic itself has business
significance.

Ref: Evans, Ch. 6.

### Specifications

Encapsulate a business rule as a predicate. Useful for reusing the same
rule in validation, querying, and selection.

```python
@dataclass(frozen=True)
class EligibleForDiscountSpec:
    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.total_spend > Money(1000, "USD") \
            and customer.member_since < date.today() - timedelta(days=365)
```

Use sparingly. For simple predicates, a named method on the entity is
clearer.

---

## Putting it together: the design sequence

When designing a new bounded context, follow this order. Skipping is
possible; the steps earlier in the sequence just become implicit
decisions that later steps must assume.

1. **Language.** Sit with the domain expert and capture the core
   vocabulary. Two nouns that sound similar but behave differently are
   usually in different contexts.
2. **Context boundary.** Name the context. What is in, what is out?
3. **Aggregates.** For each core noun, ask: *what invariant does this
   protect?* That invariant is the aggregate boundary. If no invariant
   exists, it may not be an aggregate — it may be a value object or a
   read model.
4. **Commands and events.** For each aggregate, list the commands it
   accepts and the events it produces. This is the aggregate's
   behavioral contract.
5. **Repositories.** One per aggregate root. Sketch the few methods
   actually needed — usually `get`, `add`, and a small number of
   domain-named queries. Resist adding methods speculatively.
6. **Use cases.** Thin orchestration: load aggregates, call domain
   methods, persist, emit events. Use cases live in the application
   layer (see `clean-architecture.md`).

---

## Common violations and fixes

**Violation:** `User` class with 47 public setters and no behavior.
**Fix:** identify the invariants currently enforced in services. Move
the methods onto the entity. Remove setters — replace with intent-named
methods (`Order.ship()`, not `Order.setStatus("shipped")`).

**Violation:** a transaction updates two aggregates.
**Fix:** the first aggregate publishes a domain event; a handler (in a
new transaction) updates the second. If the system cannot tolerate
eventual consistency here, the aggregate boundary is wrong — merge or
redraw.

**Violation:** ORM entities leak through the service layer into HTTP
handlers.
**Fix:** introduce DTOs at the application layer boundary. Translate
domain → DTO on output, DTO → commands on input.

**Violation:** `Customer` in Sales and Billing share a class and
database table.
**Fix:** split into two classes in two bounded contexts. Integrate via
events (`CustomerRegistered` from Sales consumed by Billing) or an ACL.

**Violation:** `XxxService` classes contain all the business logic;
entities are data bags.
**Fix:** for each service method, ask "which entity's state is this
mutating?" — move the method there. Services remain only for true
multi-entity orchestration.

---

## When DDD is overkill

Not every system deserves full DDD. Khononov (Ch. 3) draws a clean
line: apply tactical DDD fully in **core subdomains**; use lighter
approaches (transaction scripts, active record, straightforward CRUD)
in **supporting** and **generic** subdomains.

*Transaction Script* (Fowler, PoEAA Ch. 9): a procedural function per
use case. Fine for a simple reporting endpoint.

*Active Record* (Fowler, PoEAA Ch. 10): entity carries its own
persistence. Fine for CRUD-heavy admin panels with no domain logic.

Using heavyweight DDD on a CRUD admin panel is overengineering; using
transaction scripts in a core subdomain with nontrivial invariants is
under-engineering. Match the technique to the subdomain.
