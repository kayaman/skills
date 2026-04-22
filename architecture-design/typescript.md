# TypeScript Idioms for Architecture & Design (5.x)

TypeScript 5.x — especially 5.2+ with `using`, 5.4+ with
`NoInfer`, 5.8+ with `erasableSyntaxOnly` and Node-native type
stripping — has matured into a language where DDD, Clean
Architecture, SOLID, and the GoF patterns translate cleanly with
minimal ceremony. This reference maps each design concept to its
idiomatic TypeScript 5.x expression.

Canonical references: Cherny, *Programming TypeScript* (2019) —
foundations still current; Vanderkam, *Effective TypeScript* (2nd ed.,
2024) — modern idioms and traps; the TypeScript release notes for
5.0 through 5.9.

A note on classes vs functions: TypeScript is not Java. Class
hierarchies are often not the right tool. Discriminated unions,
factory functions, and interface-typed objects frequently beat a class
tree for modeling domain states. The idioms here lean into this.

---

## Value Objects

The modern pattern is a branded type plus a factory function, not a
class. This keeps value objects erasable (works with `erasableSyntaxOnly`
and Node's native type stripping) and composable.

```typescript
// Branded type — nominal distinction within structural typing
export type Money = {
  readonly _brand: unique symbol;
  readonly amount: bigint;        // cents, avoid float for money
  readonly currency: Currency;
};

export type Currency = "USD" | "EUR" | "BRL";

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
```

**Why branded types:** plain `string` for an ID is indistinguishable
from any other string. A branded type — `string & { readonly __brand:
unique symbol }` — is nominally distinct at compile time, zero
runtime cost.

```typescript
export type UserId = string & { readonly __brand: unique symbol };
export type OrderId = string & { readonly __brand: unique symbol };

function shipOrder(id: OrderId): void { /* … */ }

const userId = "abc" as UserId;
shipOrder(userId);  // Error: UserId is not assignable to OrderId
```

**Class-based value objects** are fine when methods on the value object
itself aid readability. Keep them immutable:

```typescript
export class Email {
  private constructor(public readonly value: string) {}

  static create(raw: string): Email {
    if (!/^[^@]+@[^@]+\.[^@]+$/.test(raw)) {
      throw new Error(`Invalid email: ${raw}`);
    }
    return new Email(raw);
  }

  equals(other: Email): boolean {
    return this.value === other.value;
  }
}
```

`private constructor` + `static create` forces construction through the
validated path. No way to skip invariant enforcement.

---

## Entities

Entities have identity and evolve. Use classes when behavior clusters
naturally; use interfaces + pure functions when state transitions are
better modeled as a series of transformations.

```typescript
import type { CustomerId, OrderId } from "./ids";
import type { LineItem } from "./lineItem";
import type { DomainEvent, OrderPlaced, OrderShipped } from "./events";

export class Order {
  readonly id: OrderId;
  readonly customerId: CustomerId;
  private readonly items: ReadonlyArray<LineItem>;
  private status: "draft" | "placed" | "paid" | "shipped" | "cancelled";
  private events: DomainEvent[] = [];

  private constructor(
    id: OrderId, customerId: CustomerId, items: ReadonlyArray<LineItem>,
  ) {
    if (items.length === 0) throw new Error("Order requires items");
    this.id = id;
    this.customerId = customerId;
    this.items = items;
    this.status = "placed";
  }

  static create(
    id: OrderId, customerId: CustomerId, items: ReadonlyArray<LineItem>,
  ): Order {
    const order = new Order(id, customerId, items);
    order.events.push({
      type: "OrderPlaced",
      orderId: id,
      customerId,
      at: new Date(),
    });
    return order;
  }

  ship(): void {
    if (this.status !== "paid") throw new Error("Cannot ship unpaid order");
    this.status = "shipped";
    this.events.push({ type: "OrderShipped", orderId: this.id, at: new Date() });
  }

  pullEvents(): DomainEvent[] {
    const out = this.events;
    this.events = [];
    return out;
  }
}
```

### Alternative: pure-function entity

For event-sourced or state-machine-heavy domains, skip the class:

```typescript
export type OrderState = {
  readonly id: OrderId;
  readonly customerId: CustomerId;
  readonly items: ReadonlyArray<LineItem>;
  readonly status: "placed" | "paid" | "shipped" | "cancelled";
};

export function placeOrder(
  id: OrderId, customerId: CustomerId, items: ReadonlyArray<LineItem>,
): { state: OrderState; events: ReadonlyArray<DomainEvent> } {
  if (items.length === 0) throw new Error("Order requires items");
  const state: OrderState = { id, customerId, items, status: "placed" };
  const events = [{ type: "OrderPlaced" as const, orderId: id, customerId,
                    at: new Date() }];
  return { state, events };
}

export function shipOrder(
  state: OrderState,
): { state: OrderState; events: ReadonlyArray<DomainEvent> } {
  if (state.status !== "paid") throw new Error("Cannot ship unpaid order");
  return {
    state: { ...state, status: "shipped" },
    events: [{ type: "OrderShipped", orderId: state.id, at: new Date() }],
  };
}
```

Both are valid. The functional form tests a little easier and is a
natural fit for event sourcing. The class form clusters behavior.

---

## Domain states as discriminated unions

Often the cleanest model. Replaces a state column plus a tangle of
optional fields.

```typescript
export type Order =
  | { kind: "Draft";     id: OrderId; items: ReadonlyArray<LineItem> }
  | { kind: "Placed";    id: OrderId; items: ReadonlyArray<LineItem>; placedAt: Date }
  | { kind: "Paid";      id: OrderId; items: ReadonlyArray<LineItem>; paidAt: Date }
  | { kind: "Shipped";   id: OrderId; items: ReadonlyArray<LineItem>; shippedAt: Date }
  | { kind: "Cancelled"; id: OrderId; reason: string };

export function ship(order: Order): Order {
  switch (order.kind) {
    case "Paid":
      return { kind: "Shipped", id: order.id, items: order.items,
               shippedAt: new Date() };
    default:
      throw new Error(`Cannot ship order in state ${order.kind}`);
  }
}
```

**Exhaustiveness check.** Pair with a `never` default to get a compile-
time error when a new variant is added and someone forgets to handle it.

```typescript
function describe(order: Order): string {
  switch (order.kind) {
    case "Draft":     return "not yet placed";
    case "Placed":    return "awaiting payment";
    case "Paid":      return "ready to ship";
    case "Shipped":   return "in transit";
    case "Cancelled": return `cancelled: ${order.reason}`;
    default: {
      const _exhaustive: never = order;
      return _exhaustive;
    }
  }
}
```

Add a new variant → TypeScript points out every `switch` that needs
updating. This is one of the most powerful design tools TypeScript
gives you.

---

## Ports via interfaces

```typescript
import type { OrderId } from "./ids";
import type { Order } from "./order";

export interface OrderRepository {
  get(id: OrderId): Promise<Order>;
  add(order: Order): Promise<void>;
  findByCustomer(customerId: CustomerId): Promise<ReadonlyArray<Order>>;
}
```

TypeScript interfaces are structural — any object with matching shape
conforms. This fits ISP naturally. Split by consumer need:

```typescript
export interface OrderReader {
  get(id: OrderId): Promise<Order>;
}

export interface OrderWriter {
  add(order: Order): Promise<void>;
}
```

A read-only consumer depends on `OrderReader`. A write path depends on
both. `class SqlOrderRepository implements OrderReader, OrderWriter`
satisfies both.

---

## Dependency injection

Constructor injection at the use case level:

```typescript
export class PlaceOrder {
  constructor(
    private readonly orders: OrderRepository,
    private readonly uow: UnitOfWork,
    private readonly events: EventBus,
    private readonly clock: () => Date = () => new Date(),
  ) {}

  async execute(cmd: PlaceOrderCommand): Promise<OrderId> {
    return this.uow.withTransaction(async () => {
      const order = Order.create(cmd.id, cmd.customerId, cmd.items);
      await this.orders.add(order);
      for (const event of order.pullEvents()) {
        await this.events.publish(event);
      }
      return order.id;
    });
  }
}
```

Wiring in a composition root:

```typescript
// infrastructure/container.ts
export function buildPlaceOrderUseCase(deps: {
  db: Database;
  broker: MessageBroker;
}): PlaceOrder {
  const repo = new SqlOrderRepository(deps.db);
  const uow  = new SqlUnitOfWork(deps.db);
  const bus  = new KafkaEventBus(deps.broker);
  return new PlaceOrder(repo, uow, bus);
}
```

DI frameworks for TypeScript (tsyringe, InversifyJS, NestJS's built-in)
are available. Reach for them when wiring becomes cumbersome —
generally only in medium-to-large apps or when you need interception
(logging, metrics) via decorators.

---

## DTOs at layer boundaries

Zod (runtime + compile-time schema) is the de facto tool.

```typescript
import { z } from "zod";

export const PlaceOrderRequest = z.object({
  customerId: z.string().uuid(),
  items: z.array(z.object({
    sku: z.string().min(1),
    quantity: z.number().int().positive(),
    unitPriceCents: z.number().int().positive(),
  })).min(1),
});

export type PlaceOrderRequest = z.infer<typeof PlaceOrderRequest>;

// In the controller:
const parsed = PlaceOrderRequest.parse(req.body);
const command: PlaceOrderCommand = {
  id: newOrderId(),
  customerId: parsed.customerId as CustomerId,
  items: parsed.items.map(toLineItem),
};
```

Zod gives you runtime validation and a compile-time type from the same
schema. Alternatives: Valibot (smaller bundle), ArkType (ergonomic
syntax). Pick one per project and stay consistent.

---

## `readonly` and `as const`

Immutability without a framework:

```typescript
// Readonly object and array
const COLORS = ["red", "green", "blue"] as const;
type Color = typeof COLORS[number];   // "red" | "green" | "blue"

// In value objects
type Point = {
  readonly x: number;
  readonly y: number;
};
```

Prefer `ReadonlyArray<T>` over `T[]` in function signatures you don't
intend to mutate — the reader of the signature sees the intent.

### The `satisfies` operator (4.9+)

Get literal-preserving types on constants without widening:

```typescript
const routes = {
  placeOrder: { method: "POST", path: "/orders" },
  getOrder:   { method: "GET",  path: "/orders/:id" },
} satisfies Record<string, { method: "GET" | "POST" | "PUT"; path: string }>;

// routes.placeOrder.method is "POST", not string.
```

Use `satisfies` when you want both **type checking against a broader
shape** and **the precise literal type for downstream inference**.

---

## `using` for resource management (5.2+)

Replaces `try/finally` for synchronous cleanup, and `await using` for
async. Essential in infrastructure adapters (connections, transactions,
files).

```typescript
async function shipOrderFlow(id: OrderId) {
  await using conn = await db.connect();  // disposed on exit
  const tx = await conn.beginTransaction();
  try {
    // … domain operations
    await tx.commit();
  } catch (err) {
    await tx.rollback();
    throw err;
  }
}
```

The `Disposable` / `AsyncDisposable` interfaces let your own types opt
in:

```typescript
class Transaction implements AsyncDisposable {
  async [Symbol.asyncDispose](): Promise<void> {
    if (!this.committed) await this.rollback();
  }
}
```

---

## `import type` — compile-time-only imports

Keep type-only imports separate from value imports. Improves build
times and is required for `erasableSyntaxOnly` (5.8+) / Node's native
type stripping.

```typescript
import type { OrderRepository } from "../domain/ports";
import { PlaceOrder } from "./placeOrder";  // value import
```

At every layer boundary, prefer `import type` when you only need the
shape. It makes the value graph visible in bundler analysis and plays
nicely with `erasableSyntaxOnly`.

---

## Testing without the framework

```typescript
class InMemoryOrderRepository implements OrderRepository {
  private readonly store = new Map<OrderId, Order>();

  async get(id: OrderId): Promise<Order> {
    const o = this.store.get(id);
    if (!o) throw new Error(`Order ${id} not found`);
    return o;
  }

  async add(order: Order): Promise<void> {
    this.store.set(order.id, order);
  }

  async findByCustomer(customerId: CustomerId): Promise<Order[]> {
    return [...this.store.values()]
      .filter((o) => o.customerId === customerId);
  }
}

test("placeOrder emits OrderPlaced", async () => {
  const orders = new InMemoryOrderRepository();
  const uow = new InMemoryUnitOfWork();
  const events = new InMemoryEventBus();
  const useCase = new PlaceOrder(orders, uow, events);

  await useCase.execute({
    id: newOrderId(), customerId: newCustomerId() as CustomerId,
    items: [{ sku: "a", quantity: 1, unitPriceCents: 100n as any }],
  });

  expect(events.published.some(e => e.type === "OrderPlaced")).toBe(true);
});
```

Tests run in milliseconds. The real database and broker get their own,
smaller set of integration tests against the concrete adapters.

---

## Linting architectural boundaries

Use
[`dependency-cruiser`](https://github.com/sverweij/dependency-cruiser)
or `eslint-plugin-boundaries` to enforce the Dependency Rule:

```json
// .dependency-cruiser.json (excerpt)
{
  "forbidden": [
    {
      "name": "no-domain-to-outer",
      "from": { "path": "src/.+/domain/" },
      "to":   { "path": "src/.+/(application|adapters|infrastructure)/" }
    },
    {
      "name": "no-application-to-adapters",
      "from": { "path": "src/.+/application/" },
      "to":   { "path": "src/.+/(adapters|infrastructure)/" }
    }
  ]
}
```

Run on every PR. A violation is caught at merge time, before it ossifies.

---

## TypeScript-specific anti-patterns

**`any` in domain signatures.** Every `any` is a type hole the compiler
stops helping you with. If you need dynamic behavior, reach for
`unknown` and narrow.

**Classes where discriminated unions fit better.** A `class OrderDraft
extends Order` tree with virtual methods is often cleaner as a union
+ exhaustive `switch`.

**`!` non-null assertion.** Usually hiding a design problem. If the
value can be null, express it in the type and force the caller to
handle it.

**Enums used for discriminants.** `const` assertion unions beat enums
for discriminator fields — `"Placed"` is a string literal type, no
runtime overhead, works with `erasableSyntaxOnly`.

**Unnecessary `class` wrapping.** A class with only static methods is a
namespace. Just export functions.

**Leaking Prisma/TypeORM types across layers.** Same issue as leaking
SQLAlchemy entities in Python. Map to domain types inside the
repository adapter.

**Omitted exhaustive checks.** `switch` without `never` default means
every new variant silently ignores some branches. Add the `never`
check; let the compiler catch what humans forget.
