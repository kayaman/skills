# Event-Driven Anti-Patterns — Reference

Load this when reviewing an existing event-driven system that "feels painful," when debugging recurring incidents, or when designing a new boundary and you want a sanity check against common pitfalls.

Each anti-pattern follows the same shape: **symptom**, **why it happens**, **detection**, **fix**.

Sources: Mark Richards & Neal Ford, *Software Architecture Patterns, Antipatterns, and Pitfalls* (O'Reilly); Mark Richards & Neal Ford, *Fundamentals of Software Architecture, 2nd Edition* (O'Reilly); Adam Bellemare, *Building Event-Driven Microservices, 2nd Edition* (O'Reilly); Sam Newman, *Building Microservices, 2nd Edition* (O'Reilly); Chris Richardson, *Microservices Patterns* (O'Reilly); Vlad Khononov, *Learning Domain-Driven Design* (O'Reilly).

---

## 1. The Distributed Monolith with Events

**Symptom.** Twelve services. Every user action requires six of them to publish, consume, publish, consume. A single deploy of service A requires coordinated deploys of B, C, D. Rollbacks are catastrophic. Latency is worse than the monolith it replaced.

**Why it happens.** Services were split along *technical* lines (one per CRUD entity, one per DB table) rather than *domain* lines. Events became a way to reassemble what should have been one bounded context. Coupling did not disappear — it moved from a function call to a topic with no IDE to track it.

**Detection.**
- Draw the event flow of a single user journey. If it does not fit on one screen, suspect.
- `git log` across service repos: are releases coordinated? Look for PR titles like "coordinate release with payments 2.4.x".
- Any topic where a single bad deploy breaks four consumers simultaneously.

**Fix.** Merge services whose events always flow together. The lightest boundary between two services is no boundary. Bellemare recommends running an event storming workshop (see `EVENT_STORMING.md`) to re-discover the natural aggregates, then redrawing service boundaries around them, not around tables.

---

## 2. Chatty Events / Event Storms

**Symptom.** One business action emits 50 events. Consumers are overwhelmed, brokers are saturated during peak, CPU on consumers spikes to 100%.

**Why it happens.**
- Fine-grained events for every field change: `UserFirstNameChanged`, `UserLastNameChanged`, `UserMiddleNameChanged` published when the user typed once and hit save.
- CDC on every column of a large table with no rate limiting.
- Events that in turn trigger events (feedback loops).

**Detection.**
- Plot events per business action. More than a handful per user-visible action is a yellow flag.
- Monitor broker throughput per topic; look for topics with high event rate relative to business throughput.
- Look for circular event flows: service A consumes `X` and emits `Y`; service B consumes `Y` and emits `X`.

**Fix.**
- Aggregate field changes into one event per user action: `UserProfileUpdated` with the diff, not ten events.
- Debounce or batch CDC.
- Feedback loops must be broken by construction, not by rate-limit tuning: if `X → Y → X`, one of the two arrows is wrong. (Richards & Ford, *Software Architecture Patterns, Antipatterns, and Pitfalls*.)

---

## 3. Temporal Coupling Through Events

**Symptom.** Service A publishes `X`, service B publishes `Y`, and C correctly processes only when B receives Y before A's `X`. "Fix" is a sleep in C's handler or a polling loop.

**Why it happens.** The "independent" services are actually coupled through time ordering that the broker does not guarantee.

**Detection.**
- Any handler that checks "is the other state ready yet" and loops.
- Any retry that is really a wait.
- Tests pass locally but fail under load.

**Fix.**
- Model the real prerequisite as data. C consumes both X and Y, keeps local state, and applies the combined effect only once both arrive. A dedupe table keyed by `(X.id, Y.id)` or by the correlation id handles the asynchrony.
- If the prerequisite cannot be modelled (you really need the result of X before Y can be meaningful), this is not an event-driven flow; it is a saga. See `SAGAS.md`.

---

## 4. The "God Event"

**Symptom.** One event type `UserUpdated` with 40 optional fields and a `changedFields: [...]` array. Every consumer must parse the array, diff against local state, and decide what changed.

**Why it happens.** The producer's team wanted flexibility; the consumers' teams were not consulted. CRUD thinking leaked into event design.

**Detection.**
- Event names ending in `Updated`, `Changed`, `Modified` without domain specificity.
- Schema has > 10 optional fields.
- Consumer code contains `if (event.changedFields.includes("email"))` branches.

**Fix.** Split into specific events per business fact: `UserEmailChanged`, `UserAddressChanged`, `UserTierUpgraded`. Consumers subscribe to the ones they care about. The schema evolution surface shrinks dramatically because each event only moves when its specific fact does. (Bellemare, *Building Event-Driven Microservices, 2e*; Khononov, *Learning DDD*.)

---

## 5. Missing Events / Queries Through Events

**Symptom.** Service A publishes `UserLookupRequested`; service B publishes `UserLookupReplied` on a different topic. A joins them by `requestId`. Latency is 300ms, debugging is grep through two topics.

**Why it happens.** Teams want "decoupling" and reach for events reflexively. Request/response is seen as "the old way."

**Detection.**
- Any pair of events `Requested` / `Replied`, `Asked` / `Answered`.
- Any consumer that blocks (logically) on a reply topic.
- Correlation IDs used as request IDs.

**Fix.** Delete the "event pair" and make a synchronous call — an HTTP or gRPC request from A to B. If you must decouple, materialize a local read model from B's legitimate domain events and query that locally. Request–reply over events is synchronous RPC with added latency and halved debugability. (Richardson, *Microservices Patterns*.)

---

## 6. Poison Messages and DLQ Mismanagement

**Symptom A — silent drop.** Messages that fail the handler are swallowed and the consumer continues. Loss is only detected via customer complaints.

**Symptom B — crash loop.** Messages that fail the handler are retried forever. Consumer pegs CPU, downstream lags grow, operators panic.

**Symptom C — DLQ black hole.** DLQ has millions of messages. No one has looked at it in six months. No alert fires.

**Why it happens.**
- A — missing error handling: exception caught and logged, offset committed.
- B — retries without a cap, or retries with cap but no DLQ routing.
- C — DLQ was "good enough" to ship without alerting.

**Detection.**
- Read the consumer's error path line by line. `try { handle() } catch (e) { log(e); }` is a silent drop.
- Monitor DLQ size. Anything above zero during business hours is an incident.
- Confirm the DLQ has an alert wired.

**Fix.**
- Explicit policy: N retries with backoff → DLQ.
- Every DLQ has an alert on non-zero size.
- DLQ messages carry diagnostics: original event, exception, handler version, timestamp.
- Replay from DLQ is manual, never automated. Fix the code first, then replay. (Newman, *Building Microservices, 2e*.)

---

## 7. Hot Partition

**Symptom.** One consumer instance is pegged; others are idle. Latency on one aggregate is bad; everyone else is fine. Auto-scaling adds consumers; one still pegged.

**Why it happens.** Partition key is skewed. `tenantId` as key and one tenant does 80% of traffic, or `orderId` distributes evenly but one order has 50k events because it is the system test.

**Detection.**
- Per-partition lag dashboards. Skew is visible immediately.
- Per-partition throughput — one partition at 10x the others.

**Fix.**
- Salt the key for the skewed entity: `tenantId + "::" + hash(eventId) % 16`. Breaks per-aggregate ordering — only apply when ordering is not required.
- Route the hot tenant to its own topic with more partitions.
- Revisit the partitioning decision: maybe the right key is not what you chose. (Gorshkova, *Kafka for Architects*.)

---

## 8. "Share Nothing, Copy Everything"

**Symptom.** Every service has its own local copy of the user table, built from `UserCreated` / `UserUpdated` events. The copies drift. Support tickets about stale data are common.

**Why it happens.** "Services should be independent" interpreted as "services should never call each other." ECST taken to an extreme.

**Detection.**
- Multiple services maintain identical projections of the same entity.
- Bug reports about stale data: "the email we sent used the old address."
- Dashboards show per-service user counts that disagree.

**Fix.**
- Ask: what does this service *actually* need? Often a subset of fields. A narrower projection drifts less.
- For data that must be accurate now (email to send a password reset), call the source synchronously. Eventual consistency is a trade, not an absolute.
- Add monitoring that compares projection counts/checksums across services and alerts on drift. (Bellemare, *Building Event-Driven Microservices, 2e*.)

---

## 9. Non-Deterministic Projections

**Symptom.** Rebuilding a projection from offset 0 produces a different result each time. Tests randomly pass or fail depending on clock/order.

**Why it happens.**
- Projection uses `now()`, `random()`, or external HTTP during the fold.
- Projection depends on the order of events across partitions (which is not guaranteed across partitions).
- Projection depends on wall-clock ordering rather than producer sequence.

**Detection.**
- Run the projection rebuild test (`TESTING.md` §8) three times; if results differ, you have non-determinism.
- Grep the projection code for `time.now()`, `System.currentTimeMillis()`, `random`, HTTP client calls.

**Fix.**
- Projections take `(state, event) → state`. Pure function. No external calls.
- If "now" is needed, carry it in the event (`occurredAt`).
- Order requirements must be satisfied by the partitioning strategy (one aggregate's events in one partition). Do not assume cross-partition ordering.

---

## 10. "Just Use CDC" as a Design Decision

**Symptom.** Every event is a raw row-change from the primary database. Every column rename breaks every consumer.

**Why it happens.** CDC looks free: you did not have to write producer code. The cost is paid later when the business table schema becomes a public API.

**Detection.**
- Event names look like `users_table_row_updated` with before/after column dumps.
- Column renames in the DB have been blocked for months because "too many downstream consumers."

**Fix.**
- Promote the producer: write an application-level event in an outbox. The outbox schema is owned by you; the DB schema is free to change.
- Use CDC, but off the outbox table, not off the business tables. (Bellemare, *Building Event-Driven Microservices, 2e*.)

---

## 11. Commands on Event Topics

**Symptom.** A topic `orders` carries both `OrderPlaced` (fact, past) and `PlaceOrder` (intent, present). Consumers are confused; some fire side effects on what they thought were events but are actually commands.

**Why it happens.** Topic consolidation for "simplicity," or confusion about whether an envelope carries fact or intent.

**Detection.**
- Event names mixing past and imperative on one topic.
- Schema has a `"kind": "command" | "event"` discriminator field.

**Fix.** Separate topics. Commands go on command-dedicated channels (or request/response protocols like gRPC). Events are immutable facts on event topics. The two travel in opposite logical directions; do not mix.

---

## 12. Offset Commit Before Side Effect

**Symptom.** Consumer calls an external API (email, payment, HTTP), occasionally the process dies after the commit but before the API call completes. Side effect is lost, event is marked processed.

**Why it happens.** Auto-commit enabled, or manual commit placed before the side effect for "simplicity."

**Detection.**
- Auto-commit on + any non-transactional side effect in the handler.
- Missing emails, missing downstream state changes that the consumer logs say it processed.

**Fix.**
- Commit the offset *only after* the side effect is durable. For transactional databases: put the side effect in the transaction that updates the consumer's state, commit the offset after.
- For non-transactional side effects (HTTP, email): write to the consumer's outbox inside the DB transaction that also records the offset, then commit. The outbox relay sends the side effect with at-least-once semantics.
- Consumer-side idempotency everywhere, because at-least-once is the ceiling. (Kleppmann & Riccomini, *DDIA, 2e*.)

---

## 13. Compensations That Are Not Idempotent

**Symptom.** A saga compensation runs, the network flakes, it retries, the compensation applies twice (double refund, double inventory release, double email).

**Why it happens.** The forward transaction was idempotent; the compensation was written in a hurry and forgotten.

**Detection.**
- Audit every compensation for the same idempotency story as the forward transaction.
- Tests for compensation rarely assert "run twice, effect is once."

**Fix.** Same techniques as consumer idempotency: dedupe key, or idempotent state transition. Saga unit tests must cover double-compensation.

---

## 14. "Eventually" Meaning "Never"

**Symptom.** Service claims to be eventually consistent. Operators notice drift that never heals. Incident review reveals a missing retry or a permanently-stuck consumer.

**Why it happens.** "Eventual" became a synonym for "hopefully" when no one set a bound.

**Detection.**
- No SLO on consumer lag.
- No alert on DLQ size.
- No monitoring on "projection X behind by Y seconds."

**Fix.** Every "eventually" must have a bound: a consumer-lag SLO, a DLQ-size SLO, a projection-lag SLO. "Eventual" without a deadline is just "fail open."

---

## 15. Review Heuristics (Fast Walkthrough)

When reviewing a codebase for EDA health, walk these in order:

1. **Topic inventory.** List every topic, its producer, its consumers, and the mode (notification / ECST / sourcing). Mixed-mode topics are a red flag.
2. **Publish surface.** `rg 'producer\.send|kafkaTemplate\.send|sns:Publish|eventBridge\.putEvents'` — every hit should be wrapped by an outbox helper. Raw publishes are latent dual-write bugs.
3. **Idempotency coverage.** `rg -l 'consumed_events|dedupe' <consumer-dirs>` — any consumer that does not appear is suspect. Read its handler.
4. **Event names.** Past tense, PascalCase, scoped to one aggregate. Catalog the violations.
5. **Schema evolution.** `git log -p` on schema files. Any change without `version` bump, compatibility annotation, or consumer-coordination comment is an unreviewed break.
6. **DLQ plumbing.** Every consumer has a DLQ. DLQ has an alert. Find exceptions.
7. **Saga legibility.** Multi-service workflows: is there a single place to look for "where is order X?". If no, recommend orchestration refactor.
8. **Observability.** `correlationId` in every log line of every handler. Missing correlation is the single biggest debugging tax.

Anti-patterns compound. Finding one often reveals two more. Write them up with severity (critical / high / low) and remediation effort; prioritize the compounding ones.
