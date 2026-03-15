---
name: oop-knowledge
description: >-
  Comprehensive knowledge base covering the main topics from the most
  influential Object-Oriented Programming books. Use when the user asks about
  OOP principles, design patterns, SOLID, refactoring, clean code, object
  thinking, or object-oriented analysis and design. Also useful when reviewing
  code for OOP best practices, discussing trade-offs like composition vs
  inheritance, or applying design patterns to solve structural problems.
license: CC-BY-4.0
metadata:
  author: claude-opus-4-6
  version: "1.0.0"
  model: claude-opus-4-6
  generated: "2026-03-14"
  category: software-engineering
  tags: oop, design-patterns, solid, clean-code, refactoring
---

# Object-Oriented Programming — Core Topics from the Best Books

This skill synthesizes the main topics covered by the most influential and
widely recommended books on Object-Oriented Programming, analysis, and design.
It is organized around the recurring themes that appear across the canon rather
than as a book-by-book summary.

## Foundational OOP Concepts

Every major OOP book builds on four pillars. Understanding these is a
prerequisite for everything else in the discipline.

1. **Abstraction** — Modeling real-world entities by exposing only relevant
   details and hiding complexity. Objects represent concepts, not
   implementation.
2. **Encapsulation** — Bundling data and the methods that operate on it into a
   single unit, restricting direct access to internal state. Protects invariants
   and reduces coupling.
3. **Inheritance** — Defining new classes based on existing ones to promote code
   reuse. Best used for expressing genuine "is-a" relationships, not mere
   convenience.
4. **Polymorphism** — Allowing objects of different types to respond to the same
   message in different ways. Enables flexible, extensible systems and
   eliminates conditional logic (replacing switch statements with polymorphic
   dispatch).

## SOLID Principles

Introduced by Robert C. Martin across several works (*Clean Code*, *Agile
Software Development*, *Clean Architecture*), SOLID is the most widely
referenced set of OOP design guidelines.

- **Single Responsibility Principle (SRP)** — A class should have only one
  reason to change. Each class encapsulates one cohesive responsibility.
- **Open/Closed Principle (OCP)** — Software entities should be open for
  extension but closed for modification. Add behavior through new code, not by
  changing existing code.
- **Liskov Substitution Principle (LSP)** — Subtypes must be substitutable for
  their base types without altering the correctness of the program.
- **Interface Segregation Principle (ISP)** — Clients should not be forced to
  depend on interfaces they do not use. Prefer many small, focused interfaces.
- **Dependency Inversion Principle (DIP)** — High-level modules should not
  depend on low-level modules. Both should depend on abstractions.

## Design Patterns (Gang of Four)

The 23 patterns catalogued in *Design Patterns: Elements of Reusable
Object-Oriented Software* (Gamma, Helm, Johnson, Vlissides — 1994) remain the
most referenced vocabulary in OOP. They are organized into three categories.

### Creational Patterns

Concerned with object creation mechanisms: Abstract Factory, Builder, Factory
Method, Prototype, Singleton.

### Structural Patterns

Concerned with class and object composition: Adapter, Bridge, Composite,
Decorator, Facade, Flyweight, Proxy.

### Behavioral Patterns

Concerned with communication between objects: Chain of Responsibility, Command,
Interpreter, Iterator, Mediator, Memento, Observer, State, Strategy, Template
Method, Visitor.

### Two Guiding Maxims

The GoF book emphasizes two principles above the individual patterns:

- "Program to an interface, not an implementation."
- "Favor object composition over class inheritance."

See [references/design-patterns.md](references/design-patterns.md) for a
detailed breakdown of each pattern with intent and applicability.

## Refactoring and Code Smells

Martin Fowler's *Refactoring* (1999, 2nd ed. 2018) established a disciplined
process for improving existing code through small, behavior-preserving
transformations. Key topics include:

- **Code smells** — Heuristics that indicate structural problems: Long Method,
  Large Class, Feature Envy, Data Clumps, Primitive Obsession, Shotgun
  Surgery, Divergent Change, Duplicated Code, and many more.
- **Refactoring catalog** — Over 70 named transformations such as Extract
  Function, Move Field, Replace Conditional with Polymorphism, Encapsulate
  Collection, and Introduce Parameter Object.
- **The role of testing** — Refactoring depends on a solid test suite. Each
  transformation is small enough that if tests break, the cause is immediately
  identifiable.
- **When to refactor** — Before adding a feature (preparatory refactoring),
  during code review, when comprehension is difficult, or when performance
  profiling reveals unnecessary complexity.

## Clean Code Practices

Robert C. Martin's *Clean Code* (2008) focuses on the craft of writing
readable, maintainable code at the function and class level. Core topics:

- **Meaningful names** — Names should reveal intent, avoid disinformation, and
  be pronounceable and searchable.
- **Small functions** — Functions should do one thing, operate at a single level
  of abstraction, and have few arguments.
- **Comments** — Good code is largely self-documenting. Comments should explain
  *why*, not *what*. Avoid redundant, misleading, or mandated comments.
- **Error handling** — Use exceptions rather than error codes. Do not return or
  pass null. Write try-catch-finally blocks first.
- **Class organization** — Classes should be small, have a single
  responsibility, and exhibit high cohesion.
- **Emergent design** — Kent Beck's four rules of simple design: passes all
  tests, reveals intention, contains no duplication, and has the fewest
  elements.

## Object-Oriented Analysis and Design (OOAD)

Covered extensively by Craig Larman (*Applying UML and Patterns*), Grady Booch
(*Object-Oriented Analysis and Design with Applications*), and Rebecca
Wirfs-Brock (*Object Design: Responsibility-Driven Design*).

- **Responsibility-Driven Design** — Assign responsibilities to objects based
  on the information they hold or the collaborations they participate in (GRASP
  patterns: Creator, Information Expert, Low Coupling, High Cohesion,
  Controller, Polymorphism, Pure Fabrication, Indirection, Protected
  Variations).
- **CRC cards** — Class-Responsibility-Collaboration cards as a design tool for
  discovering objects and their interactions.
- **Use case analysis** — Identifying system behavior from the user's
  perspective and mapping it to object collaborations.
- **Domain modeling** — Creating conceptual models that represent key
  abstractions in the problem domain.

## Composition vs Inheritance

A theme that recurs in nearly every major OOP text:

- Inheritance creates tight coupling between parent and child classes and can
  break encapsulation.
- Composition (delegating behavior to contained objects) provides greater
  flexibility and looser coupling.
- Use inheritance for genuine type hierarchies; use composition for assembling
  behavior from reusable parts.
- The Strategy and Decorator patterns are classic examples of composition
  replacing inheritance.

## Cohesion and Coupling

Two metrics that indicate design quality, discussed across all major texts:

- **High cohesion** — Elements within a module are closely related and focused
  on a single purpose. Aim for this.
- **Low coupling** — Modules have minimal dependencies on each other. Changes
  to one module should not cascade through the system.
- These two properties are the most reliable predictors of maintainable,
  testable software.

## Object Thinking and Philosophy

David West's *Object Thinking* (2004) and Alan Kay's original vision of OOP
emphasize that objects are autonomous entities that communicate through
messages, not mere data containers with attached procedures. Key ideas:

- Objects should model real-world concepts and behaviors, not database rows.
- Message passing (telling objects what to do) is preferable to querying state
  (asking objects for data and acting on it externally).
- The "Tell, Don't Ask" principle encourages moving behavior into the object
  that owns the data.

## Test-Driven Development and OOP

Steve Freeman and Nat Pryce's *Growing Object-Oriented Software, Guided by
Tests* (2009) bridges TDD and OOP design:

- Use tests to drive the discovery of object interfaces and collaborations.
- Mock objects help define boundaries between components.
- Well-designed OO systems are inherently more testable.

## Key Books Referenced

For deeper exploration, consult
[references/bibliography.md](references/bibliography.md) for the full
annotated reading list.
