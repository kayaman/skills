---
name: solid-principles
description: Enforces SOLID principles (SRP, OCP, LSP, ISP, DIP) in object-oriented and multi-paradigm code. Use when designing classes and interfaces, evaluating responsibility assignment, reviewing code for coupling issues, applying dependency inversion, refactoring fat interfaces, or checking that subtypes are truly substitutable.
---

# SOLID Principles

> **Status:** Draft — book list for review. Content to be added in second round.

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

## Topics to Cover

- SRP: "responsible to one actor" (Martin's refined definition), relationship to high cohesion
- OCP: open for extension, closed for modification — via interfaces and polymorphism, not inheritance
- LSP: behavioral subtyping, the Rectangle/Square problem, preconditions/postconditions/invariants/history constraint
- ISP: no client should depend on methods it doesn't use — role interfaces over fat interfaces
- DIP: depend on abstractions; DIP vs DI vs IoC distinction; constructor injection preferred
- How SOLID principles interconnect and reinforce each other
- SOLID in functional programming and microservices
- Modern criticisms: excessive abstraction, KISS/YAGNI balance, language features reducing pattern need
