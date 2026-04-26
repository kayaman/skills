# UX Review Checklist

Run against any interface. Each check references its governing principle.

---

## Cognitive Load

- [ ] No more than 7 items in any ungrouped list, menu, or nav (Miller's Law)
- [ ] Primary action on every screen is visually obvious within 2 seconds (self-evidence)
- [ ] Each modal/dialog contains exactly one decision (Hick's Law)
- [ ] Form fields grouped into sections of 3-5 with clear headings (Miller's Law)
- [ ] Labels use verb+noun format, no ambiguous terms (self-evidence)
- [ ] No "happy talk" or instructions that repeat what the UI already shows (omit needless words)
- [ ] Visual hierarchy guides the eye: heading > subheading > body > secondary (scanning)

## Interaction

- [ ] All clickable/tappable targets >= 44x44px (Fitts's Law)
- [ ] Adjacent clickable targets have >= 8px spacing (Fitts's Law)
- [ ] Primary CTA is visually distinct from secondary and tertiary actions (Von Restorff)
- [ ] Destructive actions require confirmation with specific label (error prevention)
- [ ] Every action is undoable, recoverable, or confirmed before execution (user control)
- [ ] Keyboard navigation works for all interactive elements (flexibility)

## Feedback

- [ ] Operations >400ms show loading indicator (Doherty Threshold)
- [ ] Operations >1s show progress bar (Doherty Threshold)
- [ ] Success states include confirmation with specific details (Peak-End Rule)
- [ ] Error messages state what happened AND how to fix it (error recovery)
- [ ] Empty states describe what to do next with a clear CTA (error prevention)
- [ ] Inline form validation appears within 400ms of field blur (Doherty + Postel's)

## Navigation

- [ ] Trunk Test passes: site ID, page name, sections, options, location all visible (Krug)
- [ ] Persistent navigation present on every page (Krug)
- [ ] Logo links to home (Jakob's Law)
- [ ] Breadcrumbs or "you are here" indicator on pages >1 level deep (Krug)
- [ ] Search available from every page (Krug)
- [ ] Nav labels are specific nouns, 1-2 words each (scanning)

## Input

- [ ] Text inputs accept liberal formats: phone, date, postal code (Postel's Law)
- [ ] Smart defaults reduce required user input (Tesler's Law)
- [ ] Auto-complete or auto-detect used where possible (Tesler's Law)
- [ ] Users are never asked for information the system already has (goodwill)
- [ ] Optional fields are clearly marked — or better, removed entirely (Hick's Law)

## Ethical Design

- [ ] No confirm-shaming language in any dialog or prompt
- [ ] Subscribe and unsubscribe require equal effort (asymmetry test)
- [ ] No pre-checked consent or opt-in boxes
- [ ] Primary action is genuinely the one that benefits the user
- [ ] No artificial urgency or false scarcity claims
- [ ] Effort to undo any action <= effort to perform it (asymmetry test)
