---
name: clean-code
description: Enforces clean code principles including meaningful naming, small focused functions, command-query separation, error handling with exceptions, and Kent Beck's four rules of simple design. Use when writing new code, refactoring existing code, reviewing pull requests for readability and maintainability, applying the Boy Scout Rule, or evaluating functions for single responsibility and appropriate abstraction level.
---

# Clean Code

Reference: *Clean Code* (Martin), *Tidy First?* (Beck), *A Philosophy of Software Design* (Ousterhout), *Refactoring* (Fowler)

## When to Apply

- Writing new functions, classes, or modules
- Refactoring existing code for readability and maintainability
- Reviewing pull requests for naming, structure, and clarity
- Deciding whether to add a comment or improve the code instead
- Handling errors and edge cases in application code
- Evaluating whether code complexity is justified

---

## Naming

*"If a name requires a comment, it does not reveal its intent."*

### Rules

- MUST use intention-revealing names — the name tells WHY it exists, WHAT it does, HOW it's used
- MUST use pronounceable, searchable names — avoid abbreviations and single-letter variables (except loop counters)
- MUST use nouns for classes (`Order`, `ShippingPolicy`) and verbs for methods (`calculateTotal`, `validateAddress`)
- MUST pick one word per concept and use it consistently: don't mix `fetch`, `retrieve`, `get` for the same operation
- MUST NOT use Hungarian notation, type prefixes, or member prefixes (`strName`, `m_count`)
- SHOULD use domain vocabulary — names from the problem domain or solution domain, never invented jargon

| Bad | Good | Why |
|-----|------|-----|
| `d` | `elapsedTimeInDays` | Intention-revealing |
| `genymdhms` | `generationTimestamp` | Pronounceable |
| `accountList` | `accounts` | Don't encode the container type |
| `Manager`, `Processor`, `Handler` | Specific name for the actual responsibility | Avoid meaningless suffixes |

---

## Functions

### Rules

- MUST do one thing — if a function does more than one thing, extract the other things
- MUST operate at one level of abstraction — don't mix high-level orchestration with low-level details
- SHOULD follow the **Stepdown Rule**: read like a top-down narrative, each function introducing the next level of detail
- SHOULD have as few arguments as possible — zero (niladic) is ideal; three or more requires justification
- MUST NOT use boolean flag arguments — they signal the function does two things; split into two functions
- SHOULD be small enough to fit in your working memory — but prioritize clarity over arbitrary line counts

### Command-Query Separation (CQS)

Functions MUST either **do something** (command — changes state, returns void) or **answer something** (query — returns a value, no side effects). Never both.

```
# BAD — command and query mixed
def set_and_get_previous(value):
    previous = self.value
    self.value = value
    return previous

# GOOD — separated
def get_value(self):          # query
    return self.value

def set_value(self, value):   # command
    self.value = value
```

---

## Comments

*"Don't comment bad code — rewrite it."* (Kernighan & Plaugher)

### Acceptable Comments

| Type | Example | Why |
|------|---------|-----|
| Legal headers | `// Copyright 2024 Acme Corp` | Required by policy |
| Explanation of intent | `// Use binary search because list is always sorted by insertion order` | The code shows WHAT; the comment explains WHY |
| Warning of consequences | `// This test takes 30 minutes to run` | Prevents accidental execution |
| TODO markers | `// TODO(#1234): Replace with batch API when available` | Tracks known improvement with issue reference |
| API documentation | Javadoc/JSDoc for public APIs | Contract documentation for consumers |

### Comments That MUST Be Avoided

- **Redundant comments** that restate the code: `i++; // increment i`
- **Misleading comments** that describe what the code SHOULD do but doesn't
- **Commented-out code** — version control preserves history; delete dead code
- **Journal comments** — git log tracks changes; don't maintain a changelog in code
- **Closing brace comments** — if you need them, your function is too long

---

## Objects vs Data Structures

Objects and data structures are **diametrically opposed** (Martin). Choose deliberately.

| | Objects | Data Structures |
|--|---------|----------------|
| **Expose** | Behavior (methods) | Data (fields) |
| **Hide** | Data (private state) | Nothing |
| **Easy to add** | New types (add new class) | New functions (add function operating on all types) |
| **Hard to add** | New behavior (must change all types) | New types (must change all functions) |

- MUST NOT create **hybrids** — half object, half data structure — that have the worst of both worlds
- SHOULD use objects when new types are more likely than new operations
- SHOULD use data structures when new operations are more likely than new types
- MUST respect the **Law of Demeter** — no train wrecks: `a.getB().getC().doSomething()`

---

## Error Handling

### Rules

- MUST use exceptions instead of error return codes — exceptions separate the happy path from error handling
- MUST write `try-catch-finally` first when the function involves operations that can fail
- SHOULD use unchecked exceptions — checked exceptions violate OCP (every catch clause in the call chain must be updated)
- MUST NOT return `null` — use Null Object pattern, Optional/Maybe, or throw an exception
- MUST NOT pass `null` as a function argument — there's no reasonable expectation for handling it
- SHOULD create exception classes organized by how callers HANDLE them, not by their source

```
# BAD — checking null return
user = repository.find_by_id(id)
if user is not None:
    # do something

# GOOD — exception or Optional
user = repository.find_by_id(id)  # raises NotFoundError
# or
user = repository.find_by_id(id)  # returns Optional<User>
user.if_present(lambda u: process(u))
```

---

## Unit Tests

### TDD Three Laws

1. Write a failing test before writing any production code
2. Write only enough of a test to demonstrate a failure
3. Write only enough production code to make the failing test pass

### F.I.R.S.T. Principles

| Principle | Rule |
|-----------|------|
| **Fast** | Tests MUST run quickly — slow tests don't get run |
| **Independent** | Tests MUST NOT depend on each other or on execution order |
| **Repeatable** | Tests MUST produce the same result in any environment |
| **Self-Validating** | Tests MUST have a boolean output (pass/fail) — no manual log inspection |
| **Timely** | Tests SHOULD be written just before the production code (TDD) |

- MUST test one concept per test — multiple assertions are fine if they all verify the same concept
- MUST NOT test private methods directly — test through the public interface

---

## Kent Beck's Four Rules of Simple Design

In priority order:

1. **Passes all the tests** — a system that can't be verified MUST NOT be deployed
2. **Reveals intention** — good names, small functions, standard patterns make the code self-documenting
3. **No duplication** — every piece of knowledge has a single, authoritative representation
4. **Fewest elements** — minimize classes and methods; counterbalance against over-decomposition

Rules 2–4 are applied during refactoring under the safety net of rule 1.

---

## Successive Refinement

*"To write clean code, you must first write dirty code and then clean it."*

- SHOULD write a working solution first, then refactor incrementally
- MUST have tests in place before refactoring — TDD provides the safety net
- SHOULD apply the **Boy Scout Rule**: leave the code cleaner than you found it — small improvements compound over time
- SHOULD prefer **tidying** (small, safe structural improvements) as a separate step from feature work (Beck, *Tidy First?*)

---

## Balancing Clean Code with Pragmatism

### What Holds Up (2024 consensus)

Naming principles, SRP for functions, CQS, F.I.R.S.T. test principles, error handling with exceptions, the Boy Scout Rule, objects vs data structures distinction.

### What Is Debated

- **Extreme function size** ("2–4 lines") can produce unreadable names and excessive indirection — prioritize clarity over arbitrary limits
- **Performance in hot paths** — Muratori demonstrated that Clean Code structural rules can produce 10–25x slower code in performance-critical scenarios; optimize hot paths pragmatically
- **Deep modules** (Ousterhout) — sometimes a larger function with a simple interface is better than many tiny functions that fragment the logic

- SHOULD apply clean code principles as **guidelines** balanced by context, not as rigid dogma
- SHOULD NOT fragment a clear 20-line function into five 4-line functions if it reduces readability

---

## Checklist

When writing or reviewing code, verify:

- [ ] Names are intention-revealing, pronounceable, and consistent across the codebase
- [ ] Functions do one thing at one level of abstraction
- [ ] CQS is respected — functions either change state OR return a value, not both
- [ ] No commented-out code, redundant comments, or journal entries
- [ ] Comments explain WHY (intent), not WHAT (code restates itself)
- [ ] Error handling uses exceptions, not return codes; no null returns or null parameters
- [ ] Tests follow F.I.R.S.T. principles and cover one concept each
- [ ] No hybrids — objects hide data and expose behavior, or data structures expose data
- [ ] Law of Demeter is respected — no train wreck method chains
- [ ] Code has been tidied after getting it working — Boy Scout Rule applied

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
