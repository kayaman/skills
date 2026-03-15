---
name: yagni-principle
description: Enforces the YAGNI (You Aren't Gonna Need It) principle to prevent speculative complexity while maintaining code quality. Use when evaluating whether to build a feature preemptively, deciding between extensibility and simplicity, reviewing code for over-engineering, resolving the YAGNI-SOLID tension, or assessing whether supporting practices (tests, CI, refactoring) are in place to apply YAGNI safely.
---

# YAGNI Principle

> **Status:** Draft — book list for review. Content to be added in second round.

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Extreme Programming Explained* (2nd ed.) | Kent Beck | Addison-Wesley | 2004 |
| *Tidy First?* | Kent Beck | O'Reilly | 2023 |
| *Software Engineering at Google* | Winters, Manshreck, Wright | O'Reilly | 2020 |
| *The Pragmatic Programmer* (2nd ed.) | Hunt & Thomas | Addison-Wesley | 2020 |
| *Refactoring* (2nd ed.) | Martin Fowler | Addison-Wesley | 2018 |

### Online References

- Martin Fowler, "Yagni" (bliki, 2015)
- Ron Jeffries, "YAGNI, yes. Skimping, no. Technical Debt? Not even."

## Topics to Cover

- Origin in Extreme Programming (Beck, Hendrickson, Chrysler C3 project)
- Critical caveat: YAGNI requires supporting practices — refactoring, testing, CI
- Fowler's four costs of unnecessary complexity: build, delay, carry, repair
- Only ~1/3 of features actually improve target metrics (Kohavi et al., Microsoft)
- The YAGNI-SOLID tension and Fowler's resolution: structure is not speculation
- "Open for extension" (good) vs "already extended" (YAGNI violation)
- Fowler's practical test: imagine the refactoring you'd have to do later
- Common pitfalls: using YAGNI as excuse for poor design, ignoring confirmed requirements, confusing "don't build" with "don't think ahead"
