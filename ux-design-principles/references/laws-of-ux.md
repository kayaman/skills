# Laws of UX

Reference: *Laws of UX, 2nd Edition* by Jon Yablonski (O'Reilly Media)

Each law follows: Principle, When It Applies, Code Checks, Violation, Fix.

---

## 1. Fitts's Law

**Principle:** Time to acquire a target = f(distance / size). Larger, closer targets are faster to reach.

**When:** Buttons, links, form controls, touch targets, dropdown items, mobile tap areas.

**Code checks:**
- All interactive elements: at least `min-width: 24px; min-height: 24px` to meet WCAG 2.5.8 minimum target size requirements (exceptions may apply); prefer `44px × 44px` as a touch-friendly best practice
- Spacing between adjacent clickable targets >= 8px to prevent mis-taps
- Primary CTA positioned near expected cursor location (end of form, center of modal)
- Corner/edge targets on desktop benefit from edge anchoring (infinite target depth)

**Violation:** 16x16px close button in modal corner on mobile.
**Fix:** Increase to at least a 24x24px target to satisfy WCAG 2.5.8 where applicable; prefer a 44x44px tap target with generous padding, even if the icon remains visually smaller.

---

## 2. Hick's Law

**Principle:** Decision time increases logarithmically with number of choices.

**When:** Navigation menus, dropdowns, settings pages, onboarding flows, pricing tables.

**Code checks:**
- Count options in any select/menu/nav: >7 means restructure
- Check for progressive disclosure (can options be revealed in stages?)
- Settings: group into categories, show 5-7 per category
- Onboarding: one question per step

**Violation:** Settings page with 30 ungrouped toggles.
**Fix:** Group into categories, collapse advanced settings behind "Show more".

---

## 3. Jakob's Law

**Principle:** Users spend most of their time on *other* sites/apps. They expect yours to work the same way.

**When:** Navigation placement, e-commerce checkout, form layout, icon meanings, keyboard shortcuts.

**Code checks:**
- Logo top-left linking to home?
- Primary nav horizontal on desktop?
- Search icon = magnifying glass? Cart = top-right?
- Standard keyboard shortcuts work (Ctrl+S, Ctrl+Z, Escape to close)?
- Mobile: swipe, pull-to-refresh, back gesture follow OS conventions?

**Violation:** Hamburger menu on desktop with only 5 nav items.
**Fix:** Horizontal nav bar following platform convention.

---

## 4. Miller's Law

**Principle:** Working memory holds ~7 (plus/minus 2) chunks. Chunk information to aid processing.

**When:** Long forms, data tables, navigation, lists, multi-step flows, dashboards.

**Code checks:**
- Count visible items in any list/nav/form without visual grouping: >7 needs chunking
- Multi-step flows have step indicator showing total and current position
- Phone/card numbers displayed with grouping spaces
- Tables with >5 columns: consider which columns are essential vs. expandable

**Violation:** 15-field form with no section breaks.
**Fix:** 3 sections of 5 fields with clear headings.

---

## 5. Peak-End Rule

**Principle:** People judge an experience by its peak (most intense moment) and its end, not the average.

**When:** Onboarding, checkout completion, error recovery, sign-up, cancellation flows.

**Code checks:**
- Success states have satisfying confirmation with specifics (order number, next steps)
- Error states are helpful, not hostile (state what happened + how to fix)
- Final step of any flow leaves a positive impression
- Onboarding ends with immediate value, not "wait for approval"

**Violation:** Checkout completes with bare "Order placed" text.
**Fix:** Confirmation with order summary, delivery estimate, and a celebratory visual.

---

## 6. Aesthetic-Usability Effect

**Principle:** Aesthetically pleasing designs are perceived as more usable. Visual polish creates positive emotional responses that increase tolerance for minor issues.

**When:** First impressions, onboarding, landing pages, error states, loading states.

**Code checks:**
- Consistent spacing and alignment (use design tokens or a spacing scale)
- Loading states are designed (skeleton screens, not raw spinners)
- Error pages are styled and helpful, not browser defaults
- Empty states have illustration or guidance, not just blank space

**Note:** Investing in visual refinement IS a usability investment, not vanity.

---

## 7. Von Restorff Effect (Isolation Effect)

**Principle:** Among similar items, the one that differs most is best remembered and most noticed.

**When:** Pricing tables, CTAs, notifications, feature highlights, navigation current state.

**Code checks:**
- Primary action visually distinct (color, size, weight) from secondary actions
- In pricing tables, recommended plan is visually isolated
- Important notifications use distinct color/position from informational ones
- Current nav item has clear visual differentiation

**Violation:** Three buttons — "Cancel", "Save Draft", "Publish" — all identical styling.
**Fix:** "Publish" primary color+size; "Save Draft" secondary; "Cancel" text-only.

---

## 8. Tesler's Law (Conservation of Complexity)

**Principle:** Every system has inherent complexity that cannot be removed — only moved. Push complexity to the system, not the user.

**When:** Forms, configuration, address entry, date/time input, search, data import.

**Code checks:**
- Auto-detection: location, timezone, language, currency
- Auto-formatting: phone numbers, postal codes, credit cards
- Smart defaults: pre-fill country from locale, default to most common option
- Auto-complete for addresses, usernames, tags

**Violation:** Requiring exact state abbreviation format ("CA" not "California").
**Fix:** Accept "California", "CA", "ca", "california" — normalize server-side.

---

## 9. Doherty Threshold

**Principle:** Productivity soars when system response < 400ms. Beyond that, users perceive lag.

**When:** Form submissions, page loads, search, filtering, saving, API calls.

**Code checks:**
- >400ms: show loading indicator (spinner, skeleton, disabled state)
- >1s: show progress bar
- >10s: show progress percentage or step count
- Non-destructive mutations: consider optimistic UI (update immediately, reconcile after)
- Debounce search/filter inputs to avoid unnecessary loading states

**Violation:** Clicking "Save" with no feedback for 2 seconds.
**Fix:** Immediate disabled state + spinner on button, or optimistic "Saved" toast.

---

## 10. Postel's Law (Robustness Principle)

**Principle:** Be liberal in what you accept from users, strict in what you produce.

**When:** Form inputs, search queries, data import, phone/date/address fields.

**Code checks:**
- Phone: accept `(555) 123-4567`, `555-123-4567`, `5551234567`, `+1 555 123 4567`
- Date: accept `03/15/2025`, `March 15, 2025`, `2025-03-15`
- Search: handle typos gracefully (fuzzy matching, "did you mean?")
- Output: always consistently formatted regardless of input format
- Trim whitespace, normalize case where appropriate

**Violation:** Phone field rejecting "(555) 123-4567" because it expects digits only.
**Fix:** Accept any reasonable format, strip to digits, validate length, display formatted.
