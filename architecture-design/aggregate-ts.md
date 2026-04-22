# Template: TypeScript Aggregate

Copy and adapt. Replace `Order`, `OrderId`, `LineItem`, etc. with the
concrete domain terms. Remove what doesn't apply.

```typescript
// domain/ids.ts
export type OrderId    = string & { readonly __brand: unique symbol };
export type CustomerId = string & { readonly __brand: unique symbol };

export const newOrderId    = (): OrderId    => crypto.randomUUID() as OrderId;
export const newCustomerId = (): CustomerId => crypto.randomUUID() as CustomerId;
```

```typescript
// domain/money.ts
export type Currency = "USD" | "EUR" | "BRL";

export type Money = {
  readonly _brand: unique symbol;
  readonly amount: bigint;        // cents — avoid float for money
  readonly currency: Currency;
};

export function makeMoney(amount: bigint, currency: Currency): Money {
  if (amount < 0n) throw new Error("Money cannot be negative");
  return { _brand: undefined as never, amount, currency } as Money;
}

export function addMoney(a: Money, b: Money): Money {
  if (a.currency !== b.currency) {
    throw new Error(`Cannot add ${a.currency} to ${b.currency}`);
  }
  return makeMoney(a.amount + b.amount, a.currency);
}

export function multiplyMoney(m: Money, n: bigint): Money {
  return makeMoney(m.amount * n, m.currency);
}
```

```typescript
// domain/lineItem.ts
import { type Money, multiplyMoney } from "./money";

export type LineItem = {
  readonly sku: string;
  readonly quantity: bigint;
  readonly unitPrice: Money;
};

export function makeLineItem(
  sku: string, quantity: bigint, unitPrice: Money,
): LineItem {
  if (quantity <= 0n) throw new Error("Quantity must be positive");
  if (sku.length === 0) throw new Error("SKU cannot be empty");
  return { sku, quantity, unitPrice };
}

export function lineItemSubtotal(item: LineItem): Money {
  return multiplyMoney(item.unitPrice, item.quantity);
}
```

```typescript
// domain/events.ts
import type { OrderId, CustomerId } from "./ids";
import type { Money } from "./money";

export type OrderPlaced = {
  readonly type: "OrderPlaced";
  readonly orderId: OrderId;
  readonly customerId: CustomerId;
  readonly total: Money;
  readonly occurredAt: Date;
};

export type OrderShipped = {
  readonly type: "OrderShipped";
  readonly orderId: OrderId;
  readonly occurredAt: Date;
};

export type OrderCancelled = {
  readonly type: "OrderCancelled";
  readonly orderId: OrderId;
  readonly reason: string;
  readonly occurredAt: Date;
};

export type DomainEvent = OrderPlaced | OrderShipped | OrderCancelled;
```

```typescript
// domain/order.ts
import type { OrderId, CustomerId } from "./ids";
import {
  type LineItem,
  lineItemSubtotal,
} from "./lineItem";
import { type Money, addMoney } from "./money";
import type { DomainEvent } from "./events";

type OrderStatus = "placed" | "paid" | "shipped" | "cancelled";

/**
 * Aggregate root for a customer's order.
 *
 * Invariants:
 *   • must contain at least one line item.
 *   • total equals sum of line item subtotals.
 *   • can only be shipped from 'paid'.
 *   • can only be cancelled before 'shipped'.
 */
export class Order {
  readonly id: OrderId;
  readonly customerId: CustomerId;
  private readonly items: ReadonlyArray<LineItem>;
  private _status: OrderStatus;
  private events: DomainEvent[] = [];

  private constructor(
    id: OrderId,
    customerId: CustomerId,
    items: ReadonlyArray<LineItem>,
  ) {
    if (items.length === 0) {
      throw new Error("Order requires at least one line item");
    }
    this.id = id;
    this.customerId = customerId;
    this.items = items;
    this._status = "placed";
  }

  // -- construction -------------------------------------------------
  static place(
    id: OrderId,
    customerId: CustomerId,
    items: ReadonlyArray<LineItem>,
  ): Order {
    const order = new Order(id, customerId, items);
    order.events.push({
      type: "OrderPlaced",
      orderId: id,
      customerId,
      total: order.total,
      occurredAt: new Date(),
    });
    return order;
  }

  // -- commands -----------------------------------------------------
  markPaid(): void {
    if (this._status !== "placed") {
      throw new Error(`Cannot pay order in state ${this._status}`);
    }
    this._status = "paid";
  }

  ship(): void {
    if (this._status !== "paid") {
      throw new Error("Cannot ship unpaid order");
    }
    this._status = "shipped";
    this.events.push({
      type: "OrderShipped",
      orderId: this.id,
      occurredAt: new Date(),
    });
  }

  cancel(reason: string): void {
    if (this._status === "shipped") {
      throw new Error("Cannot cancel shipped order");
    }
    this._status = "cancelled";
    this.events.push({
      type: "OrderCancelled",
      orderId: this.id,
      reason,
      occurredAt: new Date(),
    });
  }

  // -- queries ------------------------------------------------------
  get total(): Money {
    // items.length > 0 invariant guaranteed by constructor
    return this.items
      .slice(1)
      .reduce(
        (acc, item) => addMoney(acc, lineItemSubtotal(item)),
        lineItemSubtotal(this.items[0]!),
      );
  }

  get status(): OrderStatus {
    return this._status;
  }

  // -- event collection --------------------------------------------
  pullEvents(): ReadonlyArray<DomainEvent> {
    const out = this.events;
    this.events = [];
    return out;
  }
}
```

```typescript
// domain/ports.ts
import type { Order } from "./order";
import type { OrderId, CustomerId } from "./ids";

export interface OrderRepository {
  get(id: OrderId): Promise<Order>;
  add(order: Order): Promise<void>;
  findByCustomer(customerId: CustomerId): Promise<ReadonlyArray<Order>>;
}
```

---

## Alternative: pure-function aggregate (for event sourcing)

Prefer this when state transitions are numerous, event sourcing is
adopted, or you want fully immutable state.

```typescript
export type OrderState = {
  readonly id: OrderId;
  readonly customerId: CustomerId;
  readonly items: ReadonlyArray<LineItem>;
  readonly status: OrderStatus;
};

type Result = {
  readonly state: OrderState;
  readonly events: ReadonlyArray<DomainEvent>;
};

export function placeOrder(
  id: OrderId,
  customerId: CustomerId,
  items: ReadonlyArray<LineItem>,
): Result {
  if (items.length === 0) {
    throw new Error("Order requires at least one line item");
  }
  const state: OrderState = { id, customerId, items, status: "placed" };
  const total = items.slice(1).reduce(
    (acc, i) => addMoney(acc, lineItemSubtotal(i)),
    lineItemSubtotal(items[0]!),
  );
  return {
    state,
    events: [{
      type: "OrderPlaced", orderId: id, customerId,
      total, occurredAt: new Date(),
    }],
  };
}

export function shipOrder(state: OrderState): Result {
  if (state.status !== "paid") {
    throw new Error("Cannot ship unpaid order");
  }
  return {
    state: { ...state, status: "shipped" },
    events: [{ type: "OrderShipped", orderId: state.id, occurredAt: new Date() }],
  };
}
```

---

## Notes on customization

- **Identity generation.** `crypto.randomUUID()` is UUID v4. For
  time-ordered IDs, use a v7 library (`uuid` v9+ supports it).
- **Money precision.** `bigint` in cents is the safe default. Never
  `number` for money — floating-point rounding will bite.
- **Status as discriminated union.** For richer domain modeling
  (different fields per status), promote `OrderStatus` from a string
  union to a full discriminated union — see `references/typescript.md`
  § Domain states as discriminated unions.
- **Exhaustive event handling.** When consuming events, use a `switch`
  on `event.type` with a `never`-default to ensure new event variants
  force an update to every consumer.
- **Zod DTOs.** At the HTTP boundary, define Zod schemas that mirror the
  shape of `PlaceOrderCommand`, parse incoming bodies, then cast
  validated fields to branded types.
