---
name: event-driven-design
description: Design, implement, and test event-driven systems — event modelling, schema evolution, transactional outbox, sagas (orchestration and choreography), event sourcing, CQRS, idempotent consumers, and tests that actually catch race conditions. Use whenever the user mentions events, event bus, message broker, Kafka, RabbitMQ, SNS/SQS, EventBridge, Pub/Sub, Kinesis, event sourcing, CQRS, sagas, choreography, outbox, CDC, dead-letter queue, eventual consistency, at-least-once delivery, or when designing asynchronous coupling between services. Also use when reviewing event-driven code for failure modes or converting a synchronous design to event-driven. Do NOT use for fire-and-forget in-process callbacks, UI event listeners, DOM events, plain pub/sub inside a single process, reactive UI state machines, or pure request/response API design (use api-design-principles instead). Do NOT use to pick a specific broker (Kafka vs RabbitMQ vs SQS) — this skill is vendor-neutral.
license: MIT
metadata:
  author: kayaman
  version: "1.0"
  sources: "Curated from Bellemare (Building Event-Driven Microservices 2e), Richardson (Microservices Patterns), Stopford (Designing Event-Driven Systems), Kleppmann (DDIA 2e), Newman (Building Microservices 2e), Khononov (Learning DDD), Richards/Ford (Software Architecture Patterns, Antipatterns, and Pitfalls), Hoffman (Real-World Event Sourcing), Perry (The Art of Immutable Architecture), Vernon (Implementing DDD), Percival/Gregory (Architecture Patterns with Python), Gorshkova (Kafka for Architects) — O'Reilly Media."
allowed-tools: Read Grep Glob Bash(rg:*) Bash(python3:*)
---

# Event-Driven Design

Design, implement, review, and test event-driven systems. The goal of this skill is to make the default choice the correct one — so the system stays debuggable, evolvable, and resilient as it grows beyond the first three services.

This file is a table of contents. Load referenced files only when the task needs them.

| Reference | When to load |
|---|---|
| `references/PATTERNS.md` | Choosing between event notification / state transfer / sourcing; designing aggregates, projections, CDC. |
| `references/EVENT_SCHEMA.md` | Designing a new event, changing an existing one, versioning, schema registry, compatibility rules. |
| `references/SAGAS.md` | Cross-service workflow, compensating actions, choreography vs orchestration, process managers. |
| `references/TESTING.md` | Writing tests — unit (given-when-then on aggregates), consumer-driven contracts, integration with Testcontainers, contract compatibility CI gate. |
| `references/ANTIPATTERNS.md` | Reviewing existing code or debugging "why is this system so painful?" |
| `references/EVENT_STORMING.md` | Starting from a blank domain — running the workshop, colour coding, translating stickies to bounded contexts. |

Scripts (invoke via bash; only the output consumes context):

- `scripts/validate-event-schema.py <event.json> <schema.json>` — validate an event instance against a JSON Schema envelope.
- `scripts/check-naming.py <path>` — enforce past-tense event names and envelope fields across a directory of schemas.

---

## The three kinds of "event"

Most confusion in event-driven design starts here. Get this right first, then everything else composes.

1. **Event notification** — "something happened, go look if you care." Minimal payload (IDs + timestamp). Consumer calls back to source for details. Lowest coupling, highest chattiness.
2. **Event-carried state transfer** — the event carries enough state that consumers need no callback. Higher payload size, but consumers can degrade independently of the producer. The default for most integrations.
3. **Event sourcing** — the event stream *is* the source of truth. Current state is a fold over the history. Strongest audit and replay story; highest design discipline required.

*Rule:* Pick one per boundary and state it in the contract. Mixing modes silently inside one topic is the largest source of mystery bugs in mature event systems. (Bellemare, *Building Event-Driven Microservices, 2nd Edition*, O'Reilly; Fowler's taxonomy as cited in Richardson, *Microservices Patterns*, O'Reilly.)

## Command versus event

- A **command** expresses intent (`PlaceOrder`). It can be rejected. Named in imperative. One handler. Coupling is explicit.
- An **event** states a fact (`OrderPlaced`). It cannot be rejected — it already happened. Named in past tense. N handlers. Coupling is inverted (producer does not know who listens).

If you're debating whether something is a command or an event, ask: *can a consumer refuse it?* If yes, it is a command. If the "event" has a handler that validates and rejects, rename it to a command — you have misplaced authority.

## The non-negotiables

These five rules hold across every event-driven system worth running in production. Load `references/PATTERNS.md` for the detailed treatment.

1. **Events are immutable, named in past tense** — `OrderPlaced`, not `PlaceOrder` and not `OrderPlacing`. An immutable fact is the unit of interop. (Perry, *The Art of Immutable Architecture*, O'Reilly.)
2. **Every event carries an envelope** — `id`, `type`, `version`, `source`, `occurredAt`, `causationId`, `correlationId`, plus the domain payload. The envelope exists so consumers can deduplicate, trace, and evolve without coordinating with the producer. See `assets/event-envelope.schema.json`.
3. **Publishing must be atomic with the state change** — use the transactional outbox (or change-data-capture off the same transaction log). If you write to the DB and then to the broker in two steps, you have a dual-write bug; it is only a question of when it bites. (Richardson, *Microservices Patterns*, O'Reilly.)
4. **Consumers are idempotent** — at-least-once delivery is the ceiling of what brokers reliably give you. "Exactly-once" at the consumer is achieved by deduping on `event.id` or by idempotent state transitions — not by trusting the broker. (Kleppmann & Riccomini, *DDIA, 2nd Edition*, O'Reilly.)
5. **Schemas evolve under rules, not vibes** — agree on backward and/or forward compatibility per topic, enforce it in CI, and register it. See `references/EVENT_SCHEMA.md`. (Bellemare, *Building Event-Driven Microservices, 2e*; Stopford, *Designing Event-Driven Systems*, O'Reilly.)

---

## When to reach for this skill (and when not)

**Reach for it when:**

- Two or more services need to react to something happening in a third, and those reactors want to ship independently.
- The domain has natural events — orders, payments, user signups, stock movements, document uploads — and downstream systems care about the fact, not the request.
- Audit, replay, or retroactive analytics matter — event logs make these trivial that would otherwise be retrofits.
- Load spikes on the producer must not propagate synchronously to consumers.

**Do NOT reach for it when:**

- The caller needs an immediate, strongly consistent answer (payment authorization, username uniqueness check, seat-reservation at ticket sale). Use synchronous request/response.
- You have fewer than three services and no foreseeable consumer growth. The operational cost (broker, DLQ, replay tooling, schema registry, tracing) exceeds the coupling cost of a direct call at that scale. (Newman, *Building Microservices, 2nd Edition*, O'Reilly.)
- The team does not yet have the observability to debug asynchronous flows (distributed tracing, structured logs keyed on `correlationId`, DLQ dashboards). Adopt those first; EDA on top of blind operations is a debugging nightmare.
- You are simulating request/response over events (publish a command, poll a reply topic for the result). This is almost always an accidental distributed monolith. Prefer a real synchronous call or a saga — see `references/SAGAS.md`.

Adopting EDA is hard to reverse. Bias toward starting synchronous and extracting events at the seams that proved valuable — not toward greenfield EDA on day one.

---

## The shortest path to a correct new event

Use this when adding a single new event to an existing system. For a greenfield domain, run event storming first (`references/EVENT_STORMING.md`).

### Checklist (copy into your response and tick as you go)

```
- [ ] Event named in past tense, unambiguous, and scoped to one aggregate (`OrderPaid`, not `OrderUpdated`)
- [ ] Fits the chosen mode for this topic: notification, state transfer, or sourcing — pick one
- [ ] Envelope fields filled: id (UUIDv7 or ULID), type, version=1, source, occurredAt, causationId, correlationId
- [ ] Payload contains a stable identifier for every referenced entity (never only mutable display strings)
- [ ] Schema defined (Avro / Protobuf / JSON Schema), checked into the repo next to the producer
- [ ] Backward-compatibility rule declared for the topic (and documented in the schema file header)
- [ ] Producer writes event + state in one local DB transaction via the outbox table
- [ ] A relay (or CDC) publishes outbox rows to the broker — not application code directly
- [ ] Consumers dedupe on event.id (consumed-events table, or idempotent state transition)
- [ ] A replay strategy exists: can a new consumer backfill from the topic or the outbox?
- [ ] Tests: producer aggregate (given-when-then), consumer handler, schema-compatibility, end-to-end with Testcontainers
- [ ] Tracing: causationId/correlationId propagated through every handler; visible in logs
```

If any box is "no", load the matching reference file and fix it before merging.

### Envelope template (copy, don't retype)

```json
{
  "id": "01H8XYZ...",                       // UUIDv7 or ULID — monotonic + unique
  "type": "OrderPaid",                      // past tense, PascalCase
  "version": 1,                             // integer; bump on breaking changes
  "source": "payments.service",             // stable identifier for the producer
  "occurredAt": "2026-04-23T02:45:12.413Z", // ISO-8601, UTC, millisecond precision
  "causationId": "01H8XYW...",              // id of the command/event that caused this
  "correlationId": "01H8XYV...",            // end-to-end flow id, constant across the saga
  "data": {
    "orderId": "ord_7Qk2",
    "amount": { "currency": "BRL", "minor": 42900 },
    "paidAt": "2026-04-23T02:45:11.900Z"
  }
}
```

Full schema: `assets/event-envelope.schema.json`. Validate with `scripts/validate-event-schema.py event.json assets/event-envelope.schema.json`.

---

## Patterns you will almost certainly need

Load `references/PATTERNS.md` for the full catalogue. These three are the ones worth knowing at TOC level:

### Transactional outbox (atomic publish)

**Problem.** Writing to the DB and the broker in two network calls is a dual-write. One can succeed while the other fails — silently producing ghost state or lost events.

**Solution.** Write to an `outbox` table **in the same local transaction** as the business state. A separate process (a *relay*) reads unpublished rows and forwards them to the broker, then marks them published. Rows are eventually consistent with the broker; the DB and outbox are always consistent with each other.

Why this beats "just send to the broker in a finally block": the finally block runs after the transaction commits, which is exactly when the process can crash and you lose the event. The outbox removes that window because the commit itself records the intent to publish.

DDL skeleton: `assets/outbox-table.sql`. (Richardson, *Microservices Patterns*, O'Reilly.)

### Idempotent consumer

**Problem.** Brokers deliver at-least-once. Retries, rebalances, and reprocessing all re-deliver events the consumer already saw. Processing the same `OrderPaid` twice debits the customer twice.

**Solution (pick one):**

- **Dedupe table.** Before applying side effects, `INSERT … ON CONFLICT DO NOTHING` into `consumed_events(event_id, consumer_name)`. Skip if already there.
- **Idempotent state transition.** Design the operation so applying it twice yields the same state. `balance = balance + amount` is not idempotent; `balance_at_seq(seq=42) = X` is.

Do not rely on the broker's "exactly-once" flag alone. It usually means exactly-once inside the broker's storage — not across your external side effects. (Kleppmann & Riccomini, *DDIA, 2e*, O'Reilly.)

### Saga for cross-service workflows

Two flavours:

- **Choreography.** Each service reacts to events and emits its own. No central coordinator. Lowest coupling, hardest to reason about once the graph has more than four nodes.
- **Orchestration.** A named process manager issues commands and handles replies. Central state machine; one place to look when something hangs. Pay the coupling cost of the orchestrator to get the legibility.

For anything with more than two steps or any compensating logic, prefer orchestration. Load `references/SAGAS.md`. (Richardson, *Microservices Patterns*; Newman, *Building Microservices, 2e*, O'Reilly.)

---

## Known gotchas

Concrete failure modes previously seen in production — update this list as you accumulate scars.

- **"Exactly-once" from the broker vendor.** Almost always applies only inside the broker's log (e.g., Kafka idempotent producer + transactional commits). External side effects still need consumer-side dedupe.
- **Sequence numbers reused across topics.** Offsets are per partition, not global. Do not assume `offset=42` means the same thing across topics; use `event.id` for dedupe.
- **Payload with display strings only.** `{"userName": "ana"}` without `userId` will break the day someone renames. Always carry stable identifiers.
- **Time-based ordering via wall clock.** Clocks skew. Order by producer-assigned monotonic id (UUIDv7/ULID) plus partition key, not `occurredAt`.
- **Hot partition from one bad key.** Partitioning by `customerId` when one customer does 80% of traffic pins throughput to a single consumer. Monitor per-partition lag; re-shard or introduce a sub-key if needed.
- **Poison messages looping through the DLQ.** A message that deterministically crashes the consumer will loop if you re-enqueue from DLQ without fixing the handler. Quarantine, fix, replay — in that order.
- **"Just use CDC on the business table."** Works, but the schema of the business table becomes the public contract of the event. Any column rename is now a breaking change for every consumer. Prefer a dedicated outbox whose schema you own.
- **Choreography that grew into a distributed monolith.** Seven services emit and consume from each other in a graph you cannot draw on one screen. Refactor to orchestration around the pivotal events. (Bellemare, *Building Event-Driven Microservices, 2e*, O'Reilly.)
- **"Query through events" anti-pattern.** Publishing `UserInfoRequested` and waiting for `UserInfoReplied` reinvents synchronous RPC with worse latency and worse debugging. Use the synchronous call or a materialized read model.
- **Consumer adds side effect inside the transaction that commits the offset.** If the side effect is non-transactional (HTTP, email), you are back to dual-write. Either make it idempotent and commit after, or move it into an outbox on the consumer side.

---

## Reviewing an existing event-driven system

When the task is "review this code" or "why does this feel painful?", load `references/ANTIPATTERNS.md` and walk this order:

1. Enumerate every topic and classify its mode (notification / state transfer / sourcing). Reject mixed-mode topics.
2. Grep for publish calls not wrapped by the outbox. Every one is a latent ghost-state bug: `rg 'producer\.send|kafkaTemplate\.send|sns:Publish|eventBridge\.putEvents'` plus your local wrappers.
3. Check every consumer for an idempotency key. If applying the handler twice is not safe, add dedupe.
4. Look at the event names. Past tense, scoped to one aggregate, not generic `*Updated` bags. A `UserUpdated` with 14 optional fields is N events pretending to be one; split it.
5. Check schema evolution history (`git log` on the schema files). Breaking changes without a version bump or consumer-coordination plan indicate no governance.
6. Look at DLQ dashboards. Zero messages is suspicious (maybe DLQ not wired). A steady trickle of the same error is a bug with an open feedback loop.

---

## Validating your work (self-correcting loop)

Before declaring a schema or event design done:

1. Run `scripts/validate-event-schema.py <sample.json> <schema.json>` against a realistic instance.
2. Run `scripts/check-naming.py <schemas-dir>` to catch present-tense names and missing envelope fields.
3. Open `references/TESTING.md` and ensure every bullet in the "Minimum viable test pyramid" section has at least one corresponding test committed.
4. If any step fails, fix and re-run. Do not declare done until all three pass.

---

## Pointers to related skills

- `api-design-principles` — when the boundary should be synchronous (REST/GraphQL).
- `domain-driven-design` — aggregates, bounded contexts, ubiquitous language. Event storming is a DDD technique; this skill focuses on implementation.
- `hexagonal-architecture` / `clean-architecture` — how to structure a service so its event handlers do not leak into the domain.
