---
name: object-oriented-programming
description: Enforces object-oriented programming principles including encapsulation, composition over inheritance, GRASP patterns, message passing, and CRC-driven design. Use when designing class hierarchies, assigning responsibilities to objects, evaluating cohesion and coupling, refactoring toward better OO design, or reviewing code for OOP anti-patterns like God Objects and Anemic Domain Models.
---

# Object-Oriented Programming

> **Status:** Draft — book list for review. Content to be added in second round.

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

## Topics to Cover

- Four pillars: abstraction, encapsulation, inheritance, polymorphism
- Alan Kay's original vision: messaging, late-binding, autonomous agents
- Composition vs inheritance and the fragile base class problem
- Cohesion types (functional → coincidental) and coupling types (content → data)
- GRASP patterns (Creator, Information Expert, Low Coupling, High Cohesion, Controller, Polymorphism, Pure Fabrication, Indirection, Protected Variations)
- Object thinking: Tell Don't Ask, Law of Demeter, CRC Cards
- Common pitfalls: God Objects, Anemic Domain Models, deep hierarchies, getter/setter proliferation, Primitive Obsession, Feature Envy
- Modern multi-paradigm approaches: traits/mixins, protocol-oriented programming, Actor Model
