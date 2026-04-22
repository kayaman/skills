# Event-Driven Architecture

Event-driven architecture (EDA) refers to systems where components
communicate primarily by emitting and reacting to events rather than
invoking each other directly. It's attractive for the same reason it's
treacherous: decoupling in time, space, and synchrony comes with new
classes of failure that synchronous systems don't have.

This reference covers three distinct ideas often conflated:

1. **Event-driven architecture** — services integrate via events.
2. **Event sourcing** — state is reconstructed from an append-only log
   of events.
3. **CQRS** — read and write models are separated.

Each is independent. You can use any one without the others. Mixing
them up is the most common source of overengineered systems.

Canonical references: Hohpe & Woolf, *Enterprise Integration Patterns*
(2003); Richardson, *Microservices Patterns* (2018); Vernon, *IDDD*
(2013) — for domain events specifically; Fowler's *Event Sourcing* and
*CQRS* essays; Bellemare, *Building Event-Driven Microservices* (2020).

---

## Three things, three decisions

### Domain events (in-process, within one context)

Objects representing something significant that happened in the
business. Raised by aggregates, handled in the same bounded context,
often synchronously (same transaction) or in a deferred handler within
the same process.

Covered in `ddd.md` § Domain Events. Use for:

- Decoupling side effects inside a context ("when order placed, update
  loyalty points").
- Keeping one-aggregate-per-transaction while still coordinating.

### Integration events (cross-context, cross-process)

Events that cross bounded contexts or service boundaries. Typically
delivered through a message broker (Kafka, RabbitMQ, SNS/SQS, NATS).

- Domain events are internal implementation detail of a bounded
  context.
- Integration events are part of the context's public contract.
- The two are usually *different shapes*. Translate at the outbox.

### Event-sourced aggregates

Aggregates whose state is the fold of a sequence of events. The events
are the source of truth; current state is derived. Very different thing
from the above.

---

## Commands vs events — the foundational distinction

| Aspect | Command | Event |
|---|---|---|
| Mood | imperative | past tense |
| Name | `PlaceOrder` | `OrderPlaced` |
| Outcome | can be rejected | cannot — it already happened |
| Coupling | sender knows the handler | emitter does not know consumers |
| Cardinality | exactly one handler | zero or more |

Every message in the system should be classifiable as one or the other.
If a message is "sort of a command, sort of an event", the design is
ambiguous. Split it or rename it. This distinction drives who is
responsible, how retries work, and whether versioning is additive or
breaking.

Ref: Vernon, Ch. 8; Richardson, Ch. 4.

---

## The outbox pattern

The single most important pattern for reliable event-driven systems.

**Problem:** when an aggregate is saved and an event is published, you
have two writes: one to the database, one to the broker. These can
fail independently. Without care, you get lost events (DB committed,
broker unreachable) or phantom events (broker succeeded, DB rolled
back).

**Solution.** Write the event to an `outbox` table in the same
transaction as the aggregate. A separate process polls or streams the
outbox and publishes to the broker, marking rows as published.

```
┌──────────────┐
│ Transaction  │
│  • save Order│
│  • insert    │──▶  DB committed atomically
│    outbox row│
└──────────────┘
                    ┌──▶ Relay/CDC process ──▶ Broker ──▶ Consumers
                    │    (at-least-once)
          outbox ───┘
```

Guarantees **at-least-once** delivery. Consumers must be idempotent
(see below).

Ref: Richardson, Ch. 3; Percival & Gregory, Ch. 12.

---

## Idempotency — the other non-negotiable

In any event-driven system worth the name, consumers will receive
duplicates. Brokers retry, relays retry, operators replay logs. Every
consumer must be idempotent.

**Strategies:**

- **Deterministic effect:** the handler produces the same state
  regardless of how many times it runs (`setStatus("shipped")` — fine
  if only shipped matters, not a counter increment).
- **Dedup by message ID:** store processed message IDs; skip
  duplicates.
- **Idempotency key from the source:** the producer includes a stable
  key; consumers track which keys they've applied.

Ref: Hohpe & Woolf, *Idempotent Receiver*.

---

## Ordering and partitioning

Global ordering across a distributed system is expensive. Most brokers
(Kafka, Kinesis) offer per-partition ordering. Pick a partition key
that matches your ordering needs — usually the aggregate ID. All events
for the same aggregate land on the same partition, preserving order;
events for different aggregates can interleave freely.

Common mistake: no partition key at all → events arrive in unpredictable
order → consumer logic breaks under load. Always partition by the
thing whose history matters.

---

## Event schema evolution

The hardest part of EDA. Once an event is published, consumers start
depending on its shape. You cannot freely change it.

**Rules of the road:**

- **Versioning from day one.** Include a `schema_version` field or use
  a registry (Confluent Schema Registry, JSON Schema, Avro).
- **Additive changes are safe:** add new optional fields, do not remove
  or rename existing ones.
- **Breaking changes require new event types** (`OrderPlaced` →
  `OrderPlacedV2`), with a transition period where both are emitted
  and consumers migrate.
- **Upcasters.** Translate old event formats to the current shape on
  read. Crucial for event-sourced systems.

Ref: Bellemare, Ch. 7; Greg Young, *Versioning in an Event Sourced
System*.

---

## CQRS

Separate the model used for commands (writes) from the model used for
queries (reads). Different needs, different shapes.

**Canonical motivation.** The write model is an aggregate with
invariants — small, consistent, transactional. The read model serves
UI queries — denormalized, joined, fast to read, possibly spanning
aggregates. Optimizing the same model for both makes both mediocre.

**Minimal CQRS** (without event sourcing):

```
              ┌─ commands ─▶ Write model ──▶ DB
Request ──▶   │                                │
              │                                │
              └─ queries ──▶ Read model ◀────── (populated by
                                                 domain events or
                                                 view materializers)
```

**When CQRS is worth it:**

- Read and write patterns differ drastically in volume or shape.
- Reporting or list views must join across aggregates.
- You want to scale reads independently.

**When it isn't:**

- CRUD apps where the query returns the same shape you wrote.
- Systems with low load and simple reads.

CQRS has a cost — two models to maintain, synchronization lag, more
moving parts. Default to a single model; adopt CQRS when pressure
actually exists.

Ref: Young's original essay; Vernon, Ch. 4.

---

## Event sourcing

Persist an append-only log of events as the source of truth; derive
current state by replaying. Every state change is an event.

```python
class Order:
    def __init__(self, history: Iterable[Event]):
        self._events: list[Event] = []
        for e in history: self._apply(e)

    def place(self, items, customer_id):
        self._validate(items)
        self._raise(OrderPlaced(order_id=..., items=items, ...))

    def _raise(self, event):
        self._apply(event)
        self._events.append(event)

    def _apply(self, event: Event):
        match event:
            case OrderPlaced() as e: self._status = "placed"; ...
            case OrderShipped() as e: self._status = "shipped"; ...
```

**Benefits:**

- Complete audit history, free.
- Temporal queries ("what was the state at T?") are possible.
- Natural fit for event-driven integration — you're already producing
  events.

**Costs:**

- Schema evolution is non-negotiable (every old event must be
  replayable).
- Projections (read models) must be rebuildable from scratch.
- Cognitive overhead — new team members take longer to onboard.
- Snapshotting is required for long aggregates to keep load times
  reasonable.

**When to adopt.** When audit, history, or time-travel is a business
requirement — financial ledgers, regulatory compliance, collaborative
editing. **Not** because "events are cool". Ref: Young; Fowler's
*Event Sourcing* essay.

---

## Sagas and process managers

When a business process spans multiple aggregates or services with no
distributed transaction available, use a **saga**. Each step has a
compensating action to run if a later step fails.

**Two flavors:**

- **Choreography.** Services react to each other's events without a
  central coordinator. Simple for small flows; devolves into
  "event spaghetti" for long ones. No single place to see the whole
  process.
- **Orchestration.** An explicit orchestrator (process manager) drives
  the flow, sending commands and awaiting events. Easier to reason
  about; a single failure domain.

**Heuristic.** If the process has more than 3 steps or any compensating
action, use an orchestrator. Choreography is fine for simple fan-out
("order placed → send email, update inventory, schedule pickup" — three
independent reactors, no coordination needed).

Ref: Richardson, Ch. 4; Hohpe & Woolf, *Process Manager*.

---

## EDA anti-patterns (top of the list during reviews)

**Event as disguised RPC.** The sender emits `GetCustomer` and waits
for `CustomerReturned`. It's a sync call wearing async clothes. Just
use RPC.

**Event carrying a command.** `OrderPlaced` handler is supposed to
charge payment. But *should* it? Events shouldn't contain "things to
do" — they report what happened. If the business policy is "charge on
order placed", that's a separate rule, expressed as a handler
subscribing to `OrderPlaced` that issues the `ChargePayment` command.

**Missing outbox.** Events are published inside the same function that
writes to the DB, without the outbox pattern. You have a dual-write
problem; events will be lost on failures. Fix urgently.

**Non-idempotent consumer.** Writes aren't dedup-keyed. Duplicates will
break things. Fix before it becomes a production incident.

**Implicit choreography for complex flows.** Five services fan events
around with no overview. Reach for orchestration + a dedicated saga.

**Events as storage abstraction leak.** `UserRowInserted` is a CDC
detail, not a domain event. Publishing it means every consumer now
depends on your schema. Translate at the outbox.

**Shared event schemas across contexts.** One team owns the `User`
event and other teams break when it evolves. Treat integration events
as a published language with versioning and a contract.

---

## Messaging topology choices

| Pattern | When | Caveat |
|---|---|---|
| **Publish-Subscribe** | broadcast facts, many consumers | consumers must not assume order of subscription |
| **Point-to-Point (queue)** | work distribution, one consumer per message | competing consumers; ordering lost unless single consumer |
| **Competing Consumers** | scale a single logical consumer horizontally | partition by key to preserve ordering per entity |
| **Request-Reply** | need a response | you have invented RPC; consider whether async messaging was needed at all |
| **Routing / Content-Based** | broker routes messages to queues by content | adds operational complexity; push routing to consumers when possible |

Ref: Hohpe & Woolf, Parts II–IV.

---

## Putting it together: decision tree

```
Does the sender need a reply?
 ├── Yes: Use synchronous RPC (REST, gRPC). Do not fake it with events.
 └── No:
     Is the message an intention that could be rejected?
      ├── Yes: Command → send to a known single handler.
      └── No:  Event → publish, don't know or care who consumes.

Within the event branch:
 Does the event cross a bounded context or service boundary?
  ├── No:  Domain event, in-process. Dispatch in memory.
  └── Yes: Integration event. Outbox, broker, versioned schema.

Adopting CQRS?
 Only if read and write patterns diverge enough to justify two models.

Adopting event sourcing?
 Only if audit/history is a business requirement, not a tech aesthetic.
```

The default for most systems is: domain events inside a context,
integration events via outbox across services, single data model, no
event sourcing. Climb the ladder only when specific forces demand it.
