---
name: architecture-design
description: >-
  Architecture and design-review skill covering Domain-Driven Design (DDD),
  Clean Architecture, SOLID, GoF design patterns, and event-driven
  architecture, with concrete Python 3.12+ and TypeScript 5.x idioms. Use
  whenever a structural design decision is in play — designing a new system
  or module, reviewing code for structural quality, choosing between
  architectural approaches, refactoring toward cleaner layering, placing
  business logic, defining module boundaries, evaluating aggregates and
  bounded contexts, applying SOLID, selecting a design pattern, or deciding
  when (and when not) to adopt event sourcing, CQRS, or event-driven
  messaging. Trigger on phrases like "design a system", "architecture
  review", "is this clean", "where does this logic belong", "aggregate",
  "bounded context", "hexagonal", "ports and adapters", "SOLID violation",
  "anemic domain model", "code smell", "refactor this", "use case layer",
  "event sourcing", "CQRS", or any moment a developer asks whether a piece
  of code is in the right place.
license: MIT
metadata:
  version: "1.0.0"
  category: software-engineering
  tags: ddd, clean-architecture, solid, design-patterns, event-driven, python, typescript
---

# Architecture & Design

Guide for designing and reviewing systems through five lenses —
Domain-Driven Design, Clean Architecture, SOLID, GoF patterns, and
event-driven architecture — with concrete Python 3.12+ and TypeScript 5.x
idioms. Deep content is organized in `references/`; this file is the router.

> **Core principle.** Good architecture maximizes the number of decisions
> *not made* and *easily changed*. The test of a design is how cheaply
> the system can absorb tomorrow's requirement, not how elegantly it
> handles today's.
> Ref: Martin, *Clean Architecture*, Ch. 15.

---

## Two workflows

Route based on user intent.

### A. Designing (greenfield or new module)

Follow the six-phase sequence. Do them in order — each phase produces
inputs the next one needs.

1. **Strategic DDD** — Identify bounded contexts, establish the ubiquitous
   language, map context relationships. See `references/ddd.md` §
   Strategic. *Do this before picking a framework or database.*
2. **Tactical DDD** — Model aggregates, entities, value objects, domain
   events within each context. See `references/ddd.md` § Tactical.
   Aggregate boundaries dictate transaction boundaries.
3. **Clean Architecture layers** — Place concepts into domain / application
   / interface / infrastructure. Apply the Dependency Rule. See
   `references/clean-architecture.md`.
4. **Tactical patterns** — Choose repository, specification, factory, and
   other patterns to implement the design. See
   `references/design-patterns.md`.
5. **Integration style** — Sync RPC, async messaging, event sourcing, CQRS?
   See `references/event-driven.md`.
6. **Language idioms** — Translate into Python (`references/python.md`) or
   TypeScript (`references/typescript.md`).

### B. Evaluating (existing system / PR review)

Walk `references/evaluation-rubric.md` section by section. It produces a
scored report covering: domain model health, layer integrity, SOLID
adherence, pattern usage, and integration style.

For a fast triage before a deeper review, use the **Five-question smoke
test:**

1. Is there a domain model, or just CRUD on anemic classes?
2. Do inner layers import from outer layers anywhere?
3. What are the top three SOLID violations?
4. Any singletons, service locators, or god classes in disguise?
5. Any synchronous call chain deeper than three services?

If any answer is bad, the system has a structural problem that the
referenced document diagnoses in detail.

---

## The five lenses: when to load which reference

| Lens | Load when… | Reference |
|---|---|---|
| **DDD** | modeling a domain, choosing aggregate boundaries, fighting anemic models, defining bounded contexts, aligning code with domain-expert language | `references/ddd.md` |
| **Clean Architecture** | deciding where logic belongs, drawing layer boundaries, auditing dependency direction, evaluating framework coupling, setting up ports & adapters | `references/clean-architecture.md` |
| **SOLID** | reviewing a class, auditing interfaces, diagnosing rigidity, untangling "shotgun surgery" changes, designing for extensibility | `references/solid.md` |
| **Design Patterns** | a recurring structural problem appears, or a team is reaching for a specific named pattern and you need to validate or challenge the choice | `references/design-patterns.md` |
| **Event-Driven** | services exchange messages, CQRS or event sourcing is proposed, eventual consistency is on the table, sagas/orchestration come up | `references/event-driven.md` |

Language-specific reference files load when translating any lens into code:

- **`references/python.md`** — Python 3.12+ idioms for value objects,
  aggregates, ports, DI, DTOs, pattern matching, Protocols.
- **`references/typescript.md`** — TypeScript 5.x idioms for branded types,
  discriminated unions, readonly modeling, ports, DI, satisfies.

---

## Cross-cutting gotchas

These are the non-obvious traps that separate a good review from a
mediocre one. Each is diagnosed deeper in its reference file.

**Domain modeling**

- *Anemic domain model:* classes with only getters/setters are data
  structures, not domain objects. Business logic ends up in services,
  which fragments invariants and reintroduces procedural code. Ref:
  Fowler, *AnemicDomainModel* essay; Vernon, *IDDD*, Ch. 7.
- *Aggregate bloat:* large aggregates serialize concurrent updates.
  Prefer small aggregates that reference others by ID. Ref: Vernon,
  *IDDD*, Ch. 10 ("Design Small Aggregates").
- *One transaction, one aggregate:* crossing aggregate boundaries in a
  single unit of work is a structural bug, not a performance optimization.
  Use domain events and a process manager instead.
- *Ubiquitous language is not decorative:* if the domain expert says
  "Member" and the code says "User", the mismatch *is* the bug. Rename.

**Layering**

- *The Dependency Rule is one-way:* source code dependencies point inward,
  toward higher-level policy. A single import from domain into
  infrastructure corrupts the whole architecture.
- *Frameworks are details:* Django models, SQLAlchemy entities, Express
  request objects, React components — all belong at the outermost ring.
  Your use cases should be framework-agnostic enough to run in a test
  harness.
- *DTOs at every boundary:* never leak ORM entities or domain objects
  past their layer. Translate.

**SOLID**

- *SRP is about axes of change, not "doing one thing":* a class has a
  single responsibility when it changes for one reason — that reason
  being one stakeholder or one axis of business concern.
- *OCP does not mean "never modify":* it means stable *interfaces* that
  let you add capabilities without cascading changes.
- *LSP violations hide in `isinstance` / `typeof` checks:* if callers
  have to inspect subtypes, the hierarchy is broken.
- *DIP ≠ DI container:* the principle is about dependency direction;
  the container is one mechanism. Constructor injection is enough.

**Patterns**

- *Most singletons are global state in disguise.* Use DI with a single
  instance instead. Ref: oop-knowledge skill § Composition vs Inheritance.
- *Observer and publish-subscribe are not the same:* Observer is in-process
  and synchronous; pub/sub is typically cross-process and asynchronous.
  Conflating them leads to subtle coupling.
- *Repository per aggregate root, not per entity.* One repository, one
  aggregate.

**Event-driven**

- *Commands vs events:* commands are intentions about the future and can
  be rejected; events are facts about the past and cannot. Never mix.
- *Event sourcing ≠ event-driven architecture:* you can use events to
  communicate between services without storing events as the source of
  truth, and vice versa.
- *Schema evolution is the hard part.* Version events from day one.
- *Avoid implicit choreography for multi-step workflows:* use an explicit
  saga / process manager for anything with compensating actions.

**Python idioms (3.12+)**

- Use `@dataclass(frozen=True, slots=True)` for value objects — `__eq__`
  and `__hash__` for free, immutability enforced.
- Prefer `typing.Protocol` (PEP 544) over `abc.ABC` for ports — structural
  typing fits ISP naturally.
- Use `@override` (PEP 698, 3.12+) on every overridden method — catches
  silent LSP drift.
- `match` statements replace type-switch idioms; pair with sealed-style
  unions (`Literal`, discriminated `dataclass`).
- Pydantic v2 for DTOs at layer boundaries (`model_config = ConfigDict(
  frozen=True)` to forbid mutation). Domain objects stay plain.

**TypeScript idioms (5.x)**

- Value objects: branded types + `readonly`:
  `type UserId = string & { readonly __brand: unique symbol }`.
- Domain states: discriminated unions beat class hierarchies for many
  cases. Exhaustive handling via `never`-check default.
- `satisfies` (4.9+) preserves literal types on constants.
- `using` (5.2+) for RAII-style resource management in infrastructure.
- `import type` at every layer boundary keeps the type graph separate
  from the value graph and plays nicely with `erasableSyntaxOnly` (5.8+)
  and Node's native type-stripping.

---

## Output format for design decisions

When explaining or recommending a choice, use this shape. Makes intent
auditable and gives maintainers a learning path.

```markdown
### Design Decision: <short label>

**Recommended approach:** <one line>

**References:**
- *<Book>* — <Author>, Ch. <n>: <one-line takeaway>

**Trade-offs:**
- ✅ <advantage>
- ⚠️ <caveat or cost>

**Why not <alternative>:** <one line, ideally with reference>
```

For code artifacts, cite the pattern inline:

```python
# Architecture: Hexagonal (Ports & Adapters)
# Ref: Percival & Gregory, Architecture Patterns with Python, Ch. 2
class OrderRepository(Protocol): ...
```

```typescript
// Pattern: Strategy — runtime algorithm selection
// Ref: GoF, Design Patterns, p. 315
interface PricingStrategy { calculate(order: Order): Money; }
```

---

## Before declaring "design done"

Run this checklist. Each item maps to a reference section for how to
verify.

- [ ] Ubiquitous language is agreed with the domain expert; code reflects
      it literally (`ddd.md` § Ubiquitous Language).
- [ ] Aggregate boundaries justified (what invariant does this aggregate
      protect?); no transaction spans two aggregates (`ddd.md` §
      Aggregates).
- [ ] Dependency Rule verified — no inner layer imports an outer one
      (`clean-architecture.md` § The Dependency Rule). Enforce with an
      import-linter or `depcheck` in CI.
- [ ] No framework imports inside `domain/` or `application/`
      (`clean-architecture.md` § Frameworks Are Details).
- [ ] DTOs or mappers at every layer boundary; domain objects never cross
      into HTTP or persistence (`clean-architecture.md` § Boundaries).
- [ ] Every outer-to-inner dependency goes through a port (interface)
      owned by the inner layer (`solid.md` § DIP).
- [ ] Domain and application tests run without framework, DB, or network
      (`clean-architecture.md` § Testability).
- [ ] Integration style explicit and documented — sync vs async, commands
      vs events, which operations are eventually consistent
      (`event-driven.md`).
- [ ] Language idioms applied: value objects immutable, ports as
      Protocols/interfaces, DTOs at the edge (`python.md` or
      `typescript.md`).

---

## Templates

Starter scaffolding for the most common structures lives in
`assets/templates/`:

- `assets/templates/aggregate-py.md` — Python aggregate with value
  objects, invariants, domain events.
- `assets/templates/aggregate-ts.md` — TypeScript aggregate with
  branded IDs and discriminated state.
- `assets/templates/use-case-py.md` — Python use-case (interactor)
  with port injection.
- `assets/templates/use-case-ts.md` — TypeScript use-case with port
  injection.

Copy, rename, replace placeholders. Templates are starting points, not
mandates — deviate when the domain calls for it, and note why.

---

## Caveat on authoritative backing

When an O'Reilly MCP or equivalent book-search connector is available,
*search before* making any consequential recommendation — one query
either confirms the direction or surfaces an alternative. If no book
search is connected, cite the canon from memory and mark the claim with
`[unverified]` so the reader knows to double-check. The canonical
references for this skill:

- Evans, *Domain-Driven Design* (2003).
- Vernon, *Implementing Domain-Driven Design* (2013).
- Khononov, *Learning Domain-Driven Design* (2021).
- Martin, *Clean Architecture* (2017), *Clean Code* (2008).
- Gamma, Helm, Johnson, Vlissides, *Design Patterns* (1994).
- Fowler, *Patterns of Enterprise Application Architecture* (2002),
  *Refactoring* (2nd ed., 2018).
- Hohpe & Woolf, *Enterprise Integration Patterns* (2003).
- Percival & Gregory, *Architecture Patterns with Python* (2020).
- Richards & Ford, *Fundamentals of Software Architecture* (2020) and
  *Software Architecture: The Hard Parts* (2021).
- Ramalho, *Fluent Python* (2nd ed., 2022).
