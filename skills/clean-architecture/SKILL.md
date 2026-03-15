---
name: clean-architecture
description: Enforces Clean Architecture principles including the dependency rule, layer separation, and component design. Use when structuring application layers, defining boundaries between domain and infrastructure, reviewing code for dependency rule violations, applying Screaming Architecture, or evaluating component cohesion and coupling (REP, CCP, CRP, ADP, SDP, SAP).
---

# Clean Architecture

> **Status:** Draft — book list for review. Content to be added in second round.

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Clean Architecture* | Robert C. Martin | Pearson | 2017 |
| *Get Your Hands Dirty on Clean Architecture* (2nd ed.) | Tom Hombergs | Packt | 2023 |
| *Fundamentals of Software Architecture* | Mark Richards, Neal Ford | O'Reilly | 2020 |
| *Software Architecture: The Hard Parts* | Ford, Richards, Sadalage, Dehghani | O'Reilly | 2021 |
| *Software Architecture in Practice* (4th ed.) | Bass, Clements, Kazman | Addison-Wesley | 2024 |
| *A Philosophy of Software Design* (2nd ed.) | John Ousterhout | Stanford | 2021 |

## Topics to Cover

- The dependency rule: source code dependencies can only point inward
- Four canonical layers: Entities, Use Cases, Interface Adapters, Frameworks & Drivers
- Data crossing boundaries: DTOs, simple structures — never entities or DB rows
- Screaming Architecture: top-level directories express use cases, not frameworks
- Humble Object Pattern: testable logic vs hard-to-test infrastructure
- Component cohesion principles: REP, CCP, CRP
- Component coupling principles: ADP, SDP, SAP
- Common pitfalls: over-layering for CRUD, use cases as repository proxies, mapping everything between layers
