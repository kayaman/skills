---
name: object-oriented-programming
description: Enforces object-oriented programming principles including encapsulation, composition over inheritance, GRASP patterns, message passing, and CRC-driven design. Use when designing class hierarchies, assigning responsibilities to objects, evaluating cohesion and coupling, refactoring toward better OO design, or reviewing code for OOP anti-patterns like God Objects and Anemic Domain Models.
---

# Object-Oriented Programming

Reference: *Practical Object-Oriented Design* (Metz), *Object Thinking* (West), *Applying UML and Patterns* (Larman)

## When to Apply

- Designing new classes or assigning responsibilities to existing ones
- Evaluating whether inheritance or composition is appropriate
- Reviewing code for cohesion, coupling, or responsibility assignment
- Refactoring God Objects, Anemic Domain Models, or deep hierarchies
- Deciding between Tell Don't Ask and query-based approaches
- Modeling a problem domain with objects, roles, and collaborations

---

## Core Design Principles

### Message-Passing First

Objects are autonomous agents communicating via messages. Design starts with **what messages are sent**, not what data is stored. Alan Kay's definition: *"OOP means only messaging, local retention and protection and hiding of state-process, and extreme late-binding of all things."*

- MUST design public interfaces (messages) before internal implementation
- MUST treat objects as black boxes — interact only through their public protocol
- SHOULD ask "what message should I send?" before "what data do I need?"

### The Four Pillars — Applied

| Pillar | Design Rule | Violation Signal |
|--------|-------------|-----------------|
| **Abstraction** | Hide complexity behind intention-revealing interfaces | Callers need to understand implementation to use the object |
| **Encapsulation** | Bundle data and behavior; restrict direct access to state | Public getters/setters exposing internal structure |
| **Inheritance** | Use ONLY for stable "is-a" where Liskov Substitution holds | Subclass overrides methods to do nothing, or breaks parent contracts |
| **Polymorphism** | Vary behavior through interchangeable objects sharing an interface | `if/else` or `switch` chains checking object type |

---

## Responsibility Assignment — GRASP Patterns

When deciding which object should handle a responsibility, apply these patterns in order of priority (Larman):

| Pattern | Rule | Apply When |
|---------|------|------------|
| **Information Expert** | Assign to the class that has the data needed | Default starting point for any responsibility |
| **Creator** | Assign creation to the class that aggregates, contains, or closely uses the target | Deciding where to put `new`/factory calls |
| **Low Coupling** | Among alternatives, choose the design that reduces dependencies | Comparing two valid designs |
| **High Cohesion** | Keep classes focused on a single purpose | A class is growing responsibilities beyond its core concern |
| **Controller** | A non-UI object receives and coordinates system events | Handling user actions or external triggers |
| **Polymorphism** | Use polymorphic dispatch instead of conditionals on type | `if/switch` testing object type to decide behavior |
| **Pure Fabrication** | Create a non-domain service class when Expert leads to poor cohesion | Expert assignment would bloat a domain object |
| **Indirection** | Introduce a mediating object to decouple two others | Two objects are too tightly coupled but need to collaborate |
| **Protected Variations** | Wrap predicted variation points behind stable interfaces | A known requirement may change in the future |

- MUST apply Information Expert as the default responsibility assignment strategy
- MUST use Polymorphism instead of type-checking conditionals
- SHOULD evaluate Low Coupling and High Cohesion when choosing between alternative designs
- SHOULD introduce Pure Fabrication only when Expert creates cohesion problems

---

## Composition vs Inheritance

**Default to composition. Use inheritance only when ALL of these hold:**

1. The relationship is genuinely, permanently "is-a" (not "has-a" or "behaves-like-a")
2. The subclass is a true specialization — it uses everything from the parent
3. Liskov Substitution holds: substituting the subclass for the parent breaks nothing
4. The hierarchy is shallow (SHOULD NOT exceed 2–3 levels)

**Composition advantages:**

- Black-box reuse — no exposure of internal implementation
- Runtime flexibility — swap collaborators without changing class structure
- Avoids the fragile base class problem — base changes don't silently break subclasses

| Technique | Use For | Example |
|-----------|---------|---------|
| **Delegation** | Forwarding behavior to a collaborator | `class Order { private pricing: PricingPolicy }` |
| **Traits / Mixins** | Sharing behavior across unrelated types without inheritance | Rust traits, Kotlin interfaces with default methods, PHP traits |
| **Strategy / Policy** | Varying one algorithm dimension | Interchangeable `ShippingCalculator` implementations |
| **Decorator** | Adding behavior dynamically | Wrapping a `Logger` around a `Repository` |

---

## Cohesion and Coupling

### Cohesion (aim for the top)

| Type | Quality | Description |
|------|---------|-------------|
| **Functional** | Best | All elements serve a single, well-defined task |
| **Sequential** | Good | Output of one element feeds the next |
| **Communicational** | Acceptable | Elements operate on the same data |
| **Procedural** | Weak | Elements follow a sequence but share no data |
| **Temporal** | Weak | Elements run at the same time (e.g., initialization) |
| **Logical** | Poor | Elements are grouped by category, not purpose |
| **Coincidental** | Worst | Random grouping — utility grab-bags |

### Coupling (aim for the bottom)

| Type | Quality | Description |
|------|---------|-------------|
| **Content** | Worst | One module modifies another's internals directly |
| **Common** | Poor | Modules share global mutable state |
| **External** | Weak | Modules depend on the same external format or protocol |
| **Control** | Weak | One module passes a flag controlling another's behavior |
| **Stamp** | Acceptable | Modules share a composite data structure but use different parts |
| **Data** | Best | Modules exchange only the parameters they need |

- MUST NOT introduce content coupling — never reach into another object's internals
- MUST NOT use global mutable state as a communication channel between objects
- SHOULD prefer data coupling — pass only the specific values needed
- SHOULD eliminate control coupling by replacing flag parameters with polymorphism

---

## Object Thinking — Tell, Don't Ask

Design objects as **autonomous virtual persons** (West). Command them to act rather than querying their state and deciding externally.

**Tell, Don't Ask:**

```
# BAD — Ask: querying state, deciding externally
if order.status == "paid" and order.items_in_stock():
    warehouse.ship(order)

# GOOD — Tell: the object decides internally
order.fulfill()  # Order knows its own rules
```

**Law of Demeter** — only talk to immediate collaborators:

- MUST NOT chain through intermediaries: `a.getB().getC().doSomething()`
- MUST send messages only to: `self`, parameters, instance variables, objects you create, or direct collaborators
- If you need to reach deep, the intermediate object is missing a responsibility

**CRC Cards** (Class-Responsibility-Collaboration):

Use when discovering object roles in design sessions. Each card lists:
- **Class name** — a noun representing a domain concept
- **Responsibilities** — what the object knows and does (verbs)
- **Collaborators** — other objects it needs to fulfill responsibilities

Walk through use cases, role-playing objects. Missing responsibilities reveal missing objects.

---

## Anti-Patterns and Remedies

| Anti-Pattern | Signal | Remedy |
|-------------|--------|--------|
| **God Object** | One class knows and does too much; most other classes are data holders | Extract responsibilities using Information Expert; apply SRP |
| **Anemic Domain Model** | Objects are data bags with getters/setters; all logic in service classes | Move behavior into domain objects — Tell, Don't Ask |
| **Deep Hierarchy** | 4+ inheritance levels; changes at the top cascade unpredictably | Flatten to max 2–3 levels; replace inheritance with composition |
| **Getter/Setter Proliferation** | Every field has public get/set; encapsulation is broken | Remove getters; ask the object to perform the operation instead |
| **Primitive Obsession** | Using raw strings, ints for domain concepts (email, money, ID) | Introduce Value Objects: `EmailAddress`, `Money`, `OrderId` |
| **Feature Envy** | A method uses more data from another class than its own | Move the method to the class whose data it uses |
| **Refused Bequest** | Subclass overrides inherited methods to do nothing or throw | Replace inheritance with composition; the relationship isn't "is-a" |

---

## Modern OO — Multi-Paradigm Pragmatism

Pure OO dogma has given way to blending OO encapsulation with FP immutability and higher-order functions. Apply these guidelines:

- SHOULD prefer immutable value objects over mutable entities where possible
- SHOULD use traits/mixins/protocols for behavior sharing instead of inheritance
- SHOULD use higher-order functions (lambdas, closures) where Strategy or Command patterns add unnecessary ceremony
- SHOULD consider the Actor Model (Erlang, Akka, Swift concurrency) for concurrent message-passing systems

---

## Checklist

Before finalizing an object-oriented design, verify:

- [ ] Responsibilities are assigned using Information Expert as the default
- [ ] Public interfaces are defined before internal implementation
- [ ] Inheritance is used only for stable, shallow "is-a" with Liskov Substitution
- [ ] Composition is used for "has-a", "behaves-like-a", and cross-cutting behavior
- [ ] No God Objects — every class has a single, focused purpose
- [ ] No Anemic Domain Models — objects contain behavior, not just data
- [ ] Law of Demeter is respected — no method chain trains
- [ ] No type-checking conditionals — polymorphism handles variation
- [ ] Value Objects replace primitive types for domain concepts
- [ ] Coupling is at the data or stamp level, never content or common

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Practical Object-Oriented Design* (2nd ed.) | Sandi Metz | Addison-Wesley | 2018 |
| *Head First Object-Oriented Analysis and Design* | McLaughlin, Pollice, West | O'Reilly | 2006 |
| *Growing Object-Oriented Software, Guided by Tests* | Freeman & Pryce | Addison-Wesley | 2009 |
| *Design Patterns: Elements of Reusable OO Software* | Gamma, Helm, Johnson, Vlissides | Addison-Wesley | 1994 |
| *Object Thinking* | David West | Microsoft Press | 2004 |
| *Elegant Objects* Vol 1 & 2 | Yegor Bugayenko | Self-published | 2016–2017 |
| *Applying UML and Patterns* (3rd ed.) | Craig Larman | Prentice Hall | 2004 |
| *Object-Oriented Software Construction* | Bertrand Meyer | Prentice Hall | 1997 |
| *Balancing Coupling in Software Design* | Vlad Khononov | Addison-Wesley | 2024 |
| *A Philosophy of Software Design* (2nd ed.) | John Ousterhout | Stanford | 2021 |
