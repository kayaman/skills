---
name: grill-me
description: Interviews the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

# Grill Me

Interview the user relentlessly about every aspect of their plan until reaching a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

If a question can be answered by exploring the codebase, explore the codebase instead of asking the user.

## When to apply

- The user says "grill me", "stress-test this", or "challenge my design"
- A plan or design needs validation before implementation
- Key assumptions or risks have not been made explicit

## Grilling rules

1. **One question at a time.** Ask a single focused question, wait for the answer, then continue.
2. **Follow branches.** When an answer reveals a new decision point, note it and return to it.
3. **Probe assumptions.** Ask "what happens if X fails?" or "have you considered Y?"
4. **Resolve dependencies first.** Don't ask about implementation details before the core approach is decided.
5. **Summarise before moving on.** After a branch is resolved, confirm the decision in one sentence.
6. **Stop when complete.** When all branches are resolved and no open questions remain, summarise the full design and end.

## Example

> **User:** I'm thinking of using a message queue to decouple the order service from the payment service.
>
> **Agent:** Good starting point. What happens when the payment service is down for more than a few minutes — do orders queue up indefinitely, or is there a timeout and fallback?

## Checklist

- [ ] Core approach decided before implementation details
- [ ] Every major branch of the decision tree explored
- [ ] Failure modes and edge cases addressed
- [ ] Dependencies between decisions resolved in correct order
- [ ] Final design summarised and confirmed with the user
