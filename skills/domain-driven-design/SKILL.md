---
name: domain-driven-design
description: Enforces Domain-Driven Design strategic and tactical patterns including Bounded Contexts, Aggregates, Value Objects, Domain Events, and Context Mapping. Use when modeling a business domain, defining bounded context boundaries, designing aggregates, applying ubiquitous language, running Event Storming workshops, implementing CQRS or Event Sourcing, or reviewing domain models for DDD anti-patterns like Anemic Domain Models.
---

# Domain-Driven Design

> **Status:** Draft — book list for review. Content to be added in second round.

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Domain-Driven Design: Tackling Complexity in the Heart of Software* | Eric Evans | Addison-Wesley | 2003 |
| *Implementing Domain-Driven Design* | Vaughn Vernon | Addison-Wesley | 2013 |
| *Domain-Driven Design Distilled* | Vaughn Vernon | Addison-Wesley | 2016 |
| *Learning Domain-Driven Design* | Vlad Khononov | O'Reilly | 2021 |
| *Domain Modeling Made Functional* | Scott Wlaschin | Pragmatic Bookshelf | 2018 |
| *Patterns, Principles, and Practices of Domain-Driven Design* | Millett & Tune | Wrox | 2015 |
| *Balancing Coupling in Software Design* | Vlad Khononov | Addison-Wesley | 2024 |
| *Architecture for Flow* | Andrew Harmel-Law | O'Reilly | 2023 |
| *Introducing EventStorming* | Alberto Brandolini | Leanpub | ~2024 |

## Topics to Cover

- Core philosophy: business domain at the center of software development
- Strategic patterns: Ubiquitous Language, Bounded Contexts, Context Mapping (Partnership, Shared Kernel, Customer-Supplier, Conformist, ACL, Open Host Service, Published Language, Separate Ways)
- Subdomains: Core, Supporting, Generic
- Tactical patterns: Entities, Value Objects, Aggregates, Aggregate Roots, Repositories, Domain Events, Domain Services, Application Services, Factories
- Aggregate design rules (Vaughn Vernon): small aggregates, reference by identity, eventual consistency across boundaries
- Event Storming: Big Picture, Process Modeling, Software Design
- CQRS and Event Sourcing: when to apply, projections, snapshots
- Common pitfalls: DDD on simple CRUD, oversized aggregates, ignoring ubiquitous language, Anemic Domain Model
