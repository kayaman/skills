---
name: yagni-principle
description: Enforces the YAGNI (You Aren't Gonna Need It) principle to prevent speculative complexity while maintaining code quality. Use when evaluating whether to build a feature preemptively, deciding between extensibility and simplicity, reviewing code for over-engineering, resolving the YAGNI-SOLID tension, or assessing whether supporting practices (tests, CI, refactoring) are in place to apply YAGNI safely.
---

# YAGNI Principle

Reference: *Extreme Programming Explained* (Beck), *Tidy First?* (Beck), *Software Engineering at Google* (Winters et al.)

## When to Apply

- Evaluating whether to build functionality that is not yet needed
- Reviewing code for speculative abstractions, unused extension points, or premature generalization
- Deciding between building flexibility now vs adding it when needed
- Resolving tension between YAGNI simplicity and SOLID extensibility
- Assessing whether the codebase has the supporting practices to apply YAGNI safely

---

## Core Principle

*"Always implement things when you actually need them, never when you just foresee that you need them."* — Ron Jeffries

YAGNI originated from Extreme Programming in the late 1990s. Kent Beck and Chet Hendrickson, working on the Chrysler C3 project, found that every proposed future capability turned out to be unnecessary — hence, *"You Aren't Gonna Need It."*

**Critical caveat:** YAGNI requires supporting practices — continuous refactoring, automated testing, and CI. Without these, YAGNI leads to disorganized code. YAGNI means "don't build it yet," not "don't build it well."

---

## The Four Costs of Unnecessary Complexity

Martin Fowler's analysis of what you pay when you build speculatively:

| Cost | Description | Impact |
|------|-------------|--------|
| **Cost of Build** | Time and effort spent on features that turn out unnecessary | Wasted development time |
| **Cost of Delay** | Needed features are delayed while building speculative ones | **Often the largest cost** — opportunity cost of not shipping real value |
| **Cost of Carry** | Added complexity makes ALL other features harder to build, test, and understand | Compounds over time; slows the entire team |
| **Cost of Repair** | Even if eventually needed, understanding evolves; code from months ago may need reworking | The speculative code rarely matches the actual need |

Studies show only about **one-third of features** actually improve the metrics they target (Kohavi et al., Microsoft analysis of thousands of A/B tests).

---

## What YAGNI Applies To

### YAGNI Violations (Do NOT Build)

- Features no user has requested based on "what if they want..."
- Abstract factories, plugin systems, or strategy patterns with only one implementation
- Configuration options for hypothetical future flexibility
- Database columns for anticipated but unconfirmed requirements
- API endpoints for features that don't exist yet
- Generic frameworks extracted from a single use case

### NOT YAGNI Violations (These Are Good Practice)

- Clean code structure (SRP, meaningful names, small functions)
- Automated tests for existing functionality
- Proper error handling for current operations
- Security measures for current features
- Documentation of current behavior
- Refactoring existing code for clarity

**Fowler's key distinction:** *"YAGNI only applies to capabilities built into the software to support a presumptive feature. It does not apply to effort to make the software easier to modify."*

---

## The YAGNI-SOLID Tension

The apparent conflict: YAGNI says don't build what you don't need; SOLID/OCP says make things extensible.

### Fowler's Resolution

| Concept | What It Means | YAGNI? |
|---------|--------------|--------|
| **"Open for extension"** | Good structure that MAKES future changes easy (clean interfaces, SRP, DIP) | NOT a violation — this is good design |
| **"Already extended"** | Speculative extension points, abstract factories with one impl, unused plugin systems | YAGNI violation — premature complexity |

Being easy to extend is a property of well-structured code. Being already extended is speculative engineering.

### Fowler's Practical Test

> *"Imagine the refactoring you'd have to do later to add this feature. Is it significantly more expensive to add later than now?"*

- If refactoring later is cheap → don't build it now
- If refactoring later is genuinely expensive (e.g., database schema migration affecting millions of rows) → consider building it now
- In most cases, the refactoring is cheaper than you think

---

## Decision Framework

When tempted to build something preemptively:

1. **Is there a confirmed, current need?** If yes, build it. YAGNI doesn't apply to known requirements.

2. **Is it structural quality or speculative capability?** Clean code, tests, and good naming are NOT YAGNI violations. Only speculative features and extension points are.

3. **Apply the refactoring thought experiment.** How expensive would it be to add this later when you actually need it? If the answer is "not much more expensive," wait.

4. **Check for supporting practices.** YAGNI is safe only with automated tests, CI, and a culture of continuous refactoring. Without these, you need more upfront design.

5. **Are you building a framework from a single use case?** If so, stop. You need at least three concrete use cases to know the right abstraction.

---

## Common Pitfalls

| Pitfall | Signal | Remedy |
|---------|--------|--------|
| **Speculative generality** | Abstract classes with one subclass; interfaces with one implementation; unused parameters | Remove the abstraction; add it when the second use case arrives |
| **Gold plating** | Feature has more options, configurations, or edge case handling than any user needs | Ship the minimal version; add complexity when users request it |
| **Resume-driven development** | Using complex patterns to learn or showcase skills, not to solve the problem | Ask: "Would the simplest team member understand this?" |
| **YAGNI as excuse for poor quality** | Skipping tests, error handling, or security "because YAGNI" | YAGNI applies to features, not to quality; quality is always needed |
| **Ignoring confirmed requirements** | Dismissing known requirements as "not needed yet" | YAGNI applies to speculative features, not to confirmed ones |
| **Confusing "don't build" with "don't think"** | Making no design decisions at all | Think ahead, but build only what's needed now |

---

## YAGNI at Scale

At Google scale (*Software Engineering at Google*), YAGNI manifests as:

- **Simple designs that evolve** — start with the simplest architecture; evolve as traffic and complexity grow
- **Incremental infrastructure** — build infrastructure for current scale, not predicted future scale
- **Feature flags over speculative features** — ship code behind flags; enable when ready
- **Monorepo simplicity** — avoid premature decomposition into microservices; a monolith is fine until proven otherwise

---

## Checklist

When reviewing code or proposals for YAGNI compliance, verify:

- [ ] Every feature addresses a confirmed, current need — not a speculative "might need"
- [ ] Abstractions (interfaces, factories, plugin systems) have at least two concrete implementations
- [ ] No configuration options exist for hypothetical flexibility
- [ ] Structural quality (clean code, tests, good names) is maintained — YAGNI doesn't excuse poor design
- [ ] The refactoring thought experiment shows it's not significantly more expensive to add later
- [ ] Supporting practices are in place: automated tests, CI, continuous refactoring
- [ ] The simplest solution that meets current requirements has been chosen

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
