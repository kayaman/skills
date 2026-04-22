# Usability Heuristics

Reference: *Don't Make Me Think, Revisited* by Steve Krug (New Riders)

Krug's usability principles mapped to code-level checks for agents building interfaces.

---

## 1. Don't Make Me Think

The first law of usability: every page should be self-evident — obvious, self-explanatory, requiring zero cognitive effort to understand.

**Hierarchy:** Self-evident > Self-explanatory > Requires thought

**Code checks:**
- For every label, link, and button: would a user of average ability understand this without pausing?
- Test: read each label aloud. If you need "which means..." it fails.
- No clever wordplay in navigation or actions
- No ambiguous labels: "Submit" (submit what?), "Click here" (why?), "Go" (where?)

**Fix pattern:** verb+noun labels — "Add to Cart", "View Pricing", "Download Report", "Delete Account"

**Common violations:**
- "Solutions" (what solutions?), "Resources" (what kind?), "Get Started" (with what?)
- Icons without text labels (except universally understood: home, search, close, back)

---

## 2. Users Scan, They Don't Read

Users scan pages in an F-pattern: top horizontal, then partway across lower, then vertical along left edge. They read the first few words of lines and skip the rest.

**Design for scanning:**
- Clear visual hierarchy: headings > subheadings > body
- Short paragraphs (max 4 lines in UI content)
- Bulleted lists for any list of 3+ items
- Bold key phrases within paragraphs
- First word of every heading, link, and list item must be the most informative word

**Code checks:**
- Are headings descriptive? "Shipping Options" not "Section 3"
- Is important content in the first 2 words of each line?
- Are there walls of text without visual breaks? Break them.
- Do CTAs stand out visually from surrounding content?

**Violation:** Paragraph of instructions above a form explaining how to fill it out.
**Fix:** If the form needs instructions, the form design has failed. Redesign the form.

---

## 3. Satisficing

Users don't choose the best option — they choose the first reasonable one. They don't optimize; they satisfice (satisfy + suffice).

**Implications:**
- The correct/desired action must appear first or most prominently
- Don't rely on users comparing all options
- Default selections should be the most common choice

**Code checks:**
- Is the primary CTA the first prominent interactive element?
- In search results, is the most relevant result first?
- In error messages, is the fix action more prominent than "dismiss"?
- Are recommended/default options pre-selected or highlighted?

---

## 4. Omit Needless Words

Halve the word count of every text block, then halve it again.

**Kill these:**
- "Happy talk" — welcome messages that say nothing useful
- Instructions that repeat what the UI already shows
- Introductory phrases: "Please note that", "In order to", "You can use this to"
- Marketing copy in functional UI

**Code checks:**
- Any text block >2 sentences in UI chrome (not content) needs trimming
- Error messages: state what happened + how to fix. Nothing else.
- Empty states: what to do next. No philosophy.
- Success messages: confirm what was done. One sentence.
- Tooltips: max 1-2 sentences

**Before:** "Welcome to our settings page! Here you can configure all of your account preferences and notification settings to customize your experience."
**After:** *[Remove entirely — the heading "Settings" is sufficient]*

---

## 5. Navigation Design

Navigation must answer 5 questions on every page within seconds.

### The Trunk Test

Arrive on any page as if from a search engine. Can you identify:

1. **What site is this?** — Site logo/name visible
2. **What page am I on?** — Page title or highlighted section
3. **What are the major sections?** — Top-level navigation visible
4. **What are my options at this level?** — Local navigation or content links
5. **Where am I in the scheme of things?** — Breadcrumbs or "you are here" indicator

**Persistent navigation requirements:**
- Site ID (logo linking home)
- Primary sections
- Utilities (search, account, cart)
- "You are here" indicator on current section/page

**Code checks:**
- Every page has persistent navigation with the above elements
- Breadcrumbs present on pages >1 level deep
- Nav labels: specific nouns, 1-2 words — "Pricing" not "Plans & Pricing Details"
- Search available from every page
- Logo links to home from every page

**Navigation label rules:**
- MUST be specific: "Documentation" not "Resources"
- MUST be noun-based: "Pricing" not "See Our Plans"
- SHOULD be 1-2 words maximum
- MUST NOT use internal jargon users wouldn't know

---

## 6. The Reservoir of Goodwill

Users arrive with a reservoir of goodwill. Each frustration drains it. When it empties, they leave.

### Major Drains

- Hiding information users need (phone number, pricing, shipping costs)
- Requiring unnecessary personal information
- Punishing users for not doing things your way (strict format requirements)
- Asking the same information twice
- Validation errors that don't explain what's wrong
- Requiring account creation for simple tasks
- Broken back button or unexpected navigation behavior

### Major Deposits

- Anticipating common questions and answering them inline
- Telling users costs/requirements upfront, not at the end
- Saving user effort (auto-fill, remember preferences, smart defaults)
- Recovering gracefully from errors with clear guidance
- Letting users do what they came to do without forced registration
- Providing clear confirmation that actions succeeded

**Code check:** For every form field, ask: "Do we actually need this?" For every step, ask: "Can the system do this automatically?"

---

## 7. Usability Testing

Test early, test often, with 3-5 users. Catches ~85% of usability problems.

**For an agent (cannot test with real users):** Apply the Fresh Eyes Heuristic Walk described in [ux-process.md](ux-process.md).

**Key principle:** One test with 3 users is better than zero tests with perfect methodology. The point isn't statistical significance — it's finding the obvious problems everyone on the team is too close to see.

**What to watch for in any interface:**
- Where would a user pause or hesitate?
- Where might a user click the wrong thing?
- What would a user say aloud if confused?
- Where would a user need to backtrack?
