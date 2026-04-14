---
name: Home feed UX rework
overview: "Replace the two equal tabs and implementation-centric labels with a personal-first home: signed-in users default to their bookmarks, with discovery as a secondary choice; signed-out users see only the discoverable stream and a clear sign-in CTA—no fake dual-tab parity."
todos:
  - id: index-routing
    content: "Refactor index.tsx: default saved when auth, view=public support, URL sync"
    status: completed
  - id: index-ui
    content: "Signed-out: single feed + one sign-in CTA; signed-in: Your bookmarks + Discover hierarchy"
    status: completed
  - id: feed-copy
    content: Align BookmarkFeed error strings with new naming
    status: completed
  - id: verify-check
    content: Run npm run check and smoke manual flows
    status: completed
isProject: false
---

# Rework home page feed UX (remove Public feed / My bookmarks tabs)

## Problem

[`src/pages/index.tsx`](file:///home/kayaman/Projects/blogmarks/src/pages/index.tsx) presents **two sibling tabs**: "Public feed" and "My bookmarks". That frames the app like a social timeline and uses internal/API-ish wording, which clashes with a **personal bookmark** product (see MVP in [`AGENTS.md`](file:///home/kayaman/Projects/blogmarks/AGENTS.md)).

## Target behavior (personal-first)

| Audience | Primary view | Secondary |
|----------|--------------|-----------|
| Signed out | Single stream (today’s public API) | No second tab; sign-in CTA only |
| Signed in | **Your bookmarks** (private API), default on `/` | **Discover** (today’s public feed), via explicit choice |

Deep links:

- Keep [`/?view=saved`](file:///home/kayaman/Projects/blogmarks/src/pages/saved.tsx) and `/saved` → `/?view=saved` working.
- Add **`/?view=public`** so signed-in users can bookmark/share the discover view (symmetric to `view=saved`).

Default routing when auth becomes available:

- If **authenticated** and query has no `view` (or `view=saved`), show **private** feed.
- If **authenticated** and `view=public`, show **public** feed.
- If **anonymous**, always show public feed only (ignore `view=saved` for content; sign-in flow can still target `/?view=saved` after login).

## UI changes ([`src/pages/index.tsx`](file:///home/kayaman/Projects/blogmarks/src/pages/index.tsx))

1. **Signed out**  
   - Remove the tab row that shows "Public feed" + "Sign in for My bookmarks".  
   - Render `BookmarkFeed` in `public` mode only.  
   - Add a **single** clear CTA (e.g. text link or button) to sign in—reuse `next=/` or `/?view=saved` so post-login lands on bookmarks.

2. **Signed in**  
   - Replace equal pills with **primary vs secondary** affordances, for example:  
     - **Your bookmarks** — primary / selected when on private mode.  
     - **Discover** — secondary (outline or text link) when on public mode.  
   - Labels to avoid: "Public feed", "My bookmarks" (too cold / RSS-ish).

3. **State + URL**  
   - Initialize `feedTab` as `'public'` until `isLoading` is false; then if `isAuthenticated`, default to `'saved'` unless `router.query.view === 'public'`.  
   - `selectTab('saved')` → `router.replace('/' or '/?view=saved', shallow)` (pick one canonical form; prefer **`/`** for default signed-in home if `view` is omitted when on saved).  
   - `selectTab('public')` → `router.replace('/?view=public', shallow)`.  
   - Extend the existing `useEffect` that reads `view=saved` to also read `view=public`.

## Copy alignment ([`src/components/BookmarkFeed.tsx`](file:///home/kayaman/Projects/blogmarks/src/components/BookmarkFeed.tsx))

- Update configuration error strings to match new naming (e.g. "Your bookmarks" / "Discover" instead of "My bookmarks API" / "Public feed").

## Docs (optional)

- If you want repo docs in sync: short updates to [`README.md`](file:///home/kayaman/Projects/blogmarks/README.md) home-page bullet and [`AGENTS.md`](file:///home/kayaman/Projects/blogmarks/AGENTS.md) `/` route description.

## Verification

- Manual: anonymous `/` — no duplicate tab, public list loads, sign-in works.  
- Manual: signed-in `/` — defaults to your bookmarks; Discover shows public list; refresh preserves tab via query.  
- `npm run check` (or project lint/tsc) after edits.
