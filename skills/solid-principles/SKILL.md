---
name: solid-principles
description: Enforces SOLID principles (SRP, OCP, LSP, ISP, DIP) in object-oriented and multi-paradigm code. Use when designing classes and interfaces, evaluating responsibility assignment, reviewing code for coupling issues, applying dependency inversion, refactoring fat interfaces, or checking that subtypes are truly substitutable.
---

# SOLID Principles

Reference: *Clean Architecture* (Martin), *Practical Object-Oriented Design* (Metz), *Code That Fits in Your Head* (Seemann)

## When to Apply

- Designing new classes, interfaces, or modules
- Reviewing code for responsibility bloat, coupling, or substitutability issues
- Refactoring a class that changes for multiple unrelated reasons
- Evaluating whether an abstraction or interface is appropriately sized
- Deciding where dependencies should point in a layered or modular architecture
- Resolving the tension between SOLID extensibility and YAGNI simplicity

---

## S — Single Responsibility Principle

**Refined definition (Martin, 2017):** *"A module should be responsible to one, and only one, actor."*

SRP is about **people and change reasons**, not "doing one thing." A class violates SRP when changes requested by different stakeholders (actors) would modify the same class.

**Classic example:** An `Employee` class with `calculatePay()` (CFO's team), `reportHours()` (COO's team), and `save()` (CTO's team). A shared `regularHours()` method creates accidental coupling — when the CFO's team changes the pay calculation, the COO's hours report silently breaks.

### Rules

- MUST identify which actor (stakeholder/team) each class serves
- MUST separate classes that serve different actors, even if they use similar data
- SHOULD use SRP as the primary driver for class extraction during refactoring
- Violation signals: class name includes "And" or "Manager"; class changes for unrelated business reasons

---

## O — Open/Closed Principle

*"Software entities should be open for extension, but closed for modification."*

Achieve this through **abstract interfaces and polymorphism**, not inheritance hierarchies. New behavior is added by creating new implementations, not by modifying existing code.

### Rules

- MUST use polymorphic dispatch (interface implementations) instead of `if/else` or `switch` chains that check type
- SHOULD design plugin points at known variation boundaries — but only where variation has been demonstrated
- MUST NOT add speculative extension points "just in case" — this violates YAGNI
- Martin's caveat: *"Since closure cannot be complete, it must be strategic"* — choose which changes to protect against based on experience

| Violation Signal | Remedy |
|-----------------|--------|
| `switch` on type or enum to decide behavior | Extract interface; create implementations per case |
| Adding a new feature requires modifying existing classes | Introduce abstraction at the variation point |
| Shotgun surgery — one change touches many files | Consolidate related behavior behind a single interface |

---

## L — Liskov Substitution Principle

**Liskov (1987):** Subtypes MUST be substitutable for their base types without altering program correctness.

This is **behavioral subtyping** — semantic, not just syntactic. The compiler won't catch most violations.

### Formal Constraints

| Constraint | Rule |
|-----------|------|
| **Preconditions** | A subtype MUST NOT strengthen preconditions (cannot require more from callers) |
| **Postconditions** | A subtype MUST NOT weaken postconditions (must deliver at least what the parent promises) |
| **Invariants** | A subtype MUST preserve all invariants of the parent type |
| **History Constraint** | A subtype MUST NOT allow state changes the parent would not allow |

### The Rectangle/Square Problem

`Square` cannot be a subtype of `Rectangle` because setting width independently of height violates `Rectangle`'s behavioral contract (width and height are independent). The "is-a" relationship in the real world does not imply "is-a-subtype" in code.

### Rules

- MUST verify that overridden methods honor the parent's contract, not just its signature
- MUST NOT throw `UnsupportedOperationException` or `NotImplementedException` in subtype methods — this is an LSP violation
- MUST NOT override a method to do nothing or return a hardcoded dummy value
- SHOULD use "Design by Contract" (Meyer): document and enforce preconditions, postconditions, and invariants

---

## I — Interface Segregation Principle

*"No client should be forced to depend on methods it does not use."*

Fat interfaces force implementors to provide dummy implementations or throw exceptions for methods they don't need — violating both ISP and LSP.

### Rules

- MUST split fat interfaces into focused **role interfaces** based on client needs
- MUST NOT create a single interface that serves all possible clients
- SHOULD name role interfaces by capability: `Printable`, `Serializable`, `ForPlacingOrders` — not by implementation: `PrinterInterface`
- ISP applies to APIs too: SHOULD NOT force API consumers to parse responses containing data they don't need

| Violation Signal | Remedy |
|-----------------|--------|
| Implementors throw `UnsupportedOperationException` for some methods | Split into role interfaces; implement only what applies |
| Interface has methods used by different, unrelated clients | Extract client-specific interfaces |
| A change to one method forces recompilation of unrelated clients | Segregate into independent interfaces |

---

## D — Dependency Inversion Principle

Two parts:
- **(A)** High-level modules MUST NOT depend on low-level modules — both depend on abstractions
- **(B)** Abstractions MUST NOT depend on details — details depend on abstractions

### DIP vs DI vs IoC

| Term | What It Is | Level |
|------|-----------|-------|
| **DIP** | Design principle — depend on abstractions, not concretions | Architecture principle |
| **DI (Dependency Injection)** | Pattern — supply dependencies from outside via constructor, setter, or method | Implementation technique |
| **IoC (Inversion of Control)** | Paradigm — framework calls your code, not the other way around | Broad principle |

### Rules

- MUST define interfaces in the high-level module, not the low-level module (the abstraction belongs to the consumer)
- MUST use constructor injection as the default DI mechanism
- MUST NOT instantiate concrete dependencies inside business logic classes (`new ConcreteService()`)
- SHOULD use a DI container or composition root to wire dependencies at application startup
- SHOULD NOT depend on concrete classes across module boundaries — always go through an interface

---

## How SOLID Principles Interconnect

```
SRP ──enables──▶ OCP (single-responsibility classes are extended, not modified)
DIP ──enables──▶ OCP (abstractions allow substitutable implementations)
LSP ──ensures──▶ OCP extensions don't break behavior
ISP ──prevents─▶ LSP violations (no unsupported methods forcing dummy implementations)
```

All five principles converge on one practice: **program to an interface**.

---

## SOLID in Different Paradigms

### Functional Programming

| Principle | FP Equivalent |
|-----------|--------------|
| SRP | Functions and modules have a single purpose |
| OCP | Higher-order functions extend behavior without modifying existing functions |
| LSP | Function signatures are contracts; substituting compatible functions preserves correctness |
| ISP | Modules export only what consumers need; minimal public APIs |
| DIP | Pass functions as parameters instead of depending on concrete implementations |

### Microservices

| Principle | Microservice Equivalent |
|-----------|------------------------|
| SRP | Each service owns a single business capability |
| OCP | Stable API contracts; new behavior via new endpoints or new services |
| LSP | Consumer-driven contract tests verify substitutability |
| ISP | Minimal endpoint surface per service; BFF pattern for client-specific APIs |
| DIP | Message queues and event buses as abstractions between services |

---

## Balancing SOLID with Simplicity

SOLID principles are **guidelines, not rigid rules**. Apply them where complexity warrants it.

- MUST NOT create an interface for every class — only when there are (or will be) multiple implementations or the boundary needs testing isolation
- MUST NOT split a simple class into fragments just to satisfy SRP dogmatically
- SHOULD apply SOLID when a code smell appears (shotgun surgery, divergent change, parallel inheritance), not preemptively
- SHOULD balance OCP extensibility against YAGNI: being "open for extension" (good structure) is not the same as "already extended" (speculative code)

---

## Checklist

When designing or reviewing code, verify:

- [ ] Each class is responsible to one actor — changes for different business reasons live in different classes
- [ ] New behavior is added via new implementations, not by modifying existing code (where variation is known)
- [ ] Subtypes are fully substitutable — no `UnsupportedOperationException`, no weakened contracts
- [ ] Interfaces are segregated by client role — no implementor is forced to provide dummy methods
- [ ] Dependencies point toward abstractions — high-level modules define the interfaces they need
- [ ] Constructor injection is used for all required dependencies
- [ ] No speculative abstractions — every interface has a demonstrated need
- [ ] SOLID is balanced against KISS/YAGNI — the right level of abstraction for the current complexity

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Agile Software Development: Principles, Patterns, and Practices* | Robert C. Martin | Pearson | 2002 |
| *Clean Architecture* | Robert C. Martin | Pearson | 2017 |
| *Practical Object-Oriented Design* (2nd ed.) | Sandi Metz | Addison-Wesley | 2018 |
| *Code That Fits in Your Head* | Mark Seemann | Addison-Wesley | 2021 |
| *A Philosophy of Software Design* (2nd ed.) | John Ousterhout | Stanford | 2021 |
| *Object-Oriented Software Construction* | Bertrand Meyer | Prentice Hall | 1997 |
| *Get Your Hands Dirty on Clean Architecture* (2nd ed.) | Tom Hombergs | Packt | 2023 |
