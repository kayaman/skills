---
name: domain-driven-design
description: Enforces Domain-Driven Design strategic and tactical patterns including Bounded Contexts, Aggregates, Value Objects, Domain Events, and Context Mapping. Use when modeling a business domain, defining bounded context boundaries, designing aggregates, applying ubiquitous language, running Event Storming workshops, implementing CQRS or Event Sourcing, or reviewing domain models for DDD anti-patterns like Anemic Domain Model.
---

# Domain-Driven Design

Reference: *Domain-Driven Design* (Evans), *Implementing DDD* (Vernon), *Learning DDD* (Khononov)

## When to Apply

- Modeling a complex business domain where the logic is the competitive differentiator
- Defining boundaries between subdomains or microservices
- Designing aggregates, entities, and value objects
- Establishing ubiquitous language between developers and domain experts
- Running Event Storming to discover domain events and bounded contexts
- Implementing CQRS or Event Sourcing for a specific bounded context
- Reviewing domain models for anemic models, oversized aggregates, or leaking contexts

MUST NOT apply full DDD tactical patterns to simple CRUD applications — the overhead is not justified.

---

## Strategic Design

### Ubiquitous Language

- MUST use a single, shared language within each bounded context — reflected in code, documentation, and conversation
- MUST NOT translate between "business terms" and "technical terms" — the code IS the language
- Different bounded contexts MAY use different terms for the same real-world concept (e.g., "Customer" in Sales vs "Account" in Billing)

### Bounded Contexts

A bounded context is the boundary within which a domain model is consistent and a ubiquitous language applies.

- MUST define explicit boundaries — a model is valid only within its context
- SHOULD map one bounded context to one deployable unit (microservice, module)
- Microsoft guidance: *"No smaller than an aggregate, no larger than a bounded context"*

### Context Mapping

Define relationships between bounded contexts using these patterns:

| Pattern | Relationship | Use When |
|---------|-------------|----------|
| **Partnership** | Mutual dependency, coordinated development | Two teams succeed or fail together |
| **Shared Kernel** | Small shared model subset, joint ownership | Limited overlap that both contexts need identically |
| **Customer-Supplier** | Upstream serves downstream; downstream can negotiate | Teams have a clear provider/consumer relationship |
| **Conformist** | Downstream conforms to upstream's model without negotiation | Upstream has no incentive to accommodate downstream |
| **Anti-Corruption Layer** | Translation layer protecting downstream from upstream's model | Integrating with legacy systems or external services |
| **Open Host Service** | Well-defined public API serving multiple consumers | Upstream provides a stable protocol for any consumer |
| **Published Language** | Shared exchange format (JSON schema, Protobuf, Avro) | Multiple contexts exchange data using a documented format |
| **Separate Ways** | No integration — contexts are independent | Integration cost exceeds value |

- MUST use an Anti-Corruption Layer when integrating with legacy systems or external services
- SHOULD default to Customer-Supplier for inter-team context relationships
- SHOULD document all context maps and keep them updated as relationships evolve

### Subdomains

| Type | Description | Investment Strategy |
|------|-------------|-------------------|
| **Core Domain** | Competitive differentiator — what makes the business unique | Invest heavily; use best engineers; full DDD |
| **Supporting Subdomain** | Necessary but not differentiating; custom but simpler | Moderate investment; simpler models |
| **Generic Subdomain** | Commodity functionality (auth, email, payments) | Buy or use off-the-shelf; do not build |

- MUST identify the Core Domain and invest DDD effort there
- SHOULD NOT apply full DDD tactical patterns to Generic Subdomains

---

## Tactical Design

### Entities

- Have unique identity that persists over time; equality is by ID, not attributes
- Are mutable but state changes MUST be modeled as business verbs: `order.cancel()` not `order.setStatus("cancelled")`
- SHOULD be kept lean — push behavior to Value Objects where possible

### Value Objects

- Immutable, defined by their value (not identity), interchangeable when equal
- Contain behavior: `Money.add(other)`, `EmailAddress.validate()`
- Thread-safe by nature (no shared mutable state)
- **Design guidance: aim for many Value Objects and few Entities**

### Aggregates

An aggregate is a cluster of objects treated as a single unit for data changes, defining a consistency boundary.

**Vaughn Vernon's aggregate design rules:**

1. **Design small aggregates** — prefer single-entity aggregates; add entities only when invariants require it
2. **Protect business invariants inside aggregate boundaries** — the aggregate root enforces all rules
3. **Reference other aggregates by identity only** — never hold direct object references to other aggregates
4. **Use eventual consistency across aggregate boundaries** — do not span transactions across aggregates
5. **Update one aggregate per transaction** — if multiple aggregates must change, use domain events

- MUST have exactly one Aggregate Root with global identity as the single entry point
- MUST NOT modify multiple aggregates in a single transaction
- SHOULD keep aggregates as small as invariant protection allows

### Repositories

- Provide a collection-like interface for aggregate persistence: `save()`, `findById()`, `remove()`
- One repository per aggregate root — MUST NOT create repositories for non-root entities
- MUST hide persistence details — the domain layer sees only the interface

### Domain Events

- Named in past tense: `OrderPlaced`, `PaymentReceived`, `InventoryReserved`
- Represent meaningful business occurrences, not technical events
- Enable eventual consistency across aggregate boundaries
- SHOULD be immutable and carry all data needed by consumers

### Domain Services

- Stateless operations that don't naturally belong to any entity or value object
- Typically coordinate multiple aggregates or perform calculations requiring data from several objects
- MUST NOT become a dumping ground — check if the behavior belongs on an entity first

### Application Services

- Orchestrate use cases by coordinating domain objects, repositories, and infrastructure
- MUST NOT contain business logic — delegate to domain objects
- Handle transactions, security, logging, and other cross-cutting concerns

---

## Event Storming

A collaborative workshop technique (Brandolini) for discovering domain events, commands, and bounded context boundaries.

### Three Levels

| Level | Purpose | Output |
|-------|---------|--------|
| **Big Picture** | Explore the entire business domain | Domain events timeline, hot spots, bounded context boundaries |
| **Process Modeling** | Detail a specific business process | Commands, actors, policies, read models, external systems |
| **Software Design** | Translate process into architecture | Aggregates, bounded contexts, event flows |

### Sticky Note Colors (Standard Convention)

| Color | Element | Example |
|-------|---------|---------|
| Orange | Domain Event (past tense) | "Order Placed" |
| Blue | Command (imperative) | "Place Order" |
| Yellow | Aggregate | "Order" |
| Lilac | Policy / Automation | "When payment received, ship order" |
| Pink | Hot Spot / Question | "What if payment fails?" |
| Green | Read Model / View | "Order Summary" |
| Large Pink | External System | "Payment Gateway" |

---

## CQRS and Event Sourcing

### CQRS (Command Query Responsibility Segregation)

Separate read and write models. Apply selectively — Greg Young: *"CQRS is a supporting pattern, not a top-level architecture."*

- Write side: rich domain model with aggregates enforcing invariants
- Read side: optimized projections (denormalized views) for queries
- SHOULD apply CQRS only to bounded contexts with complex domain logic AND different read/write performance needs
- MUST NOT apply CQRS everywhere — it adds significant complexity

### Event Sourcing

Store state changes as an immutable, append-only sequence of events. Current state is derived by replaying events.

- SHOULD use projections to build read-optimized views from the event stream
- SHOULD implement snapshots for aggregates with long event histories (performance optimization)
- Provides: complete audit trail, temporal queries, debugging capability, flexible projection creation
- MUST NOT use Event Sourcing for simple state management — the complexity cost is high

---

## Anti-Patterns and Remedies

| Anti-Pattern | Signal | Remedy |
|-------------|--------|--------|
| **Anemic Domain Model** | Objects are data bags; all logic in service classes | Move behavior into entities and value objects |
| **Oversized Aggregates** | Large object graphs; frequent concurrency conflicts | Split into smaller aggregates; use domain events for cross-aggregate coordination |
| **Ignoring Ubiquitous Language** | Developers use different terms than domain experts | Establish a glossary; rename code to match domain terms |
| **DDD on CRUD** | Full tactical patterns on simple data entry screens | Use DDD strategically (bounded contexts) but skip tactical patterns for simple operations |
| **Shared Database** | Multiple contexts read/write the same tables | Give each context its own storage; synchronize via events |
| **Leaking Context** | One context's model concepts appear in another | Introduce Anti-Corruption Layer or Published Language |

---

## Checklist

Before finalizing a domain model, verify:

- [ ] Core Domain is identified and receives the highest modeling investment
- [ ] Each bounded context has its own ubiquitous language reflected in code
- [ ] Context relationships are mapped using explicit patterns (ACL, Customer-Supplier, etc.)
- [ ] Aggregates are small — single entity where possible
- [ ] Aggregate boundaries protect business invariants
- [ ] Other aggregates are referenced by identity only, never by direct object reference
- [ ] One aggregate is updated per transaction; cross-aggregate consistency uses domain events
- [ ] Entities model state changes as business verbs, not setters
- [ ] Value Objects are used for domain concepts without identity (Money, Email, DateRange)
- [ ] Domain events are named in past tense and carry necessary data
- [ ] Repositories exist only for aggregate roots
- [ ] Application services orchestrate but contain no business logic

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Domain-Driven Design: Tackling Complexity in the Heart of Software* | Eric Evans | Addison-Wesley | 2003 |
| *Implementing Domain-Driven Design* | Vaughn Vernon | Addison-Wesley | 2013 |
| *Domain-Driven Design Distilled* | Vaughn Vernon | Addison-Wesley | 2016 |
| *Learning Domain-Driven Design* | Vlad Khononov | O'Reilly | 2021 |
| *Domain Modeling Made Functional* | Scott Wlaschin | Pragmatic Bookshelf | 2018 |
| *Patterns, Principles, and Practices of Domain-Driven Design* | Millett & Tune | Wrox | 2015 |
| *Balancing Coupling in Software Design* | Vlad Khononov | Addison-Wesley | 2024 |
| *Architecture for Flow* | Andrew Harmel-Law | O'Reilly | 2023 |
| *Introducing EventStorming* | Alberto Brandolini | Leanpub | TBD |
