---
name: clean-architecture
description: Enforces Clean Architecture principles including the dependency rule, layer separation, and component design. Use when structuring application layers, defining boundaries between domain and infrastructure, reviewing code for dependency rule violations, applying Screaming Architecture, or evaluating component cohesion and coupling (REP, CCP, CRP, ADP, SDP, SAP).
---

# Clean Architecture

Reference: *Clean Architecture* (Martin), *Get Your Hands Dirty on Clean Architecture* (Hombergs), *Fundamentals of Software Architecture* (Richards & Ford)

## When to Apply

- Structuring a new application's package/module layout
- Defining boundaries between domain logic and infrastructure
- Reviewing imports for dependency rule violations
- Deciding how data should cross layer boundaries
- Evaluating whether the architecture "screams" business purpose or framework choice
- Assessing component cohesion and coupling in a modular system

---

## The Dependency Rule

**The overriding rule:** Source code dependencies MUST only point inward — from outer layers toward inner layers. Nothing in an inner circle can know anything about an outer circle: no names, no data formats, no function calls.

Dynamic polymorphism (DIP) creates source code dependencies that oppose the flow of control, allowing inner layers to define interfaces that outer layers implement.

---

## The Four Layers

From innermost (most stable) to outermost (most volatile):

### 1. Entities (Enterprise Business Rules)

- Domain objects encapsulating business rules independent of any application
- Least likely to change when externalities change
- MUST NOT depend on any other layer
- MUST NOT import framework classes, database libraries, or HTTP concepts
- Examples: `Order`, `Money`, `ShippingPolicy`

### 2. Use Cases (Application Business Rules)

- Application-specific orchestration — direct entities to use their business rules
- Each use case represents one user goal or system operation
- MUST depend only on Entities
- MUST NOT know about delivery mechanism (HTTP, CLI, queue) or persistence technology
- SHOULD be named by business action: `PlaceOrder`, `CancelSubscription`, `TransferFunds`

### 3. Interface Adapters

- Controllers, presenters, gateways — convert data between use case format and external format
- MUST NOT contain business logic — only format conversion and delegation
- All SQL, HTTP serialization, and framework annotations are restricted to this layer
- Examples: REST controllers, repository implementations, view models, DTO mappers

### 4. Frameworks & Drivers

- Outermost layer: web frameworks, databases, UI, external services
- *"The web is a detail. The database is a detail."*
- SHOULD contain minimal code — mostly glue configuration wiring frameworks to adapters
- Changes here MUST NOT propagate inward

---

## Data Crossing Boundaries

- MUST pass only simple data structures across boundaries: DTOs, primitives, or plain value objects
- MUST NOT pass Entities outward — map to a response DTO at the adapter layer
- MUST NOT pass database rows or ORM entities inward — map to domain objects at the adapter layer
- SHOULD NOT create identical DTOs for every layer boundary — map only where formats genuinely differ

| Direction | What Crosses | Example |
|-----------|-------------|---------|
| Inward (request) | Input DTO or command object | `PlaceOrderCommand { customerId, items[] }` |
| Outward (response) | Output DTO or result object | `OrderConfirmation { orderId, estimatedDelivery }` |
| Never | Entity, DB row, ORM model, framework object | `Order` entity, Hibernate proxy, Express `Request` |

---

## Screaming Architecture

The top-level directory structure SHOULD reveal the system's business purpose, not its framework.

**Good — screams "health clinic":**
```
src/
  appointments/
  patients/
  billing/
  prescriptions/
```

**Bad — screams "Spring Boot":**
```
src/
  controllers/
  services/
  repositories/
  models/
```

- SHOULD organize top-level packages by business capability or use case
- MAY use technical sub-packages within a business package (e.g., `appointments/adapter/`, `appointments/domain/`)

---

## Humble Object Pattern

Split behavior into two parts: a **testable** component with all the logic, and a **humble** component that is hard to test but contains minimal logic.

| Component | Testable? | Contains |
|-----------|-----------|----------|
| **Presenter** | Yes | Formats data, applies display logic, builds view model |
| **View** | Humble (hard to test) | Renders the view model to screen — minimal logic |
| **Gateway** | Yes (interface) | Defines data access contract |
| **Repository Impl** | Humble | Executes SQL, calls ORM — tested via integration tests |

- SHOULD push all logic out of hard-to-test components into their testable counterparts
- SHOULD use the humble object boundary as a natural seam for unit vs integration testing

---

## Component Design Principles

### Cohesion Principles (what goes inside a component)

| Principle | Rule | Tension |
|-----------|------|---------|
| **REP** (Reuse/Release Equivalence) | The granule of reuse is the granule of release — group things released together | Too broad: components become bloated |
| **CCP** (Common Closure) | Classes that change together belong together — SRP at component level | Too narrow: too many components |
| **CRP** (Common Reuse) | Don't force users to depend on things they don't need — ISP at component level | Too strict: components fragment |

SHOULD balance these three forces: REP and CCP tend to make components larger; CRP makes them smaller. Early in development, favor CCP (group by change). As the system matures, shift toward CRP (minimize unnecessary dependencies).

### Coupling Principles (relationships between components)

| Principle | Rule |
|-----------|------|
| **ADP** (Acyclic Dependencies) | The component dependency graph MUST have no cycles |
| **SDP** (Stable Dependencies) | Depend in the direction of stability — volatile components depend on stable ones |
| **SAP** (Stable Abstractions) | Stable components SHOULD be abstract; unstable components SHOULD be concrete |

- MUST break dependency cycles using DIP (introduce an interface) or extract a new shared component
- SHOULD measure instability (I = outgoing / (incoming + outgoing)) and abstractness (A = abstract classes / total classes)
- Components in the "zone of pain" (stable + concrete) are rigid; components in the "zone of uselessness" (unstable + abstract) are irrelevant

---

## Common Pitfalls

| Pitfall | Why It Happens | Remedy |
|---------|---------------|--------|
| **Over-layering CRUD apps** | Applying 4 layers to simple data entry | Skip use case layer for trivial operations; use adapters directly |
| **Use cases as repository proxies** | Use case does nothing but call `repository.save()` | If there's no business logic, the use case adds no value — simplify |
| **Mapping everything** | Identical DTOs at every boundary | Map only where formats genuinely differ; don't cargo-cult mapping |
| **"Easy database swap" myth** | Justifying layers by hypothetical DB migration | Layers exist for testability and independence, not DB swaps |
| **Framework in the domain** | Annotations, framework types leak into entities | Entities MUST be plain objects with zero framework dependencies |
| **Designing components top-down** | Trying to define all components before writing code | Component structure evolves as the codebase grows — don't over-plan |

---

## Checklist

When designing or reviewing architecture, verify:

- [ ] Source code dependencies point inward — no inner layer imports from an outer layer
- [ ] Entities contain business rules and have zero framework dependencies
- [ ] Use cases orchestrate entities without knowing about HTTP, SQL, or UI
- [ ] Interface adapters convert between use case format and external format only
- [ ] Data crosses boundaries as DTOs or simple structures, never as entities or DB rows
- [ ] Top-level directory structure reveals business purpose (Screaming Architecture)
- [ ] Hard-to-test code is isolated in humble objects with minimal logic
- [ ] Component dependency graph has no cycles (ADP)
- [ ] Stable components are abstract; volatile components are concrete (SAP)
- [ ] Architecture complexity matches the problem — no over-layering for simple operations

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Clean Architecture* | Robert C. Martin | Pearson | 2017 |
| *Get Your Hands Dirty on Clean Architecture* (2nd ed.) | Tom Hombergs | Packt | 2023 |
| *Fundamentals of Software Architecture* | Mark Richards, Neal Ford | O'Reilly | 2020 |
| *Software Architecture: The Hard Parts* | Ford, Richards, Sadalage, Dehghani | O'Reilly | 2021 |
| *Software Architecture in Practice* (4th ed.) | Bass, Clements, Kazman | Addison-Wesley | 2024 |
| *A Philosophy of Software Design* (2nd ed.) | John Ousterhout | Stanford | 2021 |
