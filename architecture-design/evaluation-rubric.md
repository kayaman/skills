# Evaluation Rubric

A systematic checklist for reviewing an existing system through the
five lenses. Use this for architecture reviews, PR reviews that touch
structural code, or a first pass on an unfamiliar codebase.

Each section produces observations. The final step synthesizes them
into a report.

**How to use:** walk the sections in order. Don't skip. A quick "looks
fine" read without explicit check items misses exactly the problems
you're here to find.

---

## Step 0 — Orient

Answer before opening any file:

- What is this system's purpose in one sentence?
- What bounded contexts do you expect to find?
- Is this a core subdomain (DDD investment worth it) or supporting/
  generic (lighter touch OK)?

Then look at the top-level directory. Does it *scream the domain* or
*scream the framework*? A repo whose root is `models/ controllers/
views/` tells you less than one whose root is `orders/ invoicing/
shipping/`. Ref: Martin, *Clean Architecture*, Ch. 21 (Screaming
Architecture).

---

## Step 1 — Domain model health

Goal: is there a domain model at all? Or just anemic CRUD?

**Checks:**

- [ ] Are there explicit entities, value objects, and aggregates in the
      codebase? (Search for `@dataclass(frozen=True)` in Python,
      branded types or `private constructor` in TypeScript.)
- [ ] Do entity classes have behavior, or are they just fields plus
      getters/setters?
- [ ] Do method names match the domain language? (Example:
      `order.ship()` vs `order.setStatus("shipped")`.)
- [ ] Are invariants enforced in the constructor or factory, not in
      validation layers?
- [ ] Are there value objects for money, identifiers, emails, dates,
      or are these passed as raw primitives?
- [ ] Is aggregate size reasonable? (A root with a handful of child
      value objects, typically.)
- [ ] Is there one repository per aggregate root, or one per entity?

**Common findings:**

- **Anemic domain model.** Business logic lives in services; entities
  are data bags. Ref: `ddd.md` § Anti-Patterns; Fowler's essay.
- **Primitive obsession.** Strings and ints pretending to be domain
  concepts. Ref: `python.md` § Value Objects; `typescript.md` §
  Branded types.
- **Aggregate bloat.** A `Customer` aggregate containing orders,
  preferences, invoices, addresses. Ref: `ddd.md` § Aggregate rules.
- **Ubiquitous language drift.** Code talks about "users" while the
  business talks about "members". Ref: `ddd.md` § Ubiquitous Language.

---

## Step 2 — Layer integrity

Goal: does the Dependency Rule hold?

**Checks:**

- [ ] Does the codebase have distinguishable layers (domain,
      application, adapters, infrastructure)?
- [ ] Grep the domain layer for framework imports:
      `grep -r "from django" src/*/domain/`,
      `grep -r "from flask" src/*/domain/`,
      `grep -r "import express" src/*/domain/`,
      `grep -r "from prisma" src/*/domain/`.
      **Every match is a violation.**
- [ ] Does the application layer import concrete infrastructure
      classes, or only ports? (Constructor parameters should be typed
      as Protocols/interfaces.)
- [ ] Are ORM entities used directly in HTTP handlers, or is there
      a mapping step?
- [ ] Can domain and application tests run without a database or web
      server?

**Common findings:**

- **Framework bleed into the domain.** `from django.db import models`
  in a supposedly framework-agnostic module. Ref: `clean-architecture.md`
  § Frameworks Are Details.
- **ORM entities leaked across layers.** SQLAlchemy / Prisma /
  TypeORM objects returned from services. Fix: map at the repository
  boundary.
- **Use cases directly instantiating adapters.** Should be injected,
  not constructed inside use case logic.
- **No DTOs at HTTP boundary.** Request and response bodies are
  serialized domain objects; internal fields accidentally exposed.

---

## Step 3 — SOLID adherence

Goal: class-level design quality.

**Checks:**

- [ ] Find the largest class in the codebase. Is it over 300 lines?
      Over 500? Over 1000?
- [ ] Does any class named `Manager`, `Helper`, `Utility`, `Service` do
      more than one thing?
- [ ] Are there interfaces with more than 7 methods? (ISP smell.)
- [ ] Grep for `isinstance(` or `typeof ==` in business logic — each
      is a potential LSP smell.
- [ ] Does adding a new variant (new customer type, new payment
      method, new report) require editing existing classes or only
      adding new ones? (OCP test.)
- [ ] Do high-level modules (use cases) import low-level concrete
      classes directly? (DIP violation.)

**Common findings:**

- **God class.** One class does 80% of the work. Ref: `solid.md` § SRP;
  Fowler, *Refactoring*, "Large Class".
- **Fat interface.** One `Document` interface used for reading,
  writing, rendering, indexing. Ref: `solid.md` § ISP.
- **LSP violation hidden in runtime checks.** `if (obj instanceof
  ReadOnlyList) skip(); else modify(obj)`. Extract a narrower
  interface.
- **DIP in name only.** An interface exists, but only one implementation,
  owned by the low-level module — it's not actually inverted.

---

## Step 4 — Pattern usage (and misuse)

Goal: are patterns applied where they add value?

**Checks:**

- [ ] Any `Singleton` classes? Are they genuinely global stateless
      services, or hidden global mutable state?
- [ ] Any "service locator" / global registry pattern? (Sometimes a
      DI container in disguise; sometimes an opaque global.)
- [ ] Factories with one implementation and one call site? (Probably
      overkill.)
- [ ] Decorators stacked three deep on a use case? (Good — cross-
      cutting concerns orthogonal to domain logic.)
- [ ] Strategy used with only one strategy? (Premature abstraction.)
- [ ] Observer used across process boundaries? (Should be messaging.)

**Common findings:**

- **Singleton as global state.** `UserContext.current()` returning a
  thread-local or a module-global. Testing becomes a nightmare.
- **Service locator.** Every class calls `container.resolve(...)`.
  Dependencies are hidden from constructors.
- **Premature Strategy.** Interface with one implementation, no clear
  second one on the horizon. Inline the concrete class until the
  second variant appears.

---

## Step 5 — Integration style

Goal: are boundaries explicit? Is the messaging mature?

**Checks:**

- [ ] What is the longest synchronous call chain between services?
      (Over three hops is a smell — each hop compounds latency and
      failure probability.)
- [ ] Are messages classifiable as commands or events, or is
      everything just "messages"?
- [ ] Is there an outbox pattern (or equivalent) for dual-write
      safety?
- [ ] Are consumers idempotent? How is this verified?
- [ ] Are event schemas versioned? Is there a registry?
- [ ] For workflows that span multiple services, is there an explicit
      saga / process manager, or implicit choreography?
- [ ] Does CQRS exist where justified (different read/write load or
      shape), or only where fashionable?
- [ ] Is event sourcing used because audit is a requirement, or
      because someone thought events are cool?

**Common findings:**

- **Chatty synchronous chains.** A→B→C→D for a single request. Tail
  latency amplifies; one slow service drags everyone.
- **Missing outbox.** Events published with a `try/except` around a
  broker call. Silent loss on DB commit / broker failure race.
- **Event spaghetti.** 12 services, 40 event types, no way to see a
  whole workflow. Reach for orchestration.
- **CQRS with no payoff.** Two models, continuous divergence, no
  measurable read-performance win.

---

## Step 6 — Language idioms

Goal: is the language used well?

**Python**

- [ ] `@dataclass(frozen=True)` for value objects?
- [ ] `typing.Protocol` for ports, or unnecessary `abc.ABC`?
- [ ] `@override` on overridden methods?
- [ ] `match` statement or `isinstance` chain?
- [ ] Pydantic (v2) for DTOs at the boundary, plain classes in the
      domain?
- [ ] Type checker configured strictly and running in CI?

**TypeScript**

- [ ] Branded types for IDs, or bare `string`?
- [ ] Discriminated unions for domain states, or class hierarchies that
      could be flatter?
- [ ] `readonly` and `as const` used consistently for immutability?
- [ ] `satisfies` on config constants?
- [ ] `import type` at layer boundaries?
- [ ] Zod / Valibot / ArkType at HTTP boundaries, or ad hoc
      validation?
- [ ] `strict: true` in `tsconfig.json`?
- [ ] Exhaustive `switch` with `never` default?

Full detail in `python.md` and `typescript.md`.

---

## Step 7 — Testing

Goal: does the test suite match the architecture?

**Checks:**

- [ ] Ratio of unit to integration to E2E tests roughly matches the
      test pyramid? (many fast unit; fewer integration; few E2E)
- [ ] Do application-layer tests run without a database?
- [ ] Are there integration tests specifically for repository
      implementations?
- [ ] Does every aggregate have tests for its invariants?
- [ ] Test suite runtime under 30 seconds for the fast tests?

Ref: Freeman & Pryce, *Growing Object-Oriented Software, Guided by
Tests*; Khorikov, *Unit Testing Principles, Practices, and Patterns*.

---

## Synthesis — producing the report

Walk back through your observations and assemble:

```markdown
# Architecture Review — <system>

## Snapshot
- Subdomain class: core / supporting / generic
- Overall health: green / yellow / red
- Top risk: <one sentence>

## Domain model
Findings:
- …
References: ddd.md, python.md/typescript.md

## Layer integrity
Findings:
- …
References: clean-architecture.md

## SOLID
Findings:
- …
References: solid.md

## Patterns
Findings:
- …
References: design-patterns.md

## Integration
Findings:
- …
References: event-driven.md

## Recommended next steps
1. <highest-impact, smallest-cost first>
2. …
3. …

## Decisions worth revisiting
- <decision>: <why it might be wrong> → <alternative>
```

**On prioritization.** Rank recommendations by **impact / effort**. A
missing outbox pattern in a production event-driven system is a red
flag worth fixing now. A handful of minor naming drifts can sit in the
backlog.

**Don't let perfect be the enemy of good.** Few real systems ace every
check. Focus on structural risks that will compound: violations of
the Dependency Rule, missing outbox/idempotency, absent bounded
context boundaries. Polish naming and pattern nuance after the
foundation is sound.
