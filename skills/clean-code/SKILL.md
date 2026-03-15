---
name: clean-code
description: Enforces clean code principles including meaningful naming, small focused functions, command-query separation, error handling with exceptions, and Kent Beck's four rules of simple design. Use when writing new code, refactoring existing code, reviewing pull requests for readability and maintainability, applying the Boy Scout Rule, or evaluating functions for single responsibility and appropriate abstraction level.
---

# Clean Code

> **Status:** Draft — book list for review. Content to be added in second round.

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Clean Code* | Robert C. Martin | Pearson | 2008 |
| *Refactoring* (2nd ed.) | Martin Fowler | Addison-Wesley | 2018 |
| *A Philosophy of Software Design* (2nd ed.) | John Ousterhout | Stanford | 2021 |
| *Tidy First?* | Kent Beck | O'Reilly | 2023 |
| *Code That Fits in Your Head* | Mark Seemann | Addison-Wesley | 2021 |
| *Five Lines of Code* | Christian Clausen | Manning | 2021 |
| *The Pragmatic Programmer* (2nd ed.) | Hunt & Thomas | Addison-Wesley | 2020 |
| *Implementation Patterns* | Kent Beck | Addison-Wesley | 2007 |

## Topics to Cover

- Meaningful names: intention-revealing, pronounceable, searchable, consistent
- Functions: small, single responsibility, one level of abstraction, Stepdown Rule
- Command-Query Separation: functions do something OR answer something, never both
- Comments: when good (intent, warnings, TODOs), when bad (redundant, misleading, commented-out code)
- Objects vs data structures: opposing forces, avoid hybrids
- Error handling: exceptions over return codes, don't return null, don't pass null
- Unit tests: TDD three laws, F.I.R.S.T. principles
- Kent Beck's 4 rules of simple design: passes tests → no duplication → expresses intent → minimizes elements
- Successive refinement: write dirty code first, then clean it
- The Boy Scout Rule: leave code cleaner than you found it
- Modern criticisms: performance concerns, extreme function size advice, deep modules alternative
