---
name: oreilly-design-reference
description: >-
  O'Reilly book reference lookup for software design decisions. Coding agents
  MUST use this skill whenever making or reviewing any design decision — choosing
  an architecture pattern, selecting a data structure, structuring a module,
  evaluating a library, deciding on an API contract, applying a design pattern,
  weighing trade-offs between approaches, or any moment where a choice between
  two or more implementation strategies comes up. The O'Reilly MCP handles the
  actual book search; this skill tells you how and when to invoke it. Trigger
  even for seemingly small decisions (naming, layering, concurrency model,
  error handling strategy) — the best engineers reach for authoritative
  references before committing to an approach.
metadata:
  author: marco
  version: "1.0.0"
  category: software-engineering
  tags: oreilly, design-decisions, architecture, patterns, references, coding-agent
---

# O'Reilly Design Reference

A skill for coding agents that ensures every significant design decision is
grounded in authoritative, book-level knowledge via the O'Reilly MCP.

---

## Prime Directive

> **Before committing to any design decision, search O'Reilly for references.**

This is not optional. Even if you are confident in an approach, a 5-second
O'Reilly lookup either confirms your direction with authoritative backing or
surfaces a better alternative you hadn't considered. The O'Reilly MCP does the
heavy lifting — your job is to know *when* and *how* to invoke it.

---

## When to Trigger a Reference Lookup

Invoke the O'Reilly MCP search on **any** of the following signals:

### Architecture & Structure
- Choosing between monolith, microservices, modular monolith, event-driven, or
  layered architectures
- Deciding on module boundaries, package layout, or dependency direction
- Evaluating hexagonal/ports-and-adapters, clean architecture, or DDD patterns
- Designing an API (REST, GraphQL, gRPC, message-based)

### Design Patterns & Principles
- Applying or questioning a GoF design pattern (Factory, Strategy, Observer, …)
- Applying SOLID, GRASP, or other OO principles
- Deciding between composition and inheritance
- Identifying code smells and choosing refactoring techniques

### Data & State
- Choosing a data structure (tree vs. graph, list vs. set, …)
- Designing a schema or domain model
- Evaluating caching strategies, consistency models, or storage engines
- Deciding on state management approach (immutability, event sourcing, CQRS, …)

### Concurrency & Performance
- Choosing between threading, async/await, actor model, or CSP
- Designing for scalability or latency
- Evaluating locking strategies, lock-free structures, or backpressure

### Error Handling & Resilience
- Choosing an error propagation strategy (exceptions vs result types vs panic)
- Designing retry, circuit-breaker, or fallback logic
- Evaluating fault-isolation boundaries

### Testing & Quality
- Deciding on a testing strategy (unit vs integration vs contract vs E2E)
- Choosing test doubles (mock vs stub vs fake vs spy)
- Evaluating TDD or BDD workflows

### Language & Library Choices
- Evaluating a library or framework against alternatives
- Deciding on a serialization format (JSON, Protobuf, Avro, …)
- Choosing between language idioms (e.g., dataclasses vs TypedDict in Python)

---

## How to Use the O'Reilly MCP

The **O'Reilly MCP** is the tool that performs the actual book and content
search. When it is connected, coding agents should call it directly with a
well-formed query. Do **not** attempt to answer design questions from memory
alone when this MCP is available.

### Query Construction

Good queries are specific. Include:
1. The **decision type** (pattern, architecture, data structure, …)
2. The **domain or context** (distributed systems, frontend, ML pipelines, …)
3. Optional: **language or ecosystem** (Python, Go, TypeScript, …)

**Examples of good queries:**
```
"event sourcing vs CQRS trade-offs distributed systems"
"repository pattern domain-driven design"
"async error handling Python"
"observer pattern vs event bus"
"database sharding strategies horizontal scaling"
"dependency injection vs service locator"
"API versioning strategies REST"
"circuit breaker pattern resilience"
```

**Examples of poor queries (too vague):**
```
"design patterns"         # too broad
"how to code"             # not a design decision
"Python tutorial"         # not a design question
```

### Lookup Workflow

```
1. IDENTIFY the design decision at hand
        ↓
2. FORMULATE a specific O'Reilly search query
        ↓
3. CALL the O'Reilly MCP search tool
        ↓
4. REVIEW the returned book excerpts, titles, and chapter references
        ↓
5. CITE the relevant source(s) in your explanation or PR comment
        ↓
6. APPLY the guidance — or explicitly note why you're diverging from it
```

### Multiple Perspectives

For consequential decisions (architectural choices, public API design, major
refactors), run **2–3 searches** with different angles:

```
Search 1: the pattern you're considering ("event sourcing implementation")
Search 2: the alternative ("CQRS without event sourcing")
Search 3: trade-off framing ("event sourcing drawbacks complexity")
```

This surfaces the full picture before committing.

---

## How to Present Findings

When reporting back to the developer, structure your reference-backed answer:

```markdown
### Design Decision: [brief label]

**Recommended approach:** [your recommendation]

**O'Reilly references:**
- *[Book Title]* — [Author]: [one-sentence summary of relevant guidance]
- *[Book Title]* — [Author]: [one-sentence summary of relevant guidance]

**Trade-offs considered:**
- ✅ [Advantage of chosen approach]
- ⚠️  [Trade-off or caveat]

**Why not [alternative]:** [brief reasoning, ideally backed by a reference]
```

---

## Citing References in Code

For design decisions baked into the codebase, add a reference comment:

```python
# Architecture: Hexagonal (Ports & Adapters)
# Ref: "Architecture Patterns with Python" — Percival & Gregory, Ch. 2
class OrderRepository(AbstractRepository):
    ...
```

```typescript
// Pattern: Strategy — delegates algorithm selection to runtime
// Ref: "Design Patterns" — GoF, p. 315
interface PricingStrategy {
  calculate(order: Order): Money;
}
```

This makes architectural intent explicit and gives future maintainers a
learning path.

---

## When the O'Reilly MCP Is Not Connected

If the O'Reilly MCP is unavailable:
1. **Flag it clearly** — note that authoritative references could not be
   retrieved.
2. **Use the oop-knowledge skill** as a fallback for OOP/pattern decisions
   (if installed).
3. **Fall back to general knowledge** but explicitly mark it as
   unverified: `[no O'Reilly reference — recommend manual lookup]`.
4. **Recommend the developer** search `learning.oreilly.com` manually with
   the query you would have used.

Never silently skip the reference step — always surface the gap.

---

## Quick-Reference: Common Decision → Query Mapping

| Design Decision | Suggested O'Reilly Query |
|---|---|
| Microservices vs monolith | `"microservices trade-offs monolith migration"` |
| Event-driven architecture | `"event-driven architecture patterns messaging"` |
| Domain model design | `"domain-driven design aggregate bounded context"` |
| Async task queue | `"task queue worker pattern async processing"` |
| REST API design | `"REST API design best practices versioning"` |
| Database choice | `"polyglot persistence database selection patterns"` |
| Dependency injection | `"dependency injection inversion of control containers"` |
| Testing strategy | `"test pyramid integration testing strategy"` |
| Error handling | `"error handling resilience fault tolerance patterns"` |
| Caching | `"caching strategies invalidation distributed cache"` |
| Auth/AuthZ | `"authentication authorization OAuth JWT patterns"` |
| CI/CD pipeline | `"continuous delivery deployment pipeline patterns"` |
