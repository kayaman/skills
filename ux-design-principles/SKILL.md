---
name: ux-design-principles
description: >
  Apply UX psychology and usability principles when building user interfaces. Distills Laws of UX
  (Fitts's, Hick's, Jakob's, Miller's, Peak-End, Von Restorff, Tesler's, Doherty, Postel's,
  Aesthetic-Usability), Don't Make Me Think usability heuristics, and lightweight UX process
  methods into actionable code-level guidance. Use when building UI components, reviewing
  interfaces for usability, reducing cognitive load, designing navigation or forms, choosing
  interaction patterns, or auditing for dark patterns. Does NOT cover typography, color palettes,
  responsive CSS, or design tokens — see related skills.
license: MIT
metadata:
  author: kayaman
  version: "1.0.0"
  type: knowledge
  domain: ux-design
---

# UX Design Principles

Psychology-backed decision framework for agents building user interfaces.

Reference: *Laws of UX, 2nd Ed.* (Yablonski, O'Reilly), *Don't Make Me Think, Revisited* (Krug, New Riders), *The User Experience Team of One* (Buley, Rosenfeld Media)

These principles derive from human cognition, not trends. They apply regardless of framework, platform, or era.

## When to Use

- Building UI components (buttons, forms, navigation, modals, menus, lists)
- Reviewing existing interfaces for usability problems
- Choosing between interaction patterns (dropdown vs. radio, modal vs. inline)
- Designing navigation structure or information architecture
- Reducing cognitive load in complex interfaces
- Auditing for dark patterns or manipulative design
- Handling errors, empty states, and loading states

**Don't use for:** typography decisions (`ui-typography`, `web-typography`), color/palette generation (`frontend-design`), responsive CSS layout (`responsive-design`), design token creation (`frontend-design`).

---

## The Five UX Decisions

Apply these to every UI element you build:

| Decision | Governing Principle | Code Check |
|----------|-------------------|------------|
| How many options to show? | **Hick's Law**: decision time increases with choices | Count visible interactive elements; >7 ungrouped needs progressive disclosure |
| How big and close should targets be? | **Fitts's Law**: acquisition time = f(distance / size) | Interactive elements >= 44x44px; spacing between targets >= 8px; primary CTA largest |
| Will users understand without thinking? | **Krug's First Law**: don't make me think | Every label/button understandable without reading surrounding text; verb+noun format |
| How much can users hold at once? | **Miller's Law**: ~7 chunks in working memory | Ungrouped lists, nav items, form fields: chunk into groups of 3-5 |
| Does this match what users already know? | **Jakob's Law**: users transfer expectations | Compare pattern to platform/industry conventions; deviate only with strong justification |

---

## Quick Principle Index

**Laws of UX** — see [references/laws-of-ux.md](references/laws-of-ux.md):

- **Fitts's Law** — larger, closer targets are faster to reach
- **Hick's Law** — fewer choices = faster decisions
- **Jakob's Law** — match existing mental models and conventions
- **Miller's Law** — chunk information into groups of 3-7
- **Peak-End Rule** — users judge by the peak moment and the ending
- **Aesthetic-Usability Effect** — polished UI is perceived as more usable
- **Von Restorff Effect** — the visually different item is the one remembered
- **Tesler's Law** — absorb complexity in the system, not the user
- **Doherty Threshold** — respond within 400ms or show progress
- **Postel's Law** — accept liberal input, produce strict output

**Usability Heuristics** — see [references/usability-heuristics.md](references/usability-heuristics.md):

- **Self-evidence** — pages should be obvious, not require thought
- **Scanning over reading** — users scan in F-pattern; design for it
- **Satisficing** — users pick the first reasonable option, not the best
- **Omit needless words** — halve word count, then halve again
- **Navigation conventions** — persistent nav, "you are here", Trunk Test

**UX Process** — see [references/ux-process.md](references/ux-process.md):

- **Fresh Eyes Heuristic Walk** — 7-step agent self-review procedure
- **Proto-Personas** — lightweight user models for design decisions
- **Nielsen's 10 Heuristics** — mapped to code-level checks

---

## Component-Level Quick Reference

**Buttons and CTAs:**
- Primary action visually dominant (Von Restorff) and largest target (Fitts's)
- Max 1 primary + 1-2 secondary actions per view (Hick's)
- Labels: verb+noun — "Save Draft", "Delete Account", not "Submit" or "OK" (self-evidence)

**Forms:**
- Group related fields; max 5-7 per group (Miller's)
- Accept liberal input: phone, date, address in any format (Postel's)
- Inline validation within 400ms (Doherty); errors on the field, not in a banner
- Mark the worst errors first (Peak-End)

**Navigation:**
- Match industry conventions for position and structure (Jakob's)
- Max 7 top-level items; group beyond that (Miller's + Hick's)
- Persistent nav on every page with "you are here" indicator (Krug)

**Modals and Dialogs:**
- One decision per modal (Hick's)
- Destructive actions: specific label — "Delete 3 files", not "Are you sure?" (self-evidence)
- Close button top-right on desktop (Jakob's)

**Lists and Menus:**
- Highlight the important/different item (Von Restorff)
- Chunk into groups of 3-5 with visual separators (Miller's)
- Most-used items at top (satisficing)

**Loading and Feedback:**
- >400ms: loading indicator (Doherty)
- >1s: progress bar
- >10s: progress percentage or step count
- Non-destructive actions: consider optimistic UI

---

## Dark Pattern Avoidance

- MUST NOT use confirm-shaming ("No thanks, I don't want to save money")
- MUST NOT make unsubscribe/cancel harder than subscribe
- MUST NOT pre-check consent or opt-in boxes
- MUST NOT make the undesired choice more prominent (misdirection)
- MUST NOT create artificial urgency or false scarcity
- MUST NOT use roach-motel patterns (easy in, hard out)
- **Asymmetry test**: if the effort to undo exceeds the effort to do, it is likely a dark pattern

---

## References

Load these on demand for detailed guidance:

- [references/laws-of-ux.md](references/laws-of-ux.md) — Full treatment of all 10 laws with code checks and violation/fix examples
- [references/usability-heuristics.md](references/usability-heuristics.md) — Krug's principles with navigation rules and the Trunk Test
- [references/ux-process.md](references/ux-process.md) — Lightweight UX methods: guerrilla testing, proto-personas, heuristic walkthroughs
- [references/ux-review-checklist.md](references/ux-review-checklist.md) — 36-item checklist to run against any interface

## Related Skills

- `ui-typography` — character-level typographic correctness
- `web-typography` — typeface selection, pairing, hierarchy
- `frontend-design` — color palettes, design tokens, component templates, accessibility audits
- `responsive-design` — container queries, fluid typography, CSS Grid, breakpoints
