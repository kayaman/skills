# Sagas — Reference

Load this when designing a multi-step workflow that spans services or bounded contexts. A saga is the event-driven answer to "I wish I could use a distributed transaction" — you cannot, so you compose a sequence of local transactions with compensating actions on failure.

Sources: Chris Richardson, *Microservices Patterns* (O'Reilly), chapters 4–6; Sam Newman, *Building Microservices, 2nd Edition* (O'Reilly); Vaughn Vernon, *Implementing Domain-Driven Design* (O'Reilly); Bernd Ruecker, *Practical Process Automation* (O'Reilly); Jim Gray & Andreas Reuter, *Transaction Processing* (the original saga paper context).

---

## 1. Two flavours

### Choreography

Each participant reacts to events and emits its own. No coordinator.

```
Order service           Payment service         Shipping service
     |                        |                        |
     |── OrderPlaced ─────────▶                        |
     |                        |── PaymentCaptured ─────▶
     |                        |                        |── OrderShipped
     |◀───────────── OrderShipped ───────────────────────|
```

- **Lowest coupling**: no service needs to know any other by name; they speak through events on topics.
- **Hardest to reason about** once the graph exceeds three or four participants. You have no single place to look to answer "where is order 7Qk2 right now?"
- **Compensation is painful**: each step must know which prior steps to undo, which couples services back together via the reverse dependency.

### Orchestration

A named process manager (the *orchestrator*, sometimes "saga execution coordinator") issues commands and consumes replies. It owns the state machine.

```
Orchestrator          Order          Payment          Shipping
    |                   |                |                |
    |── CreateOrder ────▶                |                |
    |◀─ OrderCreated ───|                |                |
    |── CapturePayment ─────────────────▶|                |
    |◀─ PaymentCaptured ─────────────────|                |
    |── ScheduleShipment ────────────────────────────────▶|
    |◀─ ShipmentScheduled ────────────────────────────────|
    |── Done
```

- **Single place to look**: the orchestrator's state is the saga state. Tracing, debugging, and monitoring converge.
- **Higher coupling**: the orchestrator knows all participants. But that coupling is honest and local — the orchestrator is a service whose job *is* to know the flow.
- **Compensations are centralised**: the state machine includes "on failure, send CancelShipment, then RefundPayment, then MarkOrderCancelled."

### Decision rule

- **≤ 2 participants, no compensation**: choreography is fine.
- **Compensating logic or > 2 participants**: orchestration. Pay the coupling cost to get the legibility. (Newman, *Building Microservices, 2e*.)
- **Long-running (hours, days)**: orchestration, and use a workflow engine (Temporal, Camunda Zeebe, AWS Step Functions) — not a hand-rolled state machine. Hand-rolled long-running workflows reinvent retry, timers, and idempotency poorly.

---

## 2. Compensating transactions

A compensation is *not* a rollback. Rollback assumes atomicity you no longer have. A compensation is **a new forward transaction that semantically undoes a prior one**.

| Forward | Compensation |
|---|---|
| `CapturePayment` → charges customer | `RefundPayment` → refunds the charge |
| `ReserveInventory` → decrements stock | `ReleaseInventory` → increments stock |
| `SendOrderEmail` | No compensation possible (email cannot be un-sent) — mitigate by delaying or batching |

**Design rules:**

- Every forward step with external effect has a matched compensation, or you document explicitly that it is irreversible.
- Compensations must themselves be idempotent. Network failures during compensation will retry it.
- Compensations run in reverse order of the forward steps (LIFO). The orchestrator tracks which steps completed.
- Some domains admit only *semantic* compensation (you cannot refund time, but you can credit a customer). Work with the business to define the semantic inverse.

(Richardson, *Microservices Patterns*, ch. 4.)

---

## 3. Orchestration — a concrete pattern

### State machine

The orchestrator's persistent state per saga instance:

```
SagaInstance {
  id:              UUID
  type:            'PlaceOrderSaga'
  correlationId:   UUID          // same as the triggering command's id
  currentStep:     enum          // 'CreatingOrder' | 'CapturingPayment' | …
  state:           'Running' | 'Completed' | 'Compensating' | 'Failed'
  completedSteps:  [Step…]        // for reverse-order compensation
  createdAt, updatedAt
  payload:         JSONB          // saga variables (orderId, paymentId, shipmentId, …)
}
```

Stored in the orchestrator's own DB. Mutated under the standard outbox pattern (PATTERNS.md §3) — every state transition is atomic with the command it emits.

### Command/reply over events

Commands and replies travel over dedicated per-participant channels:

- `payments.commands` — orchestrator → payment service.
- `payments.replies` — payment service → orchestrator.
- Messages carry `correlationId = sagaInstanceId`, so the orchestrator routes replies back to the right instance.

Alternative: gRPC for commands, events for replies. This works when latency matters and the command handler is not itself long-running.

### Timeouts

Every orchestrator step has a timeout. If the reply does not arrive, treat it as failure and compensate (or retry, based on the step's idempotency). Without timeouts, one lost message hangs the saga forever.

Use timers the workflow engine provides. Do not rely on "I will scan the DB for stuck sagas" — that works until you forget to run the scanner.

### Compensation flow

```
on Failure(step):
  state = 'Compensating'
  for step in reversed(completedSteps):
    emit compensationCommand(step)
    await compensationReply(step)
  state = 'Failed'
```

Record the failure reason. A failed saga is an incident — someone looks at it.

---

## 4. Choreography — a concrete pattern

Minimal ceremony: each service subscribes to topics, applies the outbox pattern per local transaction, emits the next event.

**Trace as the only coordinator.** Every event carries the saga's `correlationId`. Without that, debugging is impossible — you cannot ask "show me every event in saga X".

**Failure:** each service emits a "failed" event (`PaymentFailed`, `InventoryUnavailable`). Upstream services that subscribed compensate their own state. This is a different event for each possible failure path, and the fan-out grows quadratically — which is why choreography degrades fast past 3–4 services.

**Reality check:** if you find yourself drawing the event flow on three sticky notes and the arrows tangle, switch to orchestration. The instinct "but orchestration adds a service!" usually mistakes operational overhead (running one more service) for architectural overhead (one more well-defined boundary). The orchestrator buys you clarity, observability, and compensable semantics for a modest ops bill.

---

## 5. Request–reply over events — almost always wrong

A recurring anti-pattern: service A publishes `UserLookupRequested`, service B replies with `UserLookupReplied` on a topic that A subscribes to, correlated by `requestId`. A blocks (logically) until the reply.

**Problems:**

1. You have reinvented synchronous RPC with added latency (broker hop, consumer poll, dispatch) and worse debugging (events in two places instead of a single call stack).
2. Back-pressure leaks: if B is slow, A accumulates pending requests.
3. Client-side timeouts become a race with broker delivery delays, producing nondeterministic failures.

**When it is acceptable:** the "reply" is itself a legitimate business event that others might also care about (e.g., `ScoreCalculated` — B calculated a score, A asked for it, but the credit-risk team also wants it). In that case the "reply" was always an event; A is just one of its consumers.

**When it is not acceptable:** 99% of the time. Use a synchronous API call. If you want decoupling, cache the lookup or materialize a local read model. (Richardson, *Microservices Patterns*.)

---

## 6. Process managers and workflow engines

The industrial form of the orchestrator. A *workflow engine* (Temporal, Camunda 8/Zeebe, AWS Step Functions, Azure Durable Functions) provides:

- Durable timers (schedule a compensation in 30 days).
- Automatic retry with configurable backoff.
- Visibility: a UI that shows "saga X is on step 3, waiting for PaymentCaptured."
- Replay semantics: restart the engine and workflows resume from their last durable step.

**Use a workflow engine when:**

- The saga spans more than seconds (hours, days, human approvals).
- Compensations must survive service restarts and deployments.
- You need to visualize and audit the process with non-engineers.

**Do not use a workflow engine when:**

- The workflow is under one second and fits in a single service's state machine. Adding Temporal to wrap three in-process steps is over-engineering. (Ruecker, *Practical Process Automation*.)

---

## 7. Correlation and causation — observability of sagas

Every event in the saga carries:

- `correlationId` — the saga instance id. Constant through the whole flow.
- `causationId` — the id of the event or command that directly caused this one.

With both, you can:

- Filter logs to a single saga: `grep correlationId=01H8ZX…`.
- Rebuild the causation DAG: `causationId` edges form a graph; visualize it for debugging.
- Alert on saga latency: if the time between the first and last event exceeds the SLO, page.

Losing `correlationId` midway through a saga (a handler forgets to propagate it) is the most common observability bug. Linting or a middleware that rejects outgoing messages without a correlation id is worth the small friction.

---

## 8. Example — order placement saga (orchestration)

Pseudocode shape, not a complete runnable example; adapt to your stack.

```python
class PlaceOrderSaga:
    steps = [
        ("CreateOrder",       "orders.commands",    "OrderCreated"),
        ("ReserveInventory",  "inventory.commands", "InventoryReserved"),
        ("CapturePayment",    "payments.commands",  "PaymentCaptured"),
        ("ScheduleShipment",  "shipping.commands",  "ShipmentScheduled"),
    ]
    compensations = {
        "CreateOrder":      "CancelOrder",
        "ReserveInventory": "ReleaseInventory",
        "CapturePayment":   "RefundPayment",
        # ScheduleShipment has no compensation — it runs last; if it fails, earlier steps compensate
    }

    def start(self, cmd: PlaceOrder) -> None:
        self.persist_instance(correlationId=cmd.id, payload=cmd.payload)
        self.emit_next()

    def on_reply(self, reply: Event) -> None:
        step = self.current_step()
        if reply.type == step.success_event:
            self.record_completed(step)
            self.emit_next_or_finish()
        else:
            self.begin_compensation()

    def begin_compensation(self) -> None:
        for step in reversed(self.completed_steps):
            self.emit(self.compensations[step.name])
            await self.wait_for_reply()
        self.state = "Failed"
```

The outbox wraps every `emit` — the state mutation and the outgoing command are in the same local transaction. Idempotency on `reply.id` protects against duplicate replies.

---

## 9. Failure modes and how to detect each

| Failure | Symptom | Fix |
|---|---|---|
| Step command lost | Saga hangs in step N; no reply ever comes | Timeouts + retry; eventually compensate |
| Reply lost | Same as above | Same — orchestrator does not distinguish |
| Duplicate reply | Saga advances twice | Dedupe replies on `reply.id` |
| Orchestrator crash mid-step | State uncertain on restart | Outbox + durable state — restart resumes from last committed step |
| Compensation fails | Saga stuck in "Compensating" | Retry with backoff; if persistent, alert and manual intervention |
| Cascading timeout | Downstream slowed → more sagas in flight → consumer overwhelmed | Back-pressure at the orchestrator: bounded in-flight; reject new starts under load |

---

## 10. Checklist for a new saga

```
- [ ] Chosen orchestration (default) or choreography (only if 2-step, no compensation, no long-running timer)
- [ ] State machine documented — every step named, every transition drawn
- [ ] Every step has a compensation defined (or is documented as irreversible)
- [ ] Every step has a timeout
- [ ] All outgoing commands and events carry correlationId = sagaInstanceId
- [ ] causationId propagates step-to-step
- [ ] Orchestrator state persisted via outbox (state change + outgoing command atomic)
- [ ] Replies deduped on reply.id
- [ ] Compensations are idempotent
- [ ] Failure path exits to a well-named terminal state (Completed | Failed); no in-between "Unknown"
- [ ] Dashboard shows in-flight sagas by state + age
- [ ] Tests: happy path; each step's failure → compensation; duplicate reply; lost reply (timeout); orchestrator crash mid-step
```

If the workflow is serious, consider a workflow engine before rolling your own — §6.
