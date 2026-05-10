# Monitoring Genie Spaces

Monitoring is curation's input signal. A space without a weekly monitoring review is a space that's silently degrading.

## Contents

1. The Monitoring tab — what's in it
2. User-side feedback ("Is this correct?", thumbs)
3. Weekly digest
4. Quality Review (Beta)
5. Benchmarks — building, running, evolving
6. Audit logs and system tables
7. The weekly review ritual
8. KPIs to track

---

## 1. The Monitoring tab

Visible to users with `CAN MANAGE` on the space. Surfaces every question and answer the space has produced.

Filter by:

- **Time range** — last 24h, 7d, 30d, custom.
- **Rating** — thumbs up / thumbs down / no rating.
- **Status** — Reviewable, Fixed, Open.
- **User** — drill into a specific consumer's history.

Each entry shows the question, the generated SQL, the result, and any feedback the user attached. The SQL is editable in-place — fixing an answer here is the fastest path to producing a new Example SQL.

## 2. User-side feedback

After every answer, Genie shows **"Is this correct?"** with three options:

| Option | What happens |
|---|---|
| Yes | Logged as a positive signal. No action required. |
| Fix it | User describes what's wrong; can regenerate or just submit feedback. The entry is flagged for the curator. |
| Request review | The conversation is marked Reviewable; managers see it in Quality Review. Optional comment. |

In addition, every message has a thumbs-up / thumbs-down button — lower friction than the modal, used as the dominant signal in practice.

**Curation implication.** Coach pilot users: a thumbs-down without a "Fix it" comment is far less useful than one with. Add this to the rollout email.

## 3. Weekly digest

The Monitoring tab's **Weekly digest** card surfaces:

- Total messages this week vs last.
- Active users.
- Thumbs up/down counts (and their ratio).
- The "Analyze space usage" button → launches Genie Code, which summarises usage patterns and proposes specific curation improvements.

Treat the weekly digest as the agenda for the curation review.

## 4. Quality Review (Beta)

Conversations marked **Reviewable by space managers** become available in Quality Review. Managers with `CAN MANAGE` can:

- Inspect the full conversation, generated SQL, and results.
- Score response quality.
- Identify patterns where additional Example SQL or SQL Functions would help.
- For *private* conversations, only the prompt is visible — not the answer or data.

Use Quality Review for hard-to-reproduce or sensitive conversations the user explicitly flagged. Don't try to use it as the primary review surface — Monitoring is faster.

## 5. Benchmarks

A benchmark is a labeled set of `(question, expected SQL, expected result)` triples used to score the space objectively as you change instructions and examples.

**Building the initial set:**

1. Start with the top 20 most-asked questions from the Monitoring tab (or your team's stated questions if the space is brand new).
2. For each, write the canonical SQL you would accept.
3. Run the benchmark; fix curation until each one passes.
4. Save the benchmark set.

**2026 features:**

- Genie auto-suggests benchmark questions based on the space's context — accept, edit, or reject each.
- After running a benchmark, a correct Genie answer can be saved as the **expected** SQL for future runs (one-click).
- The editor can generate benchmark SQL from a benchmark question — verify before committing.

**Running cadence:** before any non-trivial curation change, and as a CI gate before broader sharing. Diff the pass rate; never ship a regression.

## 6. Audit logs and system tables

For governance and FinOps work:

- **Audit logs** record every Genie action — who asked what, when, with which space, which warehouse, which result. Available via the standard Databricks audit log facility.
- **System tables** expose Genie usage metrics for SQL queries — wire into FinOps dashboards alongside warehouse cost.
- The same `correlation_id` flows through audit logs, warehouse query history, and the Genie API response — useful when debugging end-to-end.

## 7. The weekly review ritual

Block 30 minutes per week per space. Run this ritual:

```
- [ ] Open Monitoring → sort by thumbs-down + "Fix it" + Quality Review flags
- [ ] For each flagged item, classify: bad SQL / wrong metric / out-of-scope / actually correct
- [ ] For "bad SQL": add or repair an Example SQL or SQL Function
- [ ] For "wrong metric": tighten column comment / add synonym / clarify in instructions
- [ ] For "out-of-scope": tighten Scope section to refuse with a redirect
- [ ] For "actually correct": educate the user (reply on the thread); investigate UX confusion
- [ ] Add each fixed question to the benchmark set with corrected expected SQL
- [ ] Re-run the benchmark — confirm no regression
- [ ] Update the Genie space's own CHANGELOG.md or curation history tracker in that space's repo (do not add a CHANGELOG.md to this skill directory)
- [ ] Ship
```

A space without this ritual produces curation-by-guessing, which produces drift, which produces the "Genie is unreliable" complaint that quietly kills adoption.

## 8. KPIs to track

| KPI | Target | Why |
|---|---|---|
| Trusted answer rate | ≥ 60% overall, ≥ 90% on top-20 questions | Coverage of high-value question shapes by Trusted Assets. |
| Thumbs-up : thumbs-down ratio | ≥ 5:1 after pilot stabilises | Direct user satisfaction proxy. |
| Benchmark pass rate | ≥ 95% factually correct | Catches regressions from curation edits. |
| "Fix it" submissions per week | Trending down | Curation is closing real gaps faster than new ones arrive. |
| Out-of-scope refusal rate | Stable, not growing | If growing, the space is being pulled out of scope — communicate or split. |
| P95 query duration | < 15s | Warehouse rightsizing signal. |
| Conversation count vs 10k cap | < 80% | Plan archival/cloning before exhaustion. |

Track these in a notebook or AI/BI Dashboard backed by audit + system tables. Sources: Databricks docs (*Monitor a Genie Space*); reinforced by Reis & Housley, *Fundamentals of Data Engineering* (O'Reilly) — observability for data products.
