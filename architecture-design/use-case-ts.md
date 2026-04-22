# Template: TypeScript Use Case (Interactor)

A use case orchestrates domain operations to fulfill one user intent.
Lives in the application layer, depends only on ports, and knows
nothing about HTTP, SQL, or frameworks.

Copy and adapt. Replace `PlaceOrder` and command fields with the
concrete use case.

```typescript
// application/commands.ts
import type { CustomerId, OrderId } from "../domain/ids";
import type { LineItem } from "../domain/lineItem";

export type PlaceOrderCommand = {
  readonly customerId: CustomerId;
  readonly items: ReadonlyArray<LineItem>;
  readonly idempotencyKey?: string;
};
```

```typescript
// application/ports.ts
import type { OrderRepository } from "../domain/ports";
import type { DomainEvent } from "../domain/events";

/**
 * Transactional boundary + access to repositories.
 * withTransaction() runs the callback inside a transaction;
 * if the callback throws, the transaction is rolled back.
 */
export interface UnitOfWork {
  withTransaction<T>(
    work: (ctx: { readonly orders: OrderRepository }) => Promise<T>,
  ): Promise<T>;
}

export interface EventBus {
  publish(event: DomainEvent): Promise<void>;
}
```

```typescript
// application/placeOrder.ts
import type { OrderId } from "../domain/ids";
import { Order } from "../domain/order";

import type { PlaceOrderCommand } from "./commands";
import type { EventBus, UnitOfWork } from "./ports";
import { newOrderId } from "../domain/ids";

/**
 * Place a new order.
 *
 * Single responsibility: translate a PlaceOrderCommand into domain
 * operations, persist the result, and publish emitted events.
 */
export class PlaceOrder {
  constructor(
    private readonly uow: UnitOfWork,
    private readonly events: EventBus,
  ) {}

  async execute(cmd: PlaceOrderCommand): Promise<OrderId> {
    // 1. Enter transaction. Any thrown error rolls back.
    const { order, pendingEvents } = await this.uow.withTransaction(
      async ({ orders }) => {
        // 2. Domain operation. All invariants enforced inside.
        const id = newOrderId();
        const order = Order.place(id, cmd.customerId, cmd.items);

        // 3. Persist via the repository port.
        await orders.add(order);

        // 4. Events collected but NOT published inside the transaction.
        return { order, pendingEvents: order.pullEvents() };
      },
    );

    // 5. Publish after commit. At-least-once semantics — handlers
    //    must be idempotent (see event-driven.md).
    for (const event of pendingEvents) {
      await this.events.publish(event);
    }

    return order.id;
  }
}
```

---

## Composition root — wiring at startup

Use case is framework-free. Wire once at boot.

```typescript
// infrastructure/container.ts
import { PlaceOrder } from "../application/placeOrder";
import { SqlUnitOfWork } from "../adapters/repositories/sqlUnitOfWork";
import { KafkaEventBus } from "../adapters/messaging/kafkaEventBus";
import { db } from "./db";
import { kafka } from "./kafka";

export function buildPlaceOrder(): PlaceOrder {
  const uow = new SqlUnitOfWork(db);
  const bus = new KafkaEventBus(kafka);
  return new PlaceOrder(uow, bus);
}
```

---

## HTTP adapter — translating requests to commands

Controllers belong in `adapters/`, not in `application/`. They know
about HTTP; the use case does not.

```typescript
// adapters/http/placeOrderRoute.ts
import { type Request, type Response, Router } from "express";
import { z } from "zod";

import type { CustomerId } from "../../domain/ids";
import { makeLineItem } from "../../domain/lineItem";
import { makeMoney, type Currency } from "../../domain/money";
import type { PlaceOrderCommand } from "../../application/commands";

import { buildPlaceOrder } from "../../infrastructure/container";

const LineItemDTO = z.object({
  sku: z.string().min(1),
  quantity: z.coerce.bigint().positive(),
  unitPriceCents: z.coerce.bigint().positive(),
  currency: z.enum(["USD", "EUR", "BRL"]),
});

const PlaceOrderRequest = z.object({
  customerId: z.string().uuid(),
  items: z.array(LineItemDTO).min(1),
  idempotencyKey: z.string().optional(),
});

export const placeOrderRouter = Router();

placeOrderRouter.post("/orders", async (req: Request, res: Response) => {
  const parsed = PlaceOrderRequest.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ errors: parsed.error.format() });
  }

  // DTO → domain command at the boundary.
  const cmd: PlaceOrderCommand = {
    customerId: parsed.data.customerId as CustomerId,
    items: parsed.data.items.map((i) =>
      makeLineItem(i.sku, i.quantity,
        makeMoney(i.unitPriceCents, i.currency as Currency)),
    ),
    idempotencyKey: parsed.data.idempotencyKey,
  };

  try {
    const orderId = await buildPlaceOrder().execute(cmd);
    return res.status(201).json({ orderId });
  } catch (err) {
    if (err instanceof Error) {
      return res.status(400).json({ error: err.message });
    }
    throw err;
  }
});
```

---

## Testing — in-memory fakes, no framework

```typescript
// tests/application/placeOrder.test.ts
import { describe, expect, it } from "vitest";

import {
  newCustomerId,
  newOrderId,
  type OrderId,
} from "../../src/domain/ids";
import { makeLineItem } from "../../src/domain/lineItem";
import { makeMoney } from "../../src/domain/money";
import { Order } from "../../src/domain/order";
import type {
  DomainEvent,
  OrderPlaced,
} from "../../src/domain/events";
import type { OrderRepository } from "../../src/domain/ports";

import { PlaceOrder } from "../../src/application/placeOrder";
import type {
  EventBus,
  UnitOfWork,
} from "../../src/application/ports";

class InMemoryOrderRepository implements OrderRepository {
  private readonly store = new Map<OrderId, Order>();
  readonly added: Order[] = [];

  async get(id: OrderId): Promise<Order> {
    const o = this.store.get(id);
    if (!o) throw new Error(`Order ${id} not found`);
    return o;
  }

  async add(order: Order): Promise<void> {
    this.store.set(order.id, order);
    this.added.push(order);
  }

  async findByCustomer() {
    return [];
  }
}

class InMemoryUnitOfWork implements UnitOfWork {
  readonly orders = new InMemoryOrderRepository();
  committed = false;

  async withTransaction<T>(
    work: (ctx: { orders: InMemoryOrderRepository }) => Promise<T>,
  ): Promise<T> {
    const result = await work({ orders: this.orders });
    this.committed = true;
    return result;
  }
}

class InMemoryEventBus implements EventBus {
  readonly published: DomainEvent[] = [];

  async publish(event: DomainEvent): Promise<void> {
    this.published.push(event);
  }
}

describe("PlaceOrder", () => {
  it("persists the order and emits OrderPlaced", async () => {
    const uow = new InMemoryUnitOfWork();
    const bus = new InMemoryEventBus();
    const useCase = new PlaceOrder(uow, bus);

    const orderId = await useCase.execute({
      customerId: newCustomerId(),
      items: [
        makeLineItem("sku-1", 2n, makeMoney(1999n, "USD")),
      ],
    });

    expect(uow.committed).toBe(true);
    expect(uow.orders.added).toHaveLength(1);
    expect(uow.orders.added[0]!.id).toBe(orderId);
    expect(
      bus.published.some((e): e is OrderPlaced => e.type === "OrderPlaced"),
    ).toBe(true);
  });

  it("rejects empty items", async () => {
    const uow = new InMemoryUnitOfWork();
    const bus = new InMemoryEventBus();
    const useCase = new PlaceOrder(uow, bus);

    await expect(
      useCase.execute({ customerId: newCustomerId(), items: [] }),
    ).rejects.toThrow(/at least one line item/);

    expect(bus.published).toEqual([]);
  });
});
```

Runs in milliseconds. No DB, no broker, no Express. The real adapters
get their own integration tests verifying they map correctly to and
from the domain.

---

## Notes on customization

- **`withTransaction` shape.** Choosing a callback-based UoW (as above)
  over an object-lifecycle one (`begin/commit/rollback`) makes it
  harder to forget `commit()` and makes rollback-on-throw automatic.
  Both are valid; pick one per project.
- **Query vs command.** This template is for a *command* use case. For
  queries, skip the UoW and return read-optimized data — often
  bypassing aggregates entirely (see `event-driven.md` § CQRS).
- **Idempotency.** If the command originates from a message consumer
  or an HTTP client with retries, store processed `idempotencyKey`s
  and short-circuit duplicates. A dedicated `IdempotencyStore` port
  works well.
- **Cross-aggregate coordination.** Never mutate two aggregates in one
  `withTransaction` call. Publish a domain event from the first; a
  handler (in a new transaction) mutates the second. See
  `event-driven.md` for the outbox pattern.
- **Decorators for cross-cutting concerns.** Wrap use cases with
  logging, metrics, authorization decorators — see
  `design-patterns.md` § Decorator. A simple function wrapper is
  usually enough; TypeScript's experimental class decorators are
  runtime syntax and conflict with `erasableSyntaxOnly` / native
  type stripping.
