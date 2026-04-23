# New Event: `<EventName>` (v1)

> Copy this file, fill it out, and save as `schemas/<event-name>.v1.md`. The filled template becomes the event's specification and is reviewed by every downstream consumer team before the producer ships.

## Identity

- **Name:** `<EventName>` — past tense, PascalCase, scoped to one aggregate.
- **Aggregate:** `<Aggregate>`
- **Bounded context:** `<context>`
- **Mode:** [ ] Notification  [ ] Event-carried state transfer  [ ] Event sourcing

## When this event fires

One sentence describing the business fact that has occurred. Not the UI action, not the technical change — the fact.

> Example: "A payment for an order has been captured and settled with the acquirer."

## Preconditions / state the event signals

- `<state>` — e.g., "Order was in `placed` status"
- `<state>` — e.g., "Payment succeeded at the acquirer"

## Consumers (known)

Who subscribes? What do they do in reaction?

| Consumer | Reaction |
|---|---|
| `<consumer>` | `<reaction>` |
| `<consumer>` | `<reaction>` |

Notifying them before publishing changes the conversation from "we broke your code" to "we agreed on this."

## Envelope

Uses the standard envelope (see `assets/event-envelope.schema.json`). Producer fills:
- `source`: `<service.name>`
- `type`: `<EventName>`
- `version`: `1`
- `occurredAt`: server time when the fact became true
- `causationId`: the id of the command or event that directly caused this
- `correlationId`: the id of the root event/command in the flow

## Data shape

```json
{
  "data": {
    "<field>": "<type or example>",
    "<field>": { "<sub-field>": "<type>" }
  }
}
```

JSON Schema (or Avro / Protobuf) file: `schemas/<event-name>.v1.json`.

## Design rules applied

- [ ] Every referenced entity carries its stable id (not display strings).
- [ ] Monetary amounts are `{ currency, minor }`.
- [ ] Timestamps are ISO-8601 UTC.
- [ ] No secrets; no PII unless explicitly classified and approved.
- [ ] Payload size ≤ 256 KB in realistic worst case.
- [ ] No embedded state machines (one fact per event).

## Topic

- **Topic name:** `<context>.<event-name>.v1`
- **Partition key:** `<aggregateId>`
- **Compatibility regime:** [ ] BACKWARD  [ ] FORWARD  [ ] FULL  [ ] FULL_TRANSITIVE (recommended for mature systems)
- **Retention:** [ ] Functional (N days) [ ] Compacted [ ] Retained forever (event-sourced)

## Tests to include with the PR

- [ ] Aggregate unit test: given prior events, when command, then this event emitted.
- [ ] Schema validates a realistic sample (`scripts/validate-event-schema.py`).
- [ ] Schema compatibility check passes (CI).
- [ ] Integration test: event travels through outbox → relay → broker → test consumer.
- [ ] Idempotency: handler applied twice produces same state.

## Compensating actions (for saga steps only)

If this event is part of a saga step, what is the compensation?

- Compensation command: `<CompensateX>`
- Compensation event: `<XCompensated>`
- Idempotent: [ ] yes [ ] no — if no, document how double-invocation is avoided.

## Security and data classification

- Data classification: [ ] Public [ ] Internal [ ] Confidential [ ] Restricted (PII/PCI/PHI)
- If Restricted: topic ACLs, retention limit, encryption at rest details here.
