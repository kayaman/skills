# Event Schema — Reference

Load this when designing a new event, modifying an existing one, or setting up a schema registry and CI compatibility gate.

Sources: Adam Bellemare, *Building Event-Driven Microservices, 2nd Edition* (O'Reilly); Ben Stopford, *Designing Event-Driven Systems* (O'Reilly); Martin Kleppmann & Chris Riccomini, *Designing Data-Intensive Applications, 2nd Edition* (O'Reilly); Ekaterina Gorshkova, *Kafka for Architects* (Manning/O'Reilly); Michael L. Perry, *The Art of Immutable Architecture* (O'Reilly).

---

## 1. The envelope

Every event, regardless of broker or format, carries an envelope around the domain payload. The envelope exists so consumers can deduplicate, trace, and evolve without coordinating with the producer.

Canonical fields and what they are for:

| Field | Purpose | Required? |
|---|---|---|
| `id` | Unique per event. Consumers dedupe on this. UUIDv7 or ULID — both are sortable by creation time, which is how you want to scan a store. | Yes |
| `type` | The event name. Past tense, PascalCase, unique across the system. `OrderPaid`, not `order-paid` or `PaidEvent`. | Yes |
| `version` | Integer, starts at 1, bumps on breaking changes. The combination `type@version` identifies the schema. | Yes |
| `source` | Stable identifier for the producer. `payments.service` or `us-east-1.orders` — whatever is stable across deployments. | Yes |
| `occurredAt` | ISO-8601 UTC, millisecond precision. This is *when the fact became true*, not when the event was published. | Yes |
| `publishedAt` | Optional; when the event was handed to the broker. Useful for latency metrics, never for ordering. | No |
| `causationId` | The `id` of the command or event that directly caused this one. Forms a DAG for root-cause analysis. | Yes (where a cause exists) |
| `correlationId` | The `id` of the root event/command that started the flow. Stays constant through the saga. | Yes |
| `data` | The domain payload. Schema evolves under the rules below. | Yes |
| `metadata` | Optional bag for tracing (`traceparent`), tenancy (`tenantId`), or actor (`userId`). Keep it flat. | No |

See `assets/event-envelope.schema.json` for the canonical JSON Schema.

### Why the envelope is not optional

Without `id`, consumers cannot deduplicate → at-least-once becomes at-many-times.
Without `correlationId` + `causationId`, distributed tracing degrades to grep-by-guess. Adding them retroactively is expensive because every existing producer needs updating.

The envelope is a one-time cost. Pay it once, benefit forever.

---

## 2. Naming

**Events: past tense, PascalCase, scoped to one aggregate.**

Good: `OrderPlaced`, `PaymentCaptured`, `InvoiceVoided`, `UserEmailChanged`.

Bad:
- `UpdateUser` — imperative, looks like a command.
- `OrderUpdated` — present tense of a passive verb, and "updated" says nothing about what changed. Split into the specific facts: `OrderAddressChanged`, `OrderLineAdded`.
- `UserEvent` — not a fact; a type discriminator pretending to be an event.
- `order_created` — snake case fights every consumer's deserializer. Pick one.

**Topics: lowercase-hyphen-and-dot, versioned.**

`payments.order-paid.v1` — producer-qualified so you can scan topics by domain. `v1` in the topic name is a cheap way to signal breaking migrations (see §5).

**Commands: imperative, PascalCase.** `PlaceOrder`, `CaptureEtPayment`. Commands travel on request/response channels or command topics, not event topics. Mixing commands and events on one topic is a categorical error.

(Khononov, *Learning DDD*; Bellemare, *Building Event-Driven Microservices, 2e*.)

---

## 3. Payload rules

### 3.1 Stable identifiers first

Every referenced entity carries its stable id. Display strings are never sufficient.

```json
{ "customerId": "cus_7Qk2", "customerName": "Ana Souza" }   // ok
{ "customerName": "Ana Souza" }                              // will break on rename
```

### 3.2 Monetary amounts as (currency, minor_units)

Floats lose pennies. Always:

```json
{ "amount": { "currency": "BRL", "minor": 42900 } }  // R$429.00
```

### 3.3 Timestamps as ISO-8601 UTC

No local time zones. No epoch seconds disguised as timestamps. If the consumer wants local time, it does the conversion.

### 3.4 No embedded state machines

Do not stuff a full state history into one event:

```json
// anti-pattern — this is really three events pretending to be one
{ "type": "OrderChanged",
  "oldStatus": "placed", "newStatus": "paid",
  "oldTotal": 100, "newTotal": 120, "lineChanges": […] }
```

Emit `OrderPaid`, `OrderTotalRecalculated`, `OrderLineAdded` separately. Each is a single fact. Consumers that care about one do not have to parse all three.

### 3.5 No secrets, no PII unless you meant to

Event streams are often retained longer than you think, copied across environments, and read by many teams. Encrypt or omit secrets; classify PII explicitly and route it to a dedicated, access-controlled topic if you keep it in-band at all. (Stopford, *Designing Event-Driven Systems*.)

### 3.6 Size discipline

Soft budget: 1 MB per event (most brokers' default ceiling). Hard warning above 256 KB — most events that large are carrying claims that belong in storage. Use claim-check (PATTERNS.md §6).

---

## 4. Format choice: Avro vs Protobuf vs JSON Schema

There is no universally correct answer. The choice is constrained by the broker, the tooling, and the team's polyglot level.

| Format | Strengths | Weaknesses |
|---|---|---|
| **Avro** | Compact binary; schema evolution rules baked in; strong schema registry story with Kafka. | Schema must be available at read time (Confluent Schema Registry is the de facto). JSON debugging is awkward. |
| **Protobuf** | Compact; strongly typed; great polyglot code generation; schema evolution via tag numbers. | Enum defaults can trip you up; no built-in schema registry (bring your own). |
| **JSON Schema** | Human-readable, debuggable, wire format is the payload itself. No code gen needed. | Largest on the wire; evolution rules are whatever your tooling enforces — which is often nothing. |

**Rule of thumb.**

- New system on Kafka + polyglot consumers → Avro + Confluent Schema Registry.
- New system where debugging and simplicity dominate, single language stack → JSON Schema validated in CI.
- Must integrate with gRPC-heavy ecosystem → Protobuf (the schema is already there).

The format matters less than **enforcing the schema on every publish and on every consume, and running the compatibility gate in CI.** A consistently-enforced JSON Schema beats a loosely-enforced Avro registry. (Bellemare, *Building Event-Driven Microservices, 2e*; Gorshkova, *Kafka for Architects*.)

---

## 5. Evolution rules

Once a topic has consumers, the schema is a public API. Changes happen under one of three compatibility regimes.

### 5.1 Backward compatible (new producer → old consumer works)

**Allowed:**
- Add a new optional field (default must be sensible for old consumers).
- Widen a numeric type (`int32 → int64`) in formats that permit it.
- Add a new enum value *only if* consumers handle unknowns gracefully (Protobuf open enums are fine; Avro closed enums are not — widening an enum is a breaking change).

**Not allowed:**
- Remove a field old consumers read.
- Rename a field.
- Tighten a type (`string → int`).
- Change semantics of an existing field.

### 5.2 Forward compatible (old producer → new consumer works)

Mirror image of backward: old clients keep producing the v1 shape; new consumers ignore fields they do not know. Required for rolling deployments where consumers upgrade first.

### 5.3 Full compatible (both)

The union of the two. This is the regime to default to — it makes deployment orderings irrelevant.

### 5.4 Breaking change — when unavoidable

Rarely, you have to actually break the contract (e.g., the domain changed, the field was always wrong). The procedure:

1. Bump `version` on the event type (`OrderPaid v1 → v2`) or bump the topic (`payments.order-paid.v1 → …v2`).
2. Producers dual-write v1 and v2 for a deprecation window.
3. Consumers migrate from v1 to v2 at their own pace, within the window.
4. After the window, producers drop v1 and the v1 topic is retained for history but not written.

If you find yourself breaking a schema every quarter, the schema was wrong in design, not evolution. Revisit the ubiquitous language of the domain.

(Kleppmann & Riccomini, *DDIA, 2e*, ch. 4 — schema evolution in Avro/Protobuf/Thrift.)

---

## 6. Schema registry

A schema registry is a single source of truth for every schema in the system, keyed by subject (typically `<topic>-value` and `<topic>-key`).

**What it must do:**

- Store every schema version published for a subject.
- Validate new schema submissions against the subject's compatibility rule (reject incompatible changes).
- Serve schemas to producers and consumers at serialization / deserialization time.

**What it must not be:**

- A substitute for explicit event design. A registry will happily accept a mediocre schema; it enforces evolution rules, not quality.
- A runtime dependency you can lose visibility of. Producers often cache schemas locally; when the registry is down, they should fail closed — not publish schemaless blobs.

**CI gate.** On every PR that touches a schema:

```bash
# pseudo-CI step
for subject in $(changed-schemas); do
  schema-registry compatibility-check \
    --subject "$subject" \
    --schema "./schemas/$subject.avsc" \
    --compatibility FULL_TRANSITIVE || exit 1
done
```

`FULL_TRANSITIVE` means compatible with **all** prior versions, not just the immediate predecessor. That is the regime you want in a mature system. (Gorshkova, *Kafka for Architects*.)

---

## 7. Examples — good and bad

### 7.1 A good `OrderPaid` event (JSON Schema flavour)

```json
{
  "id": "01H8ZXC5TJ3VQ2K4N5RX0Y7W8A",
  "type": "OrderPaid",
  "version": 1,
  "source": "payments.service",
  "occurredAt": "2026-04-23T02:45:12.413Z",
  "causationId": "01H8ZXC5S3J…",
  "correlationId": "01H8ZXC5R1…",
  "data": {
    "orderId": "ord_7Qk2",
    "customerId": "cus_4Tg9",
    "amount": { "currency": "BRL", "minor": 42900 },
    "paidAt": "2026-04-23T02:45:11.900Z",
    "paymentMethod": { "type": "pix", "endToEndId": "E12345678202604230245abc" }
  }
}
```

Why it is good:
- Past tense, scoped to `Order`, identifiable payload.
- Full envelope, enabling dedupe and tracing.
- Money is `{currency, minor}`.
- `paymentMethod` is a nested object — future payment types add new fields next to `type`, not new top-level shapes.

### 7.2 Two bad events and the fix

**Bad — imperative and ambiguous:**

```json
{ "type": "update_order", "orderId": "…", "newStatus": "paid" }
```

Problems: imperative; the new status says "paid" but there is no amount, no payment method, nothing a consumer needs. It is a command pretending to be an event.

**Fix:** replace with `OrderPaid` (as in 7.1).

**Bad — everything-event:**

```json
{ "type": "UserUpdated", "userId": "…",
  "fields": { "email": "…", "address": "…", "tier": "…", "marketingOptIn": true } }
```

Problems: "updated" is a category, not a fact. Consumers that care only about email changes must parse and diff. Compatibility is nightmare — adding a new optional `fields.X` means every consumer's diff logic might miss it.

**Fix:** emit specific events — `UserEmailChanged`, `UserAddressChanged`, `UserTierChanged`, `UserMarketingOptInToggled`. Consumers subscribe to the ones they care about.

---

## 8. Checklist before you publish a new schema

```
- [ ] Name is past tense, PascalCase, scoped to one aggregate
- [ ] Envelope fields complete: id, type, version, source, occurredAt, causationId, correlationId
- [ ] All referenced entities carry a stable id
- [ ] Monetary amounts are {currency, minor}; timestamps are ISO-8601 UTC
- [ ] No PII unless explicitly classified; no secrets
- [ ] Payload size < 256 KB in the realistic worst case (otherwise claim-check)
- [ ] Format choice is consistent with the rest of the platform
- [ ] Compatibility regime declared for the topic (BACKWARD / FORWARD / FULL / FULL_TRANSITIVE)
- [ ] CI gate runs compatibility check on PR
- [ ] Sample instance validates against the schema (`scripts/validate-event-schema.py`)
- [ ] At least two downstream consumers have been pinged; they have signed off on payload shape
```

If the check fails, fix and re-run. Do not publish an event whose schema has not gone through CI.
