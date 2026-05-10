# Setting Up a Genie Space

Step-by-step: from prerequisites to a shareable, governed space. Covers everything you tune *before* curation.

## Contents

1. Prerequisites and entitlements
2. Workspace + account-level enablement
3. Creating the space
4. Selecting data
5. Choosing a SQL warehouse
6. Identity (Title, Description, Thumbnail, Tags)
7. Common Questions
8. Sharing and permission levels
9. Cloning a space
10. Exporting to a Metric View

---

## 1. Prerequisites and entitlements

**For curators (CAN MANAGE / CAN EDIT):**

- Databricks SQL workspace entitlement.
- `CAN USE` on at least one **Pro or Serverless** SQL warehouse.
- `SELECT` privileges on every Unity Catalog object the space will reference.
- `CAN EDIT` (or higher) on the space itself.

**For end users (CAN RUN / CAN VIEW):**

- Either Consumer access *or* SQL workspace entitlement.
- `SELECT` privileges on every Unity Catalog data object referenced by the space.
- `CAN VIEW` (read-only) or `CAN RUN` (can ask questions) on the space.
- **Users do not need direct warehouse access** — credentials are embedded in the space.

## 2. Account- and workspace-level enablement

A workspace admin must enable Partner-powered AI features at both account and workspace level before any Genie Space can be created. This is a one-time setting per workspace.

## 3. Creating the space

1. Open **AI/BI** → **Genie** in the workspace sidebar.
2. Click **New**.
3. Pick the catalog and schemas whose tables you'll add (you can add more later).
4. Click **Create**.

The space starts in *draft* state — only you can see it until shared.

## 4. Selecting data

Open **Configure → Data**.

- Add up to **30** tables, views, materialized views, or metric views.
- Verify each table's columns: name, type, description, sample data preview.
- Remove anything that isn't needed for the space's question shapes — every extra column is a noise source for the LLM.
- If you'd exceed 30 objects, **pre-join into views or metric views** in Unity Catalog instead of stretching the limit.

**Heuristic:** start with ≤ 5 well-described tables. Add more only when monitoring shows users asking questions the current set can't answer.

## 5. Choosing a SQL warehouse

Open **Configure → Settings**.

- Pick a **Serverless** warehouse where available — fastest cold-start, fewest knobs.
- Otherwise pick a **Pro** warehouse (Classic warehouses are not supported).
- The chosen warehouse's compute credentials are embedded into the space — end users do not need their own warehouse access.
- Size: start small (XS / S). Genie generates one query per question; concurrency is your dimensioning input.

**Cost consideration.** Serverless billing is per-second on actively-running queries. Idle spaces cost nothing. Spaces with high traffic but cheap queries can run on small warehouses; rightsizing comes from the Monitoring tab's query-duration histogram.

## 6. Identity — Title, Description, Thumbnail, Tags

| Field | Use it for |
|---|---|
| Title | Short, audience-specific. Bad: "Sales Data". Good: "EMEA Pipeline & Forecast — RevOps". |
| Description | Markdown supported. Two paragraphs: (1) what questions the space answers; (2) what it does *not* answer + where to go instead. |
| Thumbnail | Distinguishes the space in long lists; pick something domain-recognisable. |
| Tags (Public Preview) | Faceted discovery; align with your data-mesh domain taxonomy. Requires CAN EDIT. |

A specific Description meaningfully reduces "wrong space" support tickets. Treat it as the contract between curator and consumer.

## 7. Common Questions

Common Questions appear on the empty-state of the space and shape user expectations.

- Add 5–10 questions, each one a *different* question shape (aggregation, trend, ranking, filter, distribution).
- Use exactly the wording you expect users to actually type — not a polished brochure.
- Keep the list short. If it grows beyond 10, the dominant shapes are unclear and the space is probably too broad.

## 8. Sharing and permission levels

Click **Share** in the top-right.

| Permission | Can do |
|---|---|
| `CAN MANAGE` | Edit + share + delete. View Quality Review. |
| `CAN EDIT` | Edit data, instructions, examples. Cannot delete or reshare. |
| `CAN RUN` | Ask questions, see answers and SQL. Provide feedback. |
| `CAN VIEW` | See the space and prior conversations. Cannot ask questions. |

Patterns:

- **Pilot rollout.** Share `CAN RUN` with a named group of ≤ 20 users for the first week. Collect feedback. Iterate.
- **Broad rollout.** Once the benchmark pass rate is stable, share `CAN RUN` with **All account users** or your domain group.
- **Curator delegation.** `CAN EDIT` for domain analysts; reserve `CAN MANAGE` for the data product owner.

Users get an email notification on share. Document the space's scope in the email body or in the Description.

## 9. Cloning a space

Cloning copies tables, settings, instructions, and example SQL — but **not** chat history. Use it when:

- Splitting an over-broad space into per-domain spaces.
- Producing a sandbox copy for instruction experiments without affecting the production space.
- Templating a new space from a known-good one.

After cloning, immediately re-scope the Title, Description, Tags, and the data set — leftover identity from the source space is the most common source of confusion.

## 10. Exporting to a Metric View

Genie can export a space's effective semantic context (joins, filters, derived metrics) as a Unity Catalog Metric View. Use this when:

- The same business definitions need to be shared with **AI/BI Dashboards**, notebooks, and Genie consistently.
- You want to lift the semantic layer out of the space and into Unity Catalog as the source of truth, then point the space at the metric view.

This is one of the higher-leverage operations available — it turns curation into reusable metadata rather than space-local configuration.

---

## What "ready to share" looks like

Before clicking Share for the first time:

- [ ] All referenced tables have non-trivial descriptions and column comments in Unity Catalog.
- [ ] PK/FK declared on every table participating in joins.
- [ ] Row filters and column masks for sensitive columns are in place at the Unity Catalog level.
- [ ] The Serverless/Pro warehouse is sized and tested with the heaviest example query.
- [ ] Title and Description name the audience and the scope explicitly.
- [ ] At least 5 Common Questions, ≥ 8 Example SQL queries, ≥ 1 SQL Function for the central metric.
- [ ] At least one curator other than yourself has `CAN EDIT`.

For the curation work that follows this checklist, load `CURATION.md`.
