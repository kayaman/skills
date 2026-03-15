---
name: hexagonal-architecture
description: Enforces Hexagonal Architecture (Ports and Adapters) principles including driving and driven ports, adapter separation, and technology-agnostic core design. Use when structuring application boundaries, defining port interfaces, implementing adapters for databases or external APIs, testing business logic in isolation, or comparing hexagonal with onion and clean architecture approaches.
---

# Hexagonal Architecture (Ports and Adapters)

Reference: *Hexagonal Architecture Explained* (Cockburn & Garrido de Paz), *Get Your Hands Dirty on Clean Architecture* (Hombergs)

## When to Apply

- Structuring an application so business logic is independent of delivery mechanism and infrastructure
- Defining port interfaces for external system interactions
- Implementing adapters for databases, message queues, REST APIs, or CLI
- Testing business logic in isolation from infrastructure
- Deferring technology decisions (database, framework, messaging) to the last reasonable moment
- Migrating a tightly coupled application toward decoupled architecture

---

## Core Concept

Alistair Cockburn published the pattern in 2005 (roots back to 1994). The hexagon shape was chosen to **break away from layered stack diagrams** — it is not about the number six.

Core intent: *"Allow an application to equally be driven by users, programs, automated tests, or batch scripts, and to be developed and tested in isolation from its eventual run-time devices and databases."*

**Fundamental rule:** The application core defines ALL port interfaces. Adapters depend on ports. The core MUST NOT depend on adapters.

---

## Ports

Ports are **interfaces belonging to the application core** — they are NOT a separate layer.

### Driving (Primary) Ports

Interfaces the application **exposes** for external actors to call INTO the application.

- Define the application's capabilities from the outside world's perspective
- Connected to primary actors: users, other systems, tests, batch jobs
- SHOULD be named by capability: `ForPlacingOrders`, `ForManagingInventory`, `ForQueryingReports`

### Driven (Secondary) Ports

Interfaces the application **requires** from external systems — what the application needs but does not implement.

- Define what services the application expects the outside world to provide
- Connected to secondary actors: databases, message queues, external APIs, file systems
- SHOULD be named by need: `ForStoringOrders`, `ForSendingNotifications`, `ForFetchingExchangeRates`

### Port Design Rules

- MUST define port interfaces in the application core, not in the adapter layer
- MUST express ports in domain language, not technology language (`ForStoringOrders` not `DatabasePort`)
- MUST NOT include technology-specific types in port signatures (no SQL types, HTTP objects, or ORM entities)
- SHOULD keep ports focused — one port per actor interaction concern

---

## Adapters

Adapters are **concrete implementations** that connect ports to the outside world.

### Primary (Driving) Adapters

Translate external input into calls on driving ports. They call INTO the application.

| Adapter Type | Example | Translates From |
|-------------|---------|-----------------|
| REST Controller | `OrderController` | HTTP request → `PlaceOrderCommand` |
| CLI Handler | `ImportCli` | Command-line args → `ImportDataCommand` |
| Message Consumer | `OrderEventListener` | Queue message → `ProcessPaymentCommand` |
| Test Harness | `OrderAcceptanceTest` | Test setup → direct port method calls |
| GraphQL Resolver | `OrderResolver` | GraphQL query → port method call |

### Secondary (Driven) Adapters

Implement driven port interfaces. The application calls THROUGH them.

| Adapter Type | Example | Connects To |
|-------------|---------|-------------|
| SQL Repository | `PostgresOrderRepository` | Database via SQL/ORM |
| REST Client | `ExchangeRateApiClient` | External HTTP API |
| Message Publisher | `RabbitMqNotificationSender` | Message broker |
| File Storage | `S3DocumentStore` | Object storage |
| In-Memory Stub | `InMemoryOrderRepository` | HashMap (for tests) |

### Adapter Rules

- MUST implement exactly one port interface per adapter (adapters are single-purpose)
- MUST NOT contain business logic — only translation and delegation
- MUST NOT be referenced by the application core — the core knows only the port interface
- SHOULD be swappable: replacing `PostgresOrderRepository` with `MongoOrderRepository` requires no core changes

---

## Application Core Structure

The hexagon's interior contains all business logic, free from infrastructure concerns:

```
core/
  domain/
    model/          # Entities, Value Objects, Aggregates
    service/        # Domain services (stateless business rules)
  application/
    port/
      driving/      # Driving port interfaces (ForPlacingOrders)
      driven/       # Driven port interfaces (ForStoringOrders)
    service/        # Application services (use case orchestration)
```

- MUST NOT import any framework, database, or HTTP library in the core
- MUST NOT reference any adapter class from within the core
- SHOULD separate domain model from application services (domain contains pure business rules; application coordinates use cases)

---

## Testing Strategy

The hexagonal architecture's primary advantage is testability through adapter substitution.

### Test Progression

| Phase | Driving Adapter | Driven Adapter | Tests |
|-------|----------------|----------------|-------|
| **1. Unit/Domain** | Test harness | In-memory stubs | Business rules in isolation |
| **2. Integration** | Test harness | Real infrastructure | Port contract verification |
| **3. Acceptance** | HTTP/CLI test client | In-memory stubs | End-to-end behavior without infrastructure |
| **4. System** | HTTP/CLI test client | Real infrastructure | Full stack verification |

- MUST write tests against port interfaces, not adapter implementations
- SHOULD start with in-memory adapters during development; add real adapters incrementally
- SHOULD use the test harness as a first-class driving adapter — it validates the entire core without infrastructure

---

## Relationship to Other Architectures

All three share the same DNA: business logic at center, dependencies point inward, DIP at architectural level.

| Aspect | Hexagonal | Onion (Palermo, 2008) | Clean (Martin, 2012) |
|--------|-----------|----------------------|---------------------|
| **Internal structure** | Least prescriptive — core is a single hexagon | Explicit concentric layers: Domain Model → Domain Services → Application Services | Four named layers with defined responsibilities |
| **Terminology** | Ports and Adapters | Layers and Interfaces | Entities, Use Cases, Interface Adapters, Frameworks |
| **Unique contribution** | Symmetry between driving and driven sides; ports as first-class concept | Explicit domain service layer separation | Screaming Architecture, Humble Object, component principles |
| **Best for** | Teams wanting flexibility in internal organization | Teams wanting explicit domain layer separation | Teams wanting comprehensive architectural rules |

- SHOULD choose hexagonal when the team values simplicity and flexibility in internal core organization
- SHOULD choose clean architecture when the team benefits from prescriptive layer naming and component principles
- All three are valid; the important invariant is **dependencies point inward**

---

## Common Pitfalls

| Pitfall | Remedy |
|---------|--------|
| **Ports as a separate layer** | Ports belong to the core — they ARE the core's boundary, not a layer between core and adapters |
| **Adapter with business logic** | Move logic to domain or application service; adapter does translation only |
| **Core importing adapter** | Invert the dependency — core defines the interface, adapter implements it |
| **Technology in port signatures** | Express ports in domain language; convert technology types in the adapter |
| **One giant port per side** | Split into focused ports by actor/concern; one port per interaction boundary |
| **Over-engineering simple apps** | Hexagonal adds value when multiple adapters or testability are genuinely needed |

---

## Checklist

When designing or reviewing a hexagonal architecture, verify:

- [ ] The application core defines all port interfaces — no port is defined in an adapter
- [ ] Driving ports express application capabilities in domain language
- [ ] Driven ports express application needs in domain language — no technology types
- [ ] Primary adapters translate external input and call driving ports
- [ ] Secondary adapters implement driven ports and connect to external systems
- [ ] The core has zero imports from frameworks, databases, or HTTP libraries
- [ ] No adapter is referenced from within the core
- [ ] Business logic lives in the core, not in adapters
- [ ] Tests run against ports using in-memory adapters for fast feedback
- [ ] Adapters are swappable without modifying core code

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Hexagonal Architecture Explained* | Alistair Cockburn, Juan Manuel Garrido de Paz | Addison-Wesley | 2024 |
| *Get Your Hands Dirty on Clean Architecture* (2nd ed.) | Tom Hombergs | Packt | 2023 |
| *Fundamentals of Software Architecture* | Mark Richards, Neal Ford | O'Reilly | 2020 |
| *Software Architecture: The Hard Parts* | Ford, Richards, Sadalage, Dehghani | O'Reilly | 2021 |

### Online References

- Alistair Cockburn's original article: alistair.cockburn.us/hexagonal-architecture
- Netflix Tech Blog: "Ready for Changes with Hexagonal Architecture" (2020)
- AWS Prescriptive Guidance: "Building Hexagonal Architectures on AWS" (2023)
