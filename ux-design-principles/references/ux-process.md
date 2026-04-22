# UX Process Methods

Reference: *The User Experience Team of One* by Leah Buley & Joe Natoli (Rosenfeld Media)

Lightweight UX methods adapted for agents and teams with limited UX resources.

---

## 1. Proto-Personas

Lightweight alternative to full persona research. Create when making design decisions without access to user research.

**Template:**

```
Name:           [Descriptive name, e.g., "Busy Manager Maria"]
Role/Context:   [Job title, environment, device usage]
Goals:          - [Primary goal]
                - [Secondary goal]
                - [Tertiary goal]
Frustrations:   - [Main pain point]
                - [Secondary pain point]
                - [Constraint or limitation]
Tech Comfort:   [Novice / Intermediate / Power user]
```

**How to use:**
- Create 2-3 proto-personas for any interface: the primary user and at least one edge-case user (novice, accessibility needs, or impatient power user)
- Before building a component, check: does this serve both the novice (clear labels, guided flow) AND the expert (keyboard shortcuts, bulk actions)?
- Proto-personas are hypotheses, not facts. Update them when real user feedback arrives.

---

## 2. Fresh Eyes Heuristic Walk

A 7-step self-review procedure for agents. Simulates what a usability tester would catch.

**Run this against every page or view before delivering code:**

### Step 1: Trunk Test
Clear your context. Approach the page as if from a search engine. Can you identify: What site? What page? Major sections? Your options? Where you are?

### Step 2: Primary Task
Identify the primary task on this page. Can it be completed in <=3 clicks/taps? Is the path obvious without reading instructions?

### Step 3: Scanning Check
Squint at the page. Does the visual hierarchy guide the eye to the right place? Can you identify the primary action within 2 seconds?

### Step 4: Label Audit
For each interactive element: is its purpose obvious without reading surrounding text? Would you need to reword any label for clarity?

### Step 5: Content Trim
For each piece of text in chrome (not user content): would removing it break anything? If not, remove it.

### Step 6: Error States
Does every possible error say what went wrong AND how to fix it? Are error messages specific to the field, not generic banners?

### Step 7: Empty States
Does every empty state (no data, no results, first-time use) tell the user what to do next with a clear CTA?

---

## 3. Nielsen's 10 Heuristics

Mapped to code-level checks. Use during reviews.

### H1: Visibility of System Status
Keep users informed about what's happening through timely feedback.
- Loading indicators for operations >400ms
- Progress bars for multi-step processes
- "Saving...", "Saved" state indicators
- Active/selected states on interactive elements

### H2: Match Between System and Real World
Use language and concepts familiar to users, not system internals.
- Labels use domain language, not technical jargon
- Error codes are never shown to end users without translation
- Dates/numbers follow user's locale conventions

### H3: User Control and Freedom
Users need a clear emergency exit. Support undo and redo.
- Every action has a cancel/back/undo path
- Modals have close buttons and respond to Escape
- Multi-step flows allow going back to previous steps
- Destructive actions are recoverable (soft delete, undo toast)

### H4: Consistency and Standards
Same actions should have same appearance and position throughout.
- Button styles consistent: primary, secondary, destructive used uniformly
- Icon meanings don't change between pages
- Terminology is consistent (don't mix "delete/remove/trash")

### H5: Error Prevention
Prevent errors before they happen. Better than good error messages.
- Disable invalid actions rather than allowing then showing error
- Confirm destructive actions with specific details
- Validate inline as user types (not only on submit)
- Use constrained inputs (date picker vs. text field)

### H6: Recognition Rather Than Recall
Show options instead of requiring users to remember information.
- Recent items, suggestions, autocomplete
- Don't ask users to re-enter information from a previous step
- Use visual cues (icons, thumbnails) alongside text

### H7: Flexibility and Efficiency of Use
Accelerators for experts that don't burden novices.
- Keyboard shortcuts for common actions
- Bulk operations for power users
- Sensible defaults that work for most cases
- Search/filter alongside browsable categories

### H8: Aesthetic and Minimalist Design
Every extra element competes with relevant elements and reduces their visibility.
- Remove decorative elements that don't aid comprehension
- Reduce visual noise: fewer borders, fewer colors, more whitespace
- Each screen element should earn its place

### H9: Help Users Recover from Errors
Error messages in plain language, indicate the problem precisely, suggest a fix.
- "Email address is invalid" not "Error 422"
- Show the error next to the field that caused it
- Offer a direct action to fix: "Try again", "Use a different email"

### H10: Help and Documentation
If needed, help should be searchable, task-oriented, and concise.
- Contextual help (tooltips, inline hints) preferred over separate docs
- Help text appears near the relevant control
- FAQ or help section is searchable, not just a long page

---

## 4. Lightweight Research Methods

### Competitive Analysis
Screenshot 3-5 competitor UIs. Note common patterns — these are user expectations (Jakob's Law). Deviate only when you can articulate why.

### Card Sorting (Mental Model)
When designing navigation: list all pages/features and group by user task, not by internal system architecture. Users think in tasks ("find a product", "track my order"), not in departments ("Marketing", "Operations").

### Five-Second Test
Show the page for 5 seconds, then ask: "What was the page about?" and "What would you do first?" If answers are wrong, the hierarchy needs work.

---

## 5. Documenting UX Decisions

Link principle to decision in code comments when the choice isn't obvious:

```
/* Hick's Law: reduced from 12 to 5 top-level nav items, grouped rest under "More" */
/* Jakob's Law: kept checkout flow as single-page to match e-commerce conventions */
/* Tesler's Law: auto-detecting timezone from browser rather than asking user */
```

Keep UX rationale in commit messages when the change is user-facing:

```
feat(nav): consolidate navigation to 5 top-level items

Applied Hick's Law — reduced decision time by grouping secondary items
under "More" dropdown. Analytics showed 95% of traffic hits top 5 items.
```
