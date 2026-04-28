# New Consumer: `<consumer-name>`

> Copy this file, fill it out, and save as `docs/consumers/<consumer-name>.md` in the service that owns the consumer. The filled template is the consumer's design specification.

## Identity

- **Consumer name:** `<consumer-name>` (e.g., `shipping-on-order-paid`)
- **Owning service:** `<service>`
- **Subscribed topic(s):** `<topic>`, ...
- **Consumer group:** `<group-id>` (must be unique per logical consumer role)

## What this consumer does

One sentence describing the reaction to the event(s) in business terms.

> Example: "When an order is paid, schedule a shipment and emit `ShipmentRequested`."

## Events consumed

| Event | Version | Mode (notification / ECST / sourced) |
|---|---|---|
| `<EventName>` | `<v>` | `<mode>` |

## Events emitted (via outbox)

| Event | Trigger |
|---|---|
| `<EventName>` | `<condition>` |

## Side effects

- Internal DB mutations: list the tables and the shape of the change.
- External systems: list every HTTP / gRPC / third-party call this handler makes.
- Notifications: emails, SMS, push.

For every external side effect, describe how idempotency is preserved.

## Idempotency strategy

[ ] **Dedupe table.** Reject duplicate `event.id` via `consumed_events`. Side effects live inside the same DB transaction as the dedupe insert.

[ ] **Idempotent state transition.** The operation produces the same state whether applied once or N times. Describe why:

> `<reasoning>`

[ ] **Sequence tracking.** Track `max(sequenceNumber)` per aggregate; ignore lower-or-equal.

## Failure and retry policy

- Transient failures: N retries with backoff [linear / exponential], jitter [yes / no].
- Exhausted retries: route to DLQ `<dlq-name>`.
- Poison message: any message that fails deserialization routes to DLQ without retry.

## Offset commit strategy

[ ] **Manual commit after side-effects durable.** Offset is committed only after the DB transaction commits and any outbox row is persisted.

[ ] **Auto-commit** (only acceptable when the handler is read-only and idempotent; otherwise use manual).

## Observability

- `correlationId` propagated into every log line of the handler.
- Metrics emitted:
  - `consumer.<name>.events.processed` (counter)
  - `consumer.<name>.events.failed` (counter, tagged by reason)
  - `consumer.<name>.lag.seconds` (gauge)
  - `consumer.<name>.dlq.size` (gauge, alert on > 0)
- Tracing: start a span per event; attach `event.id`, `event.type`, `correlationId`.

## Ordering requirements

- [ ] Requires per-aggregate ordering (→ events must be partitioned by `aggregateId`; consumer processes one partition at a time).
- [ ] No ordering required (can parallelize across partitions).
- [ ] Requires cross-aggregate ordering (→ this is probably the wrong design; revisit).

## Tests

- [ ] Unit: given an event, then state change + emitted events are as expected.
- [ ] Idempotency: same event delivered twice → single side effect.
- [ ] Out-of-order: handle events arriving in unexpected sequences (buffer or dead-letter).
- [ ] DLQ: malformed event routes to DLQ without crash-looping.
- [ ] Integration: event flows through broker (Testcontainers) and side effect is observable.

## Rebuild / replay

- Can this consumer be reset to offset 0 and catch up?
- [ ] Yes, idempotency protects against double-application.
- [ ] No — document why. (This is usually a smell.)
