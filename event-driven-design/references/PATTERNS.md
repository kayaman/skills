# Event-Driven Patterns — Reference

Load this when implementing a specific pattern or choosing between two. Organized from "which mode of event?" outward.

Sources cited inline: Adam Bellemare, *Building Event-Driven Microservices, 2nd Edition* (O'Reilly, 2024); Chris Richardson, *Microservices Patterns* (O'Reilly); Ben Stopford, *Designing Event-Driven Systems* (O'Reilly); Martin Kleppmann & Chris Riccomini, *Designing Data-Intensive Applications, 2nd Edition* (O'Reilly); Michael L. Perry, *The Art of Immutable Architecture* (O'Reilly); Vlad Khononov, *Learning Domain-Driven Design* (O'Reilly); Harry Percival & Bob Gregory, *Architecture Patterns with Python* (O'Reilly); Ekaterina Gorshkova, *Kafka for Architects* (Manning/O'Reilly); Kevin Hoffman, *Real-World Event Sourcing* (O'Reilly).

---

## 1. Choosing the event mode

### 1.1 Event notification

**Shape.** `{ type: "OrderPlaced", orderId }` — barely more than a signal.

**Use when:** consumers are already colocated with the producer's data store, the event is rare, or the state is too large/sensitive to push. Consumers call back via API for details.

**Watch out for:** the callback becomes the real integration. If every consumer calls back, you have reinvented RPC with extra steps and a broker bill.

### 1.2 Event-carried state transfer (ECST)

**Shape.** `{ type: "OrderPlaced", orderId, customer:{id,tier}, lines:[…], total }` — enough state to render a downstream view.

**Use when:** consumers should keep running during producer outages; consumers maintain local read models; the cost of stale reads is tolerable.

**Watch out for:** the event becomes the public API of the producer's domain. Every field consumers depend on is now a schema commitment. Split events if the payload is trying to be everything-to-everyone. (Bellemare, 2e.)

### 1.3 Event sourcing

**Shape.** A sequence: `OrderCreated` → `ItemAdded` → `ItemAdded` → `DiscountApplied` → `OrderPaid`. Current state is a fold over the sequence.

**Use when:** audit and replay are first-class requirements (finance, healthcare, trading, compliance); the domain has real events that users and auditors recognise.

**Watch out for:** event-sourcing everything because it seems neat. The discipline required to keep events backward-compatible forever is high. The read side must be CQRS — you cannot query the event log directly for anything non-trivial. (Hoffman, *Real-World Event Sourcing*; Perry, *The Art of Immutable Architecture*.)

### 1.4 Decision table

| Consumer needs | Best mode |
|---|---|
| "Nudge me, I'll look things up" | Notification |
| "Give me enough to populate my local view" | ECST |
| "Reconstruct any state I have ever had" | Event sourcing |
| "Query by arbitrary attributes with low latency" | ECST + derived read model (CQRS) |
| "Replay the history after a bug fix" | Event sourcing (natively) or ECST (if producer replays the compacted topic) |

Per-boundary choice — not per-system. A single platform often has all three on different topics.

---

## 2. CQRS and projections

CQRS (Command Query Responsibility Segregation) separates the write model (commands → events) from read models (projections over the event stream or ECST topic).

**When CQRS pays off:**

- Read volume dwarfs write volume and the read shape differs from the write shape (e.g., analytical rollups over a transactional spine).
- Multiple read models serve different clients (search index, materialized list view, timeline).

**When CQRS hurts:**

- Low scale, simple CRUD. You pay eventual consistency and synchronization bugs for no win.
- The read and write shapes are identical. You are just duplicating data. (Richardson, *Microservices Patterns*.)

**Projection rules:**

- A projection is deterministic: same events → same state. Non-determinism (e.g., `now()`, random, external HTTP inside the fold) destroys replayability.
- Projections are cheap to throw away and rebuild. Bake this into operations — an engineer should be able to drop and rebuild any projection as a routine task.
- Version projections, not events. When the view shape changes, build v2 next to v1 and cut over.

---

## 3. Transactional outbox (implementation recipe)

The single most important pattern in this skill. Without it, every other pattern silently breaks.

**Why needed.** Writing to the DB and then to the broker is a dual-write. Failures between the two commits produce either:

- State changed, event lost (downstream stuck on stale data, no signal to recover) — or —
- Event sent, state rolled back (downstream reacts to a fact that never happened).

**Mechanism.**

1. In the same local DB transaction that mutates business state, insert a row into an `outbox` table. Commit.
2. A separate relay process reads unpublished outbox rows in order, forwards them to the broker, then marks them published (or deletes them).
3. If the relay crashes, it resumes from the earliest unpublished row.
4. The broker may receive duplicates if the relay publishes and crashes before marking. That is fine — consumers dedupe on `event.id`.

**DDL.** See `assets/outbox-table.sql`.

**Relay options, ordered by "least moving parts":**

1. **Polling relay in the same service.** Simple, no extra infra. Pros: owns its own backpressure. Cons: polling latency, N connections if you scale out.
2. **Change Data Capture (CDC) off the DB log** (Debezium, DynamoDB Streams, Postgres logical replication). Pros: low latency, no polling. Cons: operational complexity, bespoke format requires a transformer.
3. **Transactional outbox + CDC on the outbox table.** Best of both — you own the schema; the relay is just CDC.

**What goes in the outbox row:**

```sql
outbox (
  id           UUID      PRIMARY KEY,  -- event id, used by consumers to dedupe
  aggregate    TEXT      NOT NULL,     -- e.g., 'Order'
  aggregate_id TEXT      NOT NULL,     -- partition key for the event
  type         TEXT      NOT NULL,     -- 'OrderPlaced'
  version      INT       NOT NULL,     -- schema version
  payload      JSONB     NOT NULL,     -- the envelope's `data`
  headers      JSONB     NOT NULL,     -- causationId, correlationId, source, occurredAt
  created_at   TIMESTAMPTZ DEFAULT now(),
  published_at TIMESTAMPTZ                -- null until the relay publishes
);
CREATE INDEX outbox_unpublished ON outbox (created_at) WHERE published_at IS NULL;
```

**Backpressure.** If the broker is down, outbox rows accumulate. Monitor `COUNT(*) WHERE published_at IS NULL` and alert above a threshold. The system will self-heal when the broker returns; the number tells you how far behind you are.

(Richardson, *Microservices Patterns*, O'Reilly.)

---

## 4. Idempotent consumers

Delivery semantics recap:

- **At-most-once** — no retries, no dedupe. You will lose events. Only acceptable for non-critical telemetry.
- **At-least-once** — retries on failure, possibly redelivers. The honest default.
- **Exactly-once (end-to-end)** — requires consumer idempotency. The broker cannot provide it alone.

**Pattern A — dedupe table.**

```sql
consumed_events (
  event_id     UUID    NOT NULL,
  consumer     TEXT    NOT NULL,
  consumed_at  TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (event_id, consumer)
);
```

Handler pseudocode:

```
BEGIN;
  INSERT INTO consumed_events (event_id, consumer) VALUES ($1, $2)
    ON CONFLICT DO NOTHING RETURNING 1;
  -- if no row returned → already processed → COMMIT and ack
  -- else → apply side effects in this transaction → COMMIT and ack
COMMIT;
```

Side effects must be in the same transaction. If the side effect is external (HTTP, email), move it to the consumer's own outbox and publish a downstream event.

**Pattern B — idempotent state transitions.**

Design the operation so applying it N times yields the same state as applying it once.

- Non-idempotent: `balance += amount`.
- Idempotent: `INSERT INTO ledger_entries (id, account, amount) VALUES (?, ?, ?) ON CONFLICT DO NOTHING; balance = SUM(amount)`.

**Pattern C — sequence numbers / causation.**

If events for one aggregate are ordered and monotonic (e.g., `Order.seq=1,2,3`), the consumer can track `max_seq_per_aggregate` and ignore anything `<=` that. Works only if the producer guarantees ordered delivery per aggregate (e.g., Kafka partitioned by aggregate id).

(Kleppmann & Riccomini, *DDIA, 2e*; Bellemare, *Building Event-Driven Microservices, 2e*.)

---

## 5. Change Data Capture (CDC)

CDC reads the database's write-ahead log and emits a change event per row mutation.

**Use when:**

- You need events from a legacy system whose code you cannot change.
- The "event" is genuinely "a row changed" with no higher-level meaning.

**Do not use when:**

- You have design authority over the producer. In that case the business table schema becomes the public event contract, and column renames become breaking changes for consumers. Prefer an outbox.
- The event represents a business fact that spans multiple rows or tables. CDC will emit one event per row; you need an application-level event that aggregates them.

(Bellemare, *Building Event-Driven Microservices, 2e*.)

---

## 6. Claim-check / large payload

Events bigger than a broker's soft limit (often 1 MB) should carry a reference, not the bytes.

**Pattern.** Producer uploads the large payload (image, PDF, ML model) to object storage, emits an event with the URL and a checksum. Consumer fetches on demand.

```json
{
  "type": "DocumentUploaded",
  "data": {
    "documentId": "doc_7Qk2",
    "storageUri": "s3://docs-prod/2026/04/23/doc_7Qk2.pdf",
    "sha256": "a3f1…",
    "bytes": 4_201_338
  }
}
```

Consumers that do not need the bytes (metadata reactors, analytics) never pull. Consumers that do need them pull with retry and verify the checksum. (Stopford, *Designing Event-Driven Systems*.)

---

## 7. Event sourcing, mechanically

Load this section only if event sourcing is the chosen mode.

**The aggregate.** A consistency boundary that owns a stream. All mutations go through a single entry point (`handle(command) → events`). All queries against the aggregate's in-memory state go through a fold (`events → state`).

Minimal Python-ish illustration (Percival & Gregory, *Architecture Patterns with Python*, chapter 8 pattern):

```python
class Order:
    def __init__(self, events: list[Event]):
        self.state = self._fold(events)

    def _fold(self, events):
        state = EmptyOrder()
        for e in events:
            state = state.apply(e)
        return state

    def place(self, customer_id, lines):
        if self.state.placed:
            raise DomainError("already placed")
        return [OrderPlaced(customer_id=customer_id, lines=lines, placed_at=now())]

    def pay(self, amount):
        if not self.state.placed:
            raise DomainError("cannot pay unplaced order")
        if amount != self.state.total:
            raise DomainError("amount mismatch")
        return [OrderPaid(amount=amount, paid_at=now())]
```

**Repository.** Reads all events for an aggregate id, constructs the aggregate, returns it. On save, appends new events atomically, typically with optimistic concurrency via `expected_version`.

**Snapshots.** When the event count per aggregate grows large (hundreds to thousands), store a snapshot every N events. Load snapshot + events since. Snapshots are a cache, never authoritative.

**Projections.** A process that subscribes to the event stream and builds a read model. Must be replayable from offset 0 and deterministic. Store the last applied `event.id` (or offset) in the projection's own table so a restart resumes correctly.

**Upcasters.** When an event type's shape changes, you do *not* rewrite history. You write an upcaster — a pure function `v1 → v2` — and apply it on read. This is the price of immutability. (Hoffman, *Real-World Event Sourcing*.)

**Rebuild.** Drop the projection table, replay from offset 0, rebuild. This must be a routine ops operation, not a heroic effort. If rebuild takes 8 hours, that is a bug to fix, not a constraint to accept.

---

## 8. Choosing topic design

A topic (stream, queue, subject — broker-specific) is the unit of subscription. Topic design mistakes are expensive to undo because consumers are already wired.

- **One topic per aggregate type.** `orders`, `payments`, `users`. Not one giant `events` topic with a `type` discriminator — consumers then pay to deserialize events they do not care about, and schema evolution is entangled across unrelated domains.
- **Partition key = aggregate id.** Guarantees per-aggregate ordering. Pay attention to partition skew (see Gotchas).
- **Retention — functional vs compaction.** Functional retention (keep 7 days) for ECST where only the latest state matters; log compaction (keep the latest per key forever) for tables-as-events. Event-sourced topics retain forever.
- **Dead-letter topic per consumer, not per producer.** Failures are consumer-side; the producer has no visibility.
- **Name topics and events consistently.** `payments.order-paid.v1` scales past 100 topics. Ad-hoc naming does not. (Gorshkova, *Kafka for Architects*.)

---

## 9. Dead-letter queues and poison messages

A message that crashes the handler gets retried. After N retries, it goes to a DLQ. Rules:

1. **Every consumer has a DLQ.** No exceptions. Silent drop is worse than a full DLQ.
2. **DLQ alerts are blocking.** A non-zero DLQ count during business hours is an incident.
3. **Never auto-replay a DLQ.** You will loop if the handler is still broken. Manually inspect, fix the code, then replay (a script, not an automated job).
4. **Include diagnostics in the DLQ record.** Original event, headers, exception stack, handler version. Debugging a DLQ with just the payload is painful.
5. **Track the root cause class, not the count.** 1000 duplicates of "schema mismatch" is one incident; 10 unique errors is ten.

---

## 10. Replay and backfill

A healthy event system can rebuild any read model from the event history. A design that makes this hard is fragile.

**Requirements:**

- Retain the event stream long enough (or use log compaction if appropriate).
- Projections are idempotent and deterministic.
- Consumers can be pointed to a historical offset and fed the whole history at full speed without breaking live traffic.
- The replay speed is high enough to rebuild in hours, not days. Benchmark it.

**Two common backfill flows:**

- **New consumer joins.** Consumer starts from offset 0 (or the earliest retained), catches up, then joins live tail.
- **Projection rebuild after bug.** Drop projection table, reset consumer offset to 0 for that consumer group, replay.

Never backfill by replaying from an ad-hoc SQL dump. The replay source is the event log — that is literally its job.

---

## 11. Quick reference: pattern ↔ problem

| Problem | Pattern |
|---|---|
| "I need the DB state and the event to be atomic." | Transactional outbox (§3) |
| "My consumer runs twice, money moves twice." | Idempotent consumer (§4) |
| "I need to react to DB changes in a legacy system I cannot modify." | CDC (§5) |
| "My events are bigger than 1 MB." | Claim-check (§6) |
| "I need audit + replay + temporal queries." | Event sourcing (§7) |
| "My read side is slow; my write side is complex." | CQRS + projections (§2) |
| "Services fan-out and fan-in through a chain of events nobody understands." | Refactor to orchestrated saga (see `SAGAS.md`) |
| "I keep getting the same old event reprocessed on restart." | Store consumer offset + dedupe table |
| "Payloads diverged and now everyone's schema is different." | Schema registry + CI compatibility gate (see `EVENT_SCHEMA.md`) |
