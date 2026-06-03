---
name: todo
description: Create and maintain a TODO.md file at the repository root that tracks ONLY showstoppers — the concrete tasks currently blocking project development — as a priority-ordered numbered checklist with optional subtasks. Use this skill whenever the user wants to record, review, update, reprioritize, or check off blocking work, or says things like "todo", "add to my todo", "update TODO.md", "what's blocking me", "track this", "mark that done", "what do I still need to do", or wants a durable list so they don't lose critical work if a chat transcript is lost. Also use it proactively the moment a hard blocker to further progress is identified during work — capture it before it evaporates. Keeps TODO.md local (gitignored) so it is never pushed to a remote.
---

# todo

Maintain a single `TODO.md` at the repository root that is the user's durable, at-a-glance
list of **showstoppers**: the things actually blocking the project from moving forward. Its
whole reason to exist is to be a safety net — if a chat transcript is lost or a session ends,
the critical next actions survive on disk.

## What belongs here (and what doesn't)

This is **not** a brain-dump or a backlog. Be ruthless about that — a list of 40 "would be
nice" items is worse than useless because it buries the 3 things that actually matter.

- **Include:** hard blockers, decisions the user must make, things with external lead time
  (orders, approvals), and the single next action needed to unblock progress.
- **Exclude:** nice-to-haves, polish, ideas, anything already captured elsewhere (a roadmap,
  an issue tracker). If it isn't blocking forward motion, it doesn't go in `TODO.md`.

When unsure whether something is a showstopper, ask: *"If this stays undone, does real progress
stop?"* Only a "yes" earns a spot.

## File location

Write to `TODO.md` at the repo root. Find the root with `git rev-parse --show-toplevel`; if the
project isn't a git repo, use the current working directory. One `TODO.md` per project.

## Format

Use a numbered list ordered by priority, **highest first** (item 1 is the most urgent blocker).
Every task is a checkbox; subtasks are nested checkboxes. Keep titles short and concrete — name
the action, not the topic ("Decide bowl-state class count", not "Classes").

```markdown
# TODO

> Showstoppers blocking development, highest priority first.
> Local-only — not pushed to remote. Last updated: <YYYY-MM-DD>

1. [ ] <Most urgent blocker — the one thing to do next>
   - [ ] <subtask, if the blocker breaks into steps>
   - [x] <subtask already done>
2. [ ] <Next blocker>
3. [x] <Recently completed blocker — kept briefly so the user sees it's handled>
```

Rules that keep the file trustworthy:

- **Reorder after every edit** so the numbering always reflects true priority. A stale order
  defeats the "glance and know what's next" purpose.
- **Check off, don't silently delete.** Mark a finished blocker `[x]` so the user sees it was
  handled. Prune `[x]` items once the user has clearly moved on, to keep the list short.
- **A parent is only `[x]` when all its subtasks are.** Mixed subtasks ⇒ parent stays `[ ]`.
- Keep the whole file scannable in a few seconds. If it's growing past ~10 top-level items,
  that's a signal non-blockers crept in — trim them.

## Operating on the file

1. Read the existing `TODO.md` first (if any) so you preserve and update rather than overwrite.
2. Apply the change: add a blocker, break one into subtasks, check items off, or reprioritize.
3. Rewrite the file with items re-sorted by priority and the `Last updated` date refreshed.
4. Ensure it stays out of the remote (next section).

When the user states a new blocker mid-conversation, add it without being asked — that's the
proactive use. When they say something is done, check it off.

## Keep it off the remote

The user wants this list to survive locally but never reach a remote. Git can't keep a *committed*
file off a remote per-file (push moves whole commits), so the reliable mechanism is to **gitignore
it**: the file stays in the working tree (safe across sessions) and can never be pushed.

Ensure the repo root `.gitignore` contains a `TODO.md` line; create `.gitignore` if absent and
append the line if missing. Don't add `TODO.md` to a commit. If the user later says they *do* want
it version-controlled, removing the `.gitignore` line is all it takes — mention that option rather
than deciding for them a second time.
