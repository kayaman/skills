---
name: dry-principle
description: Enforces the DRY (Don't Repeat Yourself) principle correctly, distinguishing true knowledge duplication from incidental code similarity. Use when evaluating whether to extract shared code, deciding if duplication is acceptable, applying the Rule of Three, avoiding premature abstraction, or reviewing code for the wrong abstraction anti-pattern.
---

# DRY Principle

> **Status:** Draft — book list for review. Content to be added in second round.

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *The Pragmatic Programmer* (2nd ed.) | Hunt & Thomas | Addison-Wesley | 2020 |
| *Tidy First?* | Kent Beck | O'Reilly | 2023 |
| *A Philosophy of Software Design* (2nd ed.) | John Ousterhout | Stanford | 2021 |
| *Software Engineering at Google* | Winters, Manshreck, Wright | O'Reilly | 2020 |
| *Refactoring* (2nd ed.) | Martin Fowler | Addison-Wesley | 2018 |
| *Five Lines of Code* | Christian Clausen | Manning | 2021 |

### Online References

- Sandi Metz, "The Wrong Abstraction" (blog post, 2016)
- Kent C. Dodds, "AHA Programming" (blog post, 2020)

## Topics to Cover

- What DRY actually means: knowledge duplication, not code duplication
- Five types of duplication: code, knowledge/logic, documentation, data, representation
- The acid test: "If this business rule changes, would ALL these locations need to change the same way?"
- Incidental duplication vs true DRY violation
- When DRY becomes harmful: the wrong abstraction, sunk cost fallacy
- Sandi Metz's insight: "duplication is far cheaper than the wrong abstraction"
- Rule of Three (Don Roberts): first do it, second wince but duplicate, third refactor
- AHA Programming (Kent C. Dodds): Avoid Hasty Abstractions
- When to re-introduce duplication and re-abstract correctly
