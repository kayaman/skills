---
name: dry-principle
description: Enforces the DRY (Don't Repeat Yourself) principle correctly, distinguishing true knowledge duplication from incidental code similarity. Use when evaluating whether to extract shared code, deciding if duplication is acceptable, applying the Rule of Three, avoiding premature abstraction, or reviewing code for the wrong abstraction anti-pattern.
---

# DRY Principle

Reference: *The Pragmatic Programmer* (Hunt & Thomas), *Tidy First?* (Beck), *Software Engineering at Google* (Winters et al.)

## When to Apply

- Evaluating whether two similar code blocks should be extracted into a shared abstraction
- Reviewing code for duplicated business rules, logic, or knowledge
- Deciding whether an existing abstraction is the right one or should be reverted to duplication
- Refactoring a codebase with repeated logic that has begun to diverge
- Assessing whether a shared library or utility is worth the coupling cost

---

## What DRY Actually Means

The formal definition from Hunt & Thomas (1999): *"Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."*

DRY is about **knowledge duplication**, not code duplication. Two identical-looking code blocks that represent different business concepts are NOT a DRY violation. Two different-looking code blocks that encode the same business rule ARE a violation.

### The Acid Test

> *"If this business rule changes, would ALL of these locations need to change in exactly the same way?"*

- If **yes** → true DRY violation — extract a single authoritative representation
- If **no** → incidental similarity — leave them separate; they will likely diverge

---

## Five Types of Duplication

| Type | Description | Example | Fix |
|------|-------------|---------|-----|
| **Code** | Copy-pasted blocks | Same validation logic in two controllers | Extract shared function |
| **Knowledge / Logic** | Same business rule in multiple places | Tax calculation in order service AND invoice service | Single authoritative implementation |
| **Documentation** | Comments restating what code does | `x = x + 1  // increment x` | Delete the comment; the code is clear |
| **Data** | Derived values stored independently | Storing `total` separately from `items` | Derive on read, or use a single source of truth |
| **Representation** | Same concept across system boundaries | `User` defined separately in frontend and backend | Shared schema (Protobuf, OpenAPI, JSON Schema) |

- MUST eliminate knowledge/logic duplication — this is the most dangerous form
- SHOULD eliminate code duplication only after confirming it represents the same knowledge
- SHOULD use shared schemas or code generation to reduce representation duplication across boundaries

---

## When DRY Becomes Harmful

### The Wrong Abstraction (Metz)

*"Duplication is far cheaper than the wrong abstraction."*

**The pattern that leads to the wrong abstraction:**

1. Developer sees duplication and extracts it into a shared abstraction
2. New requirement is *almost* the same — add a parameter and conditional
3. Repeat step 2 several times
4. The abstraction becomes an incomprehensible tangle of conditionals
5. Sunk cost fallacy prevents reverting: *"We already built this; let's just add one more parameter"*

**The remedy:** The fastest way forward is back. Re-introduce duplication, then re-abstract based on the *actual* patterns that emerge.

### Coupling Cost

Every extraction creates a dependency. Extracting a shared utility between two services couples them — changes to the utility require coordinating both services.

- MUST weigh the coupling cost of extraction against the maintenance cost of duplication
- Duplication between independently deployed services is often the right choice
- SHOULD prefer duplication over coupling across team or service boundaries (Winters et al., *Software Engineering at Google*)

---

## Rule of Three

Don Roberts, popularized by Fowler: *"The first time you do something, just do it. The second time, wince at the duplication but do it anyway. The third time, refactor."*

With only two examples, you cannot reliably identify the true pattern. By three, the commonalities become visible and the abstraction has a solid foundation.

### Rules

- MUST NOT extract a shared abstraction on the first occurrence
- SHOULD tolerate duplication on the second occurrence, noting it for future refactoring
- SHOULD extract on the third occurrence, when the true pattern is clear
- MUST verify that all three instances represent the same knowledge before extracting

---

## AHA Programming

**"Avoid Hasty Abstractions"** — coined by Kent C. Dodds (2020): *"I'm fine with code duplication until you feel pretty confident that you know the use cases. At that point, the commonalities will 'scream at you for abstraction.'"*

AHA is the synthesis of DRY and WET ("Write Everything Twice"):

| Approach | Rule | Risk |
|----------|------|------|
| **DRY** | Never repeat yourself | Premature abstraction; wrong abstraction |
| **WET** | Write everything twice before extracting | Arbitrary threshold; ignores knowledge duplication |
| **AHA** | Abstract when the pattern screams for it | Requires judgment; no fixed threshold |

- SHOULD optimize for change first — future requirements are unknown
- SHOULD abstract when you are confident about the use cases, not before
- SHOULD NOT set a fixed numeric threshold — the right moment depends on how well you understand the pattern

---

## Decision Framework

When you encounter similar code, follow this sequence:

1. **Is it the same knowledge?** Apply the acid test. If different business rules happen to look similar, stop — leave them separate.

2. **How many occurrences?** If fewer than three, tolerate the duplication. Note it with a comment if helpful.

3. **What's the coupling cost?** If extraction creates a dependency across service, team, or deployment boundaries, prefer duplication.

4. **Is the abstraction clear?** If you can name the extracted concept and it represents a single, stable piece of knowledge, extract it. If the name is vague (`CommonUtils.processData`) or requires parameters to handle divergent cases, the abstraction is wrong.

5. **Can you undo it?** If the extraction turns out to be wrong, you must be willing to re-inline. Sunk cost is not a reason to keep a bad abstraction.

---

## Common Pitfalls

| Pitfall | Signal | Remedy |
|---------|--------|--------|
| **Premature extraction** | Shared function has boolean flags or parameters that select between behaviors | Re-inline; the two uses represent different knowledge |
| **Utility dumping ground** | `Utils` class grows to hundreds of methods | Break by domain concept; many "utilities" belong on domain objects |
| **Cross-boundary coupling** | Shared library forces coordinated deployments | Duplicate within each boundary; sync schema separately |
| **Sunk cost preservation** | "We already built this abstraction, let's keep extending it" | Re-introduce duplication; re-abstract from scratch |
| **DRY on tests** | Extracting test setup until tests are unreadable | Tests SHOULD be readable in isolation; duplication in tests is often acceptable |
| **Documentation DRY** | Code and comments say the same thing | Delete the comment; trust the code |

---

## Checklist

When evaluating duplication, verify:

- [ ] The acid test confirms this is knowledge duplication, not incidental code similarity
- [ ] Three or more occurrences exist (Rule of Three) — or the pattern is unmistakably clear
- [ ] The extracted abstraction has a clear, specific name representing one concept
- [ ] No boolean flags or type-switching parameters are needed to handle different use cases
- [ ] The coupling cost of extraction does not exceed the maintenance cost of duplication
- [ ] Cross-boundary duplication is preferred over cross-boundary coupling
- [ ] Existing wrong abstractions have been identified and considered for re-inlining
- [ ] Tests remain readable — test duplication is acceptable for clarity

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
