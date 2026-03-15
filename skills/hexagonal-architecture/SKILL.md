---
name: hexagonal-architecture
description: Enforces Hexagonal Architecture (Ports and Adapters) principles including driving and driven ports, adapter separation, and technology-agnostic core design. Use when structuring application boundaries, defining port interfaces, implementing adapters for databases or external APIs, testing business logic in isolation, or comparing hexagonal with onion and clean architecture approaches.
---

# Hexagonal Architecture (Ports and Adapters)

> **Status:** Draft — book list for review. Content to be added in second round.

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Hexagonal Architecture Explained* | Alistair Cockburn, Juan Manuel Garrido de Paz | Addison-Wesley | 2024 |
| *Get Your Hands Dirty on Clean Architecture* (2nd ed.) | Tom Hombergs | Packt | 2023 |
| *Fundamentals of Software Architecture* | Mark Richards, Neal Ford | O'Reilly | 2020 |
| *Software Architecture: The Hard Parts* | Ford, Richards, Sadalage, Dehghani | O'Reilly | 2021 |

### Online References

- Alistair Cockburn's original article: alistair.cockburn.us/hexagonal-architecture
- Netflix Tech Blog: "Ready for Changes with Hexagonal Architecture" (2020)
- AWS Prescriptive Guidance: "Building Hexagonal Architectures on AWS" (2023)

## Topics to Cover

- Cockburn's original concept: breaking away from layered stack diagrams
- Driving (primary) ports and driven (secondary) ports — naming conventions
- Primary (driving) adapters: REST controllers, CLI handlers, test harnesses
- Secondary (driven) adapters: SQL repositories, message queue clients, external API clients
- Critical insight: ports are NOT a layer — they're part of the hexagon
- The core never depends on adapters
- Testing advantages: test harness + mock database → production
- Deferring technology decisions to the "last reasonable moment"
- Relationship to Clean Architecture and Onion Architecture — same DNA, different prescriptiveness
