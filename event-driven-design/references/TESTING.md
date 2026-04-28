# Testing Event-Driven Systems — Reference

Load this when writing or reviewing tests for event-driven code. The test pyramid for EDA differs from synchronous systems: the expensive integration tests are less substitutable because so many bugs live in the seams.

Sources: Harry Percival & Bob Gregory, *Architecture Patterns with Python* (O'Reilly), chapters 5–9; Adam Bellemare, *Building Event-Driven Microservices, 2nd Edition* (O'Reilly), chapter 15; Chris Richardson, *Microservices Patterns* (O'Reilly), chapter 10; Sam Newman, *Building Microservices, 2nd Edition* (O'Reilly), chapter 9; Vaughn Vernon, *Implementing Domain-Driven Design* (O'Reilly).

---

## 1. The minimum viable test pyramid for EDA

For every event handler, aggregate, or saga, the repo should contain at least:

1. **Unit test on the aggregate / handler** — given prior events, when command, then new events. Fast, many.
2. **Schema compatibility test** — runs in CI on every PR that touches a schema.
3. **Consumer contract test** — the consumer's expectations encoded as a contract; CI fails if the producer's schema diverges.
4. **Integration test with a real broker** — via Testcontainers or the broker's embedded mode; validates serialization, partitioning, idempotency end-to-end.
5. **Replay test** — drop a projection, replay from offset 0, assert the end state matches live state.

Skip any of these at your peril: unit tests alone miss serialization bugs; integration tests alone miss every logic bug they are too slow to cover.

---

## 2. Unit tests — given / when / then on aggregates

The canonical shape for testing an aggregate is a triple: prior events, command, expected new events. The aggregate's internals stay private.

### Python (Percival & Gregory style)

```python
# tests/test_order_aggregate.py
from orders.domain import Order, PlaceOrder, OrderPlaced, PayOrder, OrderPaid
from decimal import Decimal

def test_placing_an_order_emits_OrderPlaced():
    # Given no prior events
    order = Order(events=[])

    # When
    new_events = order.handle(PlaceOrder(
        order_id="ord_7Qk2",
        customer_id="cus_4Tg9",
        lines=[{"sku": "SKU-1", "qty": 2, "price_minor": 21450}],
    ))

    # Then
    assert len(new_events) == 1
    assert isinstance(new_events[0], OrderPlaced)
    assert new_events[0].order_id == "ord_7Qk2"
    assert new_events[0].total_minor == 42900

def test_paying_a_placed_order_emits_OrderPaid():
    # Given
    order = Order(events=[
        OrderPlaced(order_id="ord_7Qk2", customer_id="cus_4Tg9",
                    lines=[{"sku":"SKU-1","qty":2,"price_minor":21450}],
                    total_minor=42900, placed_at="2026-04-23T00:00:00Z"),
    ])

    # When
    new_events = order.handle(PayOrder(order_id="ord_7Qk2",
                                       amount_minor=42900,
                                       currency="BRL"))

    # Then
    assert len(new_events) == 1
    assert isinstance(new_events[0], OrderPaid)

def test_paying_wrong_amount_raises_DomainError():
    order = Order(events=[
        OrderPlaced(order_id="ord_7Qk2", customer_id="cus_4Tg9",
                    lines=[{"sku":"SKU-1","qty":2,"price_minor":21450}],
                    total_minor=42900, placed_at="2026-04-23T00:00:00Z"),
    ])
    with pytest.raises(DomainError, match="amount mismatch"):
        order.handle(PayOrder(order_id="ord_7Qk2",
                              amount_minor=10000,
                              currency="BRL"))
```

Key properties:
- No mocks. The aggregate takes events in, emits events out. Pure.
- State is not asserted directly — only the events it emitted. State is implementation detail.
- One test per domain rule. Readable, grep-able.

### Java/Kotlin (Axon / Event Sourcing style)

```java
// tests/OrderAggregateTest.java
import static org.assertj.core.api.Assertions.*;

@Test
void payingPlacedOrderEmitsOrderPaid() {
    var events = List.of(
        new OrderPlaced("ord_7Qk2", "cus_4Tg9", 42900, "BRL", Instant.parse("2026-04-23T00:00:00Z"))
    );

    var order = Order.from(events);
    var newEvents = order.handle(new PayOrder("ord_7Qk2", 42900, "BRL"));

    assertThat(newEvents).hasSize(1);
    assertThat(newEvents.get(0)).isInstanceOf(OrderPaid.class);
}
```

---

## 3. Testing consumers (event handlers)

A consumer's job is: "given an event, mutate state and emit zero or more new events (via outbox)." Test it with the event as input and inspect both the state change and the outbox.

```python
def test_consumer_records_payment_and_triggers_shipping(db):
    # Given an order exists
    db.execute("INSERT INTO orders(id, status) VALUES ('ord_7Qk2', 'placed')")

    event = OrderPaid(
        envelope=Envelope(id="evt_1", type="OrderPaid", version=1, source="payments",
                          occurredAt="…", correlationId="cor_1", causationId="cmd_1"),
        data=OrderPaidData(order_id="ord_7Qk2", amount_minor=42900, currency="BRL"),
    )

    # When
    handler = OrderPaidHandler(db=db)
    handler.handle(event)

    # Then — state change
    assert db.fetch_one("SELECT status FROM orders WHERE id='ord_7Qk2'").status == "paid"

    # Then — outbox row
    outbox_row = db.fetch_one("SELECT * FROM outbox WHERE correlation_id = 'cor_1'")
    assert outbox_row.type == "ShipmentRequested"
    assert outbox_row.causation_id == "evt_1"   # proper causation chain
```

### Test idempotency explicitly

```python
def test_consumer_is_idempotent_when_event_redelivered(db):
    event = make_OrderPaid(order_id="ord_7Qk2", event_id="evt_1")
    handler = OrderPaidHandler(db=db)

    handler.handle(event)
    handler.handle(event)   # redelivery

    # State applied exactly once
    assert db.count("SELECT * FROM orders WHERE id='ord_7Qk2' AND status='paid'") == 1
    # Only one downstream command emitted
    assert db.count("SELECT * FROM outbox WHERE causation_id='evt_1'") == 1
```

Without this test, at-least-once delivery will cause double-charges in production and you will only find out from support tickets.

---

## 4. Schema compatibility tests (CI gate)

Put the schema in the repo. On every PR that touches a schema, the CI runs a compatibility check against the registered version.

### JSON Schema — Python example

```python
# tests/test_schema_compatibility.py
import json
from jsonschema import Draft202012Validator

def test_sample_event_validates_against_schema():
    with open("schemas/order-paid.v1.json") as f:
        schema = json.load(f)
    with open("schemas/examples/order-paid.example.json") as f:
        example = json.load(f)
    Draft202012Validator(schema).validate(example)

def test_adding_optional_field_is_backward_compatible():
    old = json.load(open("schemas/order-paid.v1.json"))
    new = json.load(open("schemas/order-paid.v1-next.json"))
    # A new optional field is allowed; no required-field added, no field removed
    old_required = set(old["properties"]["data"]["required"])
    new_required = set(new["properties"]["data"]["required"])
    assert new_required <= old_required   # new required is subset
```

### Avro / Confluent Schema Registry

```bash
# ci/check-schema.sh
for f in schemas/*.avsc; do
  subject=$(basename "$f" .avsc)-value
  curl --fail -X POST \
    -H "Content-Type: application/vnd.schemaregistry.v1+json" \
    --data "{\"schema\": $(jq -Rs . < "$f")}" \
    "$SCHEMA_REGISTRY/compatibility/subjects/$subject/versions/latest"
done
```

The CI fails if any change is incompatible at the declared compatibility level.

---

## 5. Consumer-driven contract tests (Pact)

Contract tests let the consumer declare what it expects; the producer's CI verifies it still meets every consumer's expectations.

```python
# consumer side — tests/test_payment_consumer_contract.py
import pact

@pact.provider("payments.service").consumer("orders.service")
class TestPaymentContract:
    def test_order_paid_contains_customer_and_amount(self):
        expected_event = {
            "type": "OrderPaid",
            "version": 1,
            "data": {
                "orderId": pact.Like("ord_7Qk2"),
                "customerId": pact.Like("cus_4Tg9"),
                "amount": {
                    "currency": pact.Term(r"^[A-Z]{3}$", "BRL"),
                    "minor": pact.Like(42900),
                },
            },
        }
        self.consumer_expects(expected_event)
```

The producer's CI pulls these pacts and runs them against a real producer build. If the producer changes a field the consumer depends on, producer's CI fails — before the event is published to production. (Newman, *Building Microservices, 2e*, ch. 9; Richardson, *Microservices Patterns*, ch. 10.)

**Limitation.** Contract tests check shape and sample values. They do not catch semantic drift (field name unchanged, meaning changed). Pair with integration tests.

---

## 6. Integration tests with Testcontainers

A local ephemeral broker gives you the serialization, partitioning, and at-least-once behaviour of production without staging.

### Kafka + Testcontainers (Python)

```python
# tests/integration/test_order_flow.py
import pytest
from testcontainers.kafka import KafkaContainer
from kafka import KafkaProducer, KafkaConsumer

@pytest.fixture(scope="session")
def kafka():
    with KafkaContainer() as kc:
        yield kc.get_bootstrap_server()

def test_placing_order_produces_event_consumed_by_shipping(kafka):
    producer = KafkaProducer(bootstrap_servers=kafka, value_serializer=serialize_event)
    consumer = KafkaConsumer("orders", bootstrap_servers=kafka,
                             value_deserializer=deserialize_event,
                             auto_offset_reset="earliest")

    # When the order service publishes
    producer.send("orders", make_OrderPlaced(order_id="ord_1"))
    producer.flush()

    # Then the shipping consumer sees it
    msg = next(consumer)
    assert msg.value.type == "OrderPlaced"
    assert msg.value.data.orderId == "ord_1"
```

### Kafka + Testcontainers (Java)

```java
@Testcontainers
class OrderFlowIT {
    @Container
    static KafkaContainer kafka = new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.6.0"));

    @Test
    void placingOrderProducesEvent() {
        var bootstrap = kafka.getBootstrapServers();
        // ... produce, consume, assert
    }
}
```

### What the integration test must cover

- Full serialization / deserialization round trip through the real client library.
- Partition key assignment — the right partition receives events for the right aggregate id.
- Consumer group offset commit — after a restart, the consumer resumes where it left off and does not re-process committed events *unless* they are still within the idempotency window.
- Outbox relay → broker flow: write a state change + outbox row, observe the event arrives on the topic.

Keep integration tests few and high-signal. A dozen happy-path tests plus five failure-path tests (retry, duplicate, out-of-order, large payload, poisoned message) buy more than a hundred permutations. (Bellemare, *Building Event-Driven Microservices, 2e*, ch. 15.)

---

## 7. Chaos tests and failure injection

At-least-once delivery is a promise; the only way to verify your consumer handles it is to induce redelivery.

```python
def test_consumer_still_correct_after_redelivery_storm(kafka):
    # Publish the same event 10x (simulating broker redelivery)
    for _ in range(10):
        producer.send("orders", make_OrderPlaced(order_id="ord_1", event_id="evt_X"))

    # Consumer runs
    run_consumer_until_lag_zero()

    # State is applied exactly once
    assert db.count("SELECT * FROM orders WHERE id='ord_1'") == 1
    assert db.count("SELECT * FROM outbox WHERE causation_id='evt_X'") == 1
```

Additional failure modes to simulate:

- **Out-of-order delivery.** Publish `OrderPaid` before `OrderPlaced`. Consumer must detect (causation missing, or sequence gap) and either buffer or dead-letter.
- **Broker unavailable.** Kill the container mid-publish. Producer's outbox keeps the event; relay retries when broker returns.
- **Poison message.** Publish a deliberately malformed event. Consumer must route it to DLQ, not crash-loop.
- **Slow consumer.** Pause the consumer; publish 10k events. Confirm no loss and that lag metrics surface the backlog.

---

## 8. Replay / backfill tests

If replay does not work in a test, it will not work in production.

```python
def test_projection_rebuild_from_zero_matches_live(db, kafka):
    # Given live projection in some state after N events
    live_state = snapshot_projection(db)

    # When we drop and replay
    db.execute("TRUNCATE order_projection")
    reset_consumer_offset("order-projection", "orders", 0)
    run_consumer_until_lag_zero()
    rebuilt_state = snapshot_projection(db)

    # Then rebuilt == live
    assert rebuilt_state == live_state
```

This test also doubles as a detector for non-deterministic projections (any use of `now()`, `random()`, or external HTTP will cause a mismatch).

---

## 9. Saga tests

For orchestrated sagas, test each branch of the state machine.

```python
def test_happy_path(orchestrator, fake_participants):
    orchestrator.start(PlaceOrder(order_id="ord_1", ...))
    fake_participants.reply("OrderCreated", success=True)
    fake_participants.reply("InventoryReserved", success=True)
    fake_participants.reply("PaymentCaptured", success=True)
    fake_participants.reply("ShipmentScheduled", success=True)

    assert orchestrator.state_of("ord_1") == "Completed"

def test_payment_fails_triggers_inventory_release_and_order_cancel(orchestrator, fake_participants):
    orchestrator.start(PlaceOrder(order_id="ord_1", ...))
    fake_participants.reply("OrderCreated", success=True)
    fake_participants.reply("InventoryReserved", success=True)
    fake_participants.reply("PaymentCaptured", success=False, reason="card_declined")

    # Compensations run in LIFO order
    assert fake_participants.sent_command("ReleaseInventory")
    assert fake_participants.sent_command("CancelOrder")
    assert orchestrator.state_of("ord_1") == "Failed"

def test_orchestrator_resumes_after_crash(orchestrator, db, kafka):
    orchestrator.start(PlaceOrder(order_id="ord_1", ...))
    reply_to("OrderCreated", success=True)
    # Simulate crash: kill + restart orchestrator process
    orchestrator.restart()
    reply_to("InventoryReserved", success=True)
    # … saga continues from where it was
    assert orchestrator.current_step("ord_1") == "CapturingPayment"
```

---

## 10. What NOT to test

- **Broker internals.** Kafka's own guarantees are not your test's job.
- **Implementation of the serializer library.** Assume Jackson / Serde / Avro works; test that your schema + sample produces expected bytes if you need to.
- **Every permutation of out-of-order events.** One representative test per ordering hazard is enough.
- **Mocks pretending to be a broker.** A mock broker lies politely about partitioning and ordering. Use Testcontainers.

---

## 11. Test review checklist

```
- [ ] Aggregate unit tests cover each domain rule — given prior events, when command, then new events
- [ ] Idempotency test for every consumer (same event delivered twice → single side effect)
- [ ] Schema compatibility test runs in CI on every PR touching schemas
- [ ] Consumer contract test exists for each (producer, consumer) pair
- [ ] At least one integration test per topic with a real broker (Testcontainers)
- [ ] Chaos test: redelivery storm, poison message, broker outage
- [ ] Replay test: drop projection + rebuild from offset 0 == live state
- [ ] Saga tests: happy path, each failure branch, crash-resume
- [ ] No mock broker in integration tier; no unit test touches the network
- [ ] Every test completes in < 30s individually; CI p95 < 10 min
```
