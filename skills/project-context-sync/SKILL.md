---
name: project-context-sync
description: Enforces updating a shared status file after each work session so that every agent and collaborator starts with accurate project state. Use when ending a session, completing a milestone, changing project phase, or before handing off to another agent or team member.
---

# Project Context Sync

Keep a single source of truth for project status by updating a shared context file at the end of every work session.

## When to Use

- End of any work session (chat, coding, planning)
- After completing a milestone or deliverable
- When a project changes phase (e.g. Phase A to Phase B)
- Before handing off work to another agent or team member
- After merging a significant PR or cutting a release

## Status File

Maintain a `context/status.md` (or equivalent) at the repository root with at minimum:

| Column | Content |
|--------|---------|
| **Project** | Name of the project or workstream |
| **Phase** | Current phase (e.g. Phase A, Phase B, GA) |
| **Last Milestone** | Most recent completed deliverable with version or PR reference |
| **Next Steps** | 1-3 concrete, actionable items (see rules below) |

Include a `Last updated` line with the date and a brief label (e.g. `2026-03-15 (auth-migration)`).

## Rules

### 1. Update on Every Session End

The status file MUST be updated at the end of every work session that touches any tracked project. Skipping an update means the next session starts with stale context.

### 2. Next Steps MUST Be Specific and Actionable

Each next step MUST describe a concrete action that someone can start immediately.

**Good:**
- "Create Prisma migration for `topics` table with title, created_at, user_id columns"
- "Configure `OPENAI_API_KEY` in repo secrets via `setup-gh-secrets.sh`"
- "Write Post 1 draft covering gateway evaluation criteria"

**Bad:**
- "Work on topics"
- "Set up keys"
- "Continue blog"

### 3. Link to Plan Files When In Progress

If a task references a plan or issue, link to it so the next session can pick up without searching.

```markdown
| AI Gateway | Phase A | Evaluation in progress | [confirm-gateway-choice](.cursor/plans/refined-gateway-phased-plan.plan.md): Complete evaluation |
```

### 4. Update Phase and Milestone Accurately

- Increment the phase only when its exit criteria are met.
- The milestone field reflects what was **completed**, not what is in progress.
- If a release was cut, include the version: `v0.2.0 released — CI setup + README`.

### 5. Touch Only Projects You Changed

Do not update rows for projects that were not touched in the current session.

### 6. Preserve the Format

Keep the status table in the same Markdown format so it can be parsed by scripts or other agents. Do not add free-form prose above the table.

## Checklist

Before ending a session, verify:

- [ ] Every project touched in this session has an updated row in the status table
- [ ] `Last Milestone` reflects the most recent completed deliverable
- [ ] `Next Steps` contains 1-3 specific, actionable items (not vague descriptions)
- [ ] Plan links are included for any in-progress tracked work
- [ ] `Last updated` date and label are current
- [ ] No untouched projects were modified
