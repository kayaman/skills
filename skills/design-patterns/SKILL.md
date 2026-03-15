---
name: design-patterns
description: Enforces correct application of software design patterns including all 23 Gang of Four patterns and modern additions. Use when selecting a creational, structural, or behavioral pattern, evaluating whether a pattern is appropriate, refactoring toward patterns, reviewing code for pattern-itis or over-engineering, or deciding between pattern-based and language-native solutions.
---

# Design Patterns

Reference: *Design Patterns* (GoF), *Head First Design Patterns* (Freeman & Robson), *Refactoring to Patterns* (Kerievsky)

## When to Apply

- Selecting a pattern for a recurring design problem
- Refactoring code that exhibits a known code smell toward a pattern
- Reviewing whether an applied pattern is justified or over-engineered
- Deciding if a language feature (lambdas, protocols, generics) eliminates the need for a pattern
- Communicating design intent using shared pattern vocabulary

---

## The Two GoF Maxims

Every pattern decision MUST be guided by these two principles:

1. **Program to an interface, not an implementation** — depend on abstractions; swap implementations without changing clients
2. **Favor object composition over class inheritance** — assemble behavior from collaborating objects rather than building class trees

---

## Creational Patterns

Select based on what varies in object creation:

| Pattern | Intent | Use When | Avoid When |
|---------|--------|----------|------------|
| **Abstract Factory** | Create families of related objects without specifying concrete classes | Multiple product families must be interchangeable (e.g., UI themes, platform adapters) | Only one product family exists |
| **Builder** | Separate construction of complex objects from representation | Object has many optional parameters or multi-step construction | Constructor with 1–3 required params suffices |
| **Factory Method** | Let subclasses decide which class to instantiate | The exact type depends on runtime context or configuration | A simple constructor call is clear enough |
| **Prototype** | Create objects by cloning an existing instance | Creating from scratch is expensive or involves complex setup | Object graphs are simple and cheap to construct |
| **Singleton** | Ensure one instance with global access | **Almost never** — prefer DI container-managed lifecycle | Testing, concurrency, or coupling matter (most cases) |

- MUST NOT use Singleton in new code — use dependency injection to manage single-instance lifecycle externally
- SHOULD prefer Builder over telescoping constructors when an object has 4+ configuration options
- SHOULD use Factory Method or Abstract Factory when the concrete type is a decision that should be deferred

---

## Structural Patterns

Select based on how objects and classes are composed:

| Pattern | Intent | Use When | Avoid When |
|---------|--------|----------|------------|
| **Adapter** | Convert an incompatible interface into one clients expect | Integrating third-party code or legacy systems | You control both interfaces and can change one |
| **Bridge** | Decouple abstraction from implementation so both vary independently | Two orthogonal dimensions of variation (e.g., shape × renderer) | Only one dimension varies |
| **Composite** | Treat individual objects and compositions uniformly as a tree | Recursive part-whole hierarchies (file systems, UI components, org charts) | The structure is flat, not tree-shaped |
| **Decorator** | Attach behavior dynamically without subclassing | Adding optional, combinable responsibilities at runtime | Behavior is always required — just put it in the class |
| **Facade** | Simplified interface to a complex subsystem | Clients need a streamlined entry point; subsystem internals should be hidden | The subsystem is already simple |
| **Flyweight** | Share fine-grained objects to save memory | Thousands of similar objects with shared intrinsic state | Object count is small; optimization is premature |
| **Proxy** | Surrogate controlling access (lazy loading, caching, protection, remote) | Access control, expensive initialization, or cross-network access | Direct access has no cost or risk |

- SHOULD use Adapter as the primary pattern for integrating external systems
- SHOULD prefer Decorator over inheritance for optional, combinable behavior
- MUST separate intrinsic (shared) from extrinsic (contextual) state when applying Flyweight

---

## Behavioral Patterns

Select based on how objects communicate and assign responsibility:

| Pattern | Intent | Use When | Avoid When |
|---------|--------|----------|------------|
| **Chain of Responsibility** | Pass request along a chain until handled | Middleware pipelines, event processing, validation chains | A single handler always processes the request |
| **Command** | Encapsulate a request as an object | Undo/redo, queuing, logging, transaction replay | The action is simple and needs no history |
| **Interpreter** | Define grammar and interpret sentences | Small, domain-specific languages (query filters, rules engines) | The grammar is complex — use a parser generator |
| **Iterator** | Sequential access without exposing internals | **Built into virtually all modern languages** — rarely implement manually | Language-native iteration exists |
| **Mediator** | Centralize complex inter-object communication | Many objects with complex, many-to-many interactions | Objects have simple, direct relationships |
| **Memento** | Capture and restore state without breaking encapsulation | Undo, snapshots, time-travel debugging | State is trivial to reconstruct |
| **Observer** | Notify dependents when state changes | Event-driven systems, reactive UI, pub-sub | **Use framework-native reactive patterns** (RxJS, signals, hooks) |
| **State** | Alter behavior when internal state changes | Object behaves differently in distinct states with defined transitions | A simple `if/else` on one flag suffices |
| **Strategy** | Interchangeable algorithm family | Multiple algorithms for the same task, selected at runtime | In FP languages, just pass a lambda/function |
| **Template Method** | Algorithm skeleton with overridable steps | Fixed workflow with varying steps across subclasses | Composition with Strategy achieves the same without inheritance |
| **Visitor** | Add operations to elements without modifying their classes | New operations are frequent; element types are stable | Element hierarchy changes often — every Visitor breaks |

- SHOULD prefer Strategy over Template Method — composition over inheritance
- SHOULD use language-native constructs (iterators, lambdas, reactive streams) before implementing Iterator, Strategy, or Observer manually
- MUST evaluate whether the pattern adds value beyond what the language provides natively

---

## Modern Patterns Beyond GoF

| Pattern | Intent | Context |
|---------|--------|---------|
| **Dependency Injection** | Supply dependencies externally rather than creating them internally | Enables testing, decoupling, and DIP compliance |
| **Null Object** | Provide a no-op implementation instead of null checks | Eliminates `if (x != null)` scattered through code |
| **Repository** | Collection-like interface for aggregate persistence | DDD — one repository per aggregate root |
| **Unit of Work** | Coordinate writes across repositories in a single transaction | Ensuring consistency across multiple aggregates |
| **Specification** | Composable, reusable business rule objects | Complex query/validation logic that must be combined |

---

## When NOT to Use Patterns

**Pattern-itis** — applying patterns speculatively — is worse than the problems patterns solve.

- MUST NOT apply a pattern when only one implementation exists and no variation is foreseeable
- MUST NOT use a pattern the team does not understand — it becomes accidental complexity
- SHOULD NOT apply patterns preemptively — refactor *toward* patterns when complexity emerges (Kerievsky)
- SHOULD start with the simplest thing that works; introduce a pattern when the code smell appears

**Norvig's observation:** 16 of 23 GoF patterns are simplified or eliminated by dynamic language features. Before applying a pattern, ask: *"Does my language already solve this?"*

### Decision Flow

1. Identify the specific code smell or design problem
2. Check if a language feature solves it natively (generics, lambdas, protocols, pattern matching)
3. If not, select the pattern whose intent matches the problem
4. Apply the simplest form of the pattern — avoid gold-plating
5. Verify the pattern improves readability and maintainability for the team

---

## Checklist

Before applying or recommending a pattern, verify:

- [ ] A specific, recurring problem has been identified (not speculative future need)
- [ ] Language-native features have been considered first
- [ ] The selected pattern's intent matches the actual problem
- [ ] The pattern improves — not hinders — code readability for the team
- [ ] Singleton is NOT used (DI container manages lifecycle instead)
- [ ] Composition-based patterns are preferred over inheritance-based ones
- [ ] The pattern is applied in its simplest form without unnecessary abstraction layers
- [ ] The code compiles and passes tests after applying the pattern

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Design Patterns: Elements of Reusable OO Software* | Gamma, Helm, Johnson, Vlissides | Addison-Wesley | 1994 |
| *Head First Design Patterns* (2nd ed.) | Freeman & Robson | O'Reilly | 2021 |
| *Patterns of Enterprise Application Architecture* | Martin Fowler | Addison-Wesley | 2002 |
| *Refactoring to Patterns* | Joshua Kerievsky | Addison-Wesley | 2004 |
| *Dive Into Design Patterns* | Alexander Shvets | Refactoring.Guru | 2021 |
| *Game Programming Patterns* | Robert Nystrom | Genever Benning | 2014 |
| *Fundamentals of Software Architecture* | Mark Richards, Neal Ford | O'Reilly | 2020 |
| *Software Architecture: The Hard Parts* | Ford, Richards, Sadalage, Dehghani | O'Reilly | 2021 |
