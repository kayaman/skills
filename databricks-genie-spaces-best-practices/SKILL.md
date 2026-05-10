---
name: databricks-genie-spaces-best-practices
description: Design, configure, curate, govern, monitor, and integrate Databricks AI/BI Genie Spaces — the natural-language-to-SQL surface over Unity Catalog. Covers space scoping, general instructions, parameterized example SQL, SQL functions, trusted assets, JOIN configuration, knowledge store, certified queries, benchmarks, monitoring tab, feedback loops, the Genie Conversation API, governance via Unity Catalog (row filters, column masks, embedded warehouse credentials), and sharing/permissions. Use whenever the user mentions Genie, Genie Space, AI/BI Genie, Databricks natural language analytics, text-to-SQL on Databricks, or asks to build/curate/troubleshoot/embed a Genie experience. Do NOT use for: AI/BI Dashboards (visual BI without natural language), Databricks Assistant (in-IDE coding companion), Mosaic AI Agent Framework (custom agent apps), generic text-to-SQL outside Databricks, or LLM RAG over unstructured documents (Genie operates on structured Unity Catalog data only).
license: MIT
metadata:
  author: kayaman
  version: "1.0"
  sources: "Databricks AI/BI Genie official docs (docs.databricks.com/aws/en/genie); Databricks blog 'From Data to Dialogue: A Best Practices Guide for Building High-Performing Genie Spaces'; AI/BI release notes 2025–2026. Reinforced with O'Reilly: Damji et al. — Learning Spark, 2e; Jaiswal & Lee — Delta Lake: The Definitive Guide; Aslam et al. — Delta Lake: Up & Running; Reis & Housley — Fundamentals of Data Engineering; Uttamchandani — The Self-Service Data Roadmap; Dehghani — Data Mesh; Kleppmann — Designing Data-Intensive Applications, 2e."
allowed-tools: Read Grep Glob WebFetch Bash(databricks:*) Bash(jq:*) Bash(curl:*)
---

# Databricks AI/BI Genie Spaces — Best Practices

Genie Spaces let business users ask questions in natural language and get SQL-backed answers over Unity Catalog data. The skill operates against a **compound AI architecture**: an LLM is one component among many — the answer quality is dominated by what *you* curate (schema metadata, example SQL, SQL functions, instructions, joins) more than by the model itself.

This file is the table of contents. Load referenced files only when the task at hand needs them.

| Reference | When to load |
|---|---|
| `references/SETUP.md` | Creating a new space, prerequisites, entitlements, choosing tables and warehouses, sharing, cloning. |
| `references/CURATION.md` | Writing General Instructions, parameterized Example SQL, SQL Functions, Trusted Assets, joins, synonyms, descriptions, knowledge store. |
| `references/MONITORING.md` | Monitoring tab, weekly digest, "Is this correct?" feedback, benchmarks, Quality Review (Beta), audit logs. |
| `references/API.md` | Conversation API — auth (OAuth U2M / M2M), endpoints, polling, embedding Genie into apps, rate limits. |
| `references/GOVERNANCE.md` | Unity Catalog row filters and column masks, embedded warehouse credentials, PII, permission levels, audit. |
| `references/ANTIPATTERNS.md` | Reviewing an underperforming space — concrete failure modes and the curation fixes that resolve them. |
| `references/EXAMPLES.md` | Worked examples for two domains (Sales pipeline, IoT telemetry): instructions, parameterized SQL, SQL functions, benchmarks. |
| `references/REFERENCES.md` | Authoritative Databricks docs and O'Reilly book references with chapter pointers. |

Templates (drop-in starting points; copy and adapt):

- `assets/space-config.template.json` — full configuration scaffold with every supported field.
- `assets/general-instructions.template.md` — the four sections every General Instructions block should have.
- `assets/example-sql.template.sql` — parameterized Example SQL with the headers Genie expects.
- `assets/benchmark.template.csv` — benchmark question/expected-SQL/expected-result triplet.

---

## When to use Genie (and when not)

**Use Genie when:**

- The audience is **business users** asking ad-hoc questions over a **bounded, well-modelled domain** (one team, one fact, a few dimensions).
- Underlying data is **structured and in Unity Catalog** — Delta tables, views, materialized views, metric views.
- A **domain expert** (ideally a SQL-fluent analyst) can own curation: instructions, example queries, ongoing monitoring.
- The questions are open-ended *but bounded by the data model* — "how did EMEA pipeline trend QoQ?" not "should we acquire Acme?"

**Do NOT use Genie when:**

- The data is unstructured (PDFs, transcripts, logs as free text). Genie cannot read them; use Mosaic AI Agent Framework with a vector index instead.
- The required answer needs **fresh, transactional consistency** (real-time inventory, payment authorization). Genie reads from a SQL warehouse — it is analytic-time, not OLTP.
- The space is being asked to span > 30 tables or > 1 business domain. Either consolidate via views/metric views or split into multiple focused spaces.
- The team cannot commit to **iterative curation**. A Genie space is not a deploy-and-forget asset; without monitoring + feedback loops it degrades as questions evolve.

(Sources: Databricks docs — *What is a Genie Space*; Uttamchandani, *The Self-Service Data Roadmap*, O'Reilly, ch. on self-service success criteria.)

---

## The five non-negotiables

These hold across every production Genie space. Detailed treatment in the referenced files.

1. **Scope to one domain.** A space answers questions for *one* audience over *one* coherent data model. Cross-domain spaces produce ambiguous joins and noisy answers. (Dehghani, *Data Mesh*, O'Reilly — domain ownership.)
2. **Prefer SQL over prose for anything expressible in SQL.** Metrics, filters, business definitions, common rollups go into **SQL Functions** and **parameterized Example SQL**, not General Instructions. SQL is unambiguous; prose is interpreted by an LLM. See `references/CURATION.md`.
3. **Make answers Trusted by construction.** When Genie's generated SQL exactly matches a parameterized Example SQL or SQL Function, it is marked **Trusted**. Aim for the high-traffic questions to all hit Trusted assets. Trust is a coverage metric, not an afterthought.
4. **Govern at Unity Catalog, not at the space.** Row filters, column masks, and table ACLs in Unity Catalog are enforced per-user automatically — Genie inherits them. Do not try to recreate ACLs inside General Instructions; users can phrase around them.
5. **Close the feedback loop.** The Monitoring tab + thumbs-up/down + Quality Review are the curation signal. Every week: review flagged answers → add/repair an Example SQL or SQL Function → record a benchmark question. See `references/MONITORING.md`.

---

## Configuration surface (everything you can tune)

Detailed semantics in `references/SETUP.md` and `references/CURATION.md`. Top-level summary so you can plan before opening the UI:

| Area | Field | Purpose |
|---|---|---|
| Identity | Title, Description (Markdown), Thumbnail, Tags (Public Preview) | Discovery and audience expectations. |
| Compute | SQL Warehouse (**Pro or Serverless** — Serverless recommended) | Executes generated SQL; credentials are embedded. |
| Data | Up to **30** tables/views/metric views from Unity Catalog | Scope of the space. |
| Schema metadata | Table description, column comments, synonyms (space-scoped) | Disambiguates terms ("revenue" → `gross_revenue_usd`). |
| Relationships | Primary keys, foreign keys, JOIN configuration | Created automatically from PK/FK; review before sharing. |
| Welcome | Common Questions (sample prompts shown to users) | Onboarding and scope signalling. |
| Curation | General Instructions (sectioned Markdown) | Clarification, summary style, scope bounds, out-of-scope refusals. |
| Curation | Example SQL Queries (parameterized) | Canonical answers for known question shapes. |
| Curation | SQL Functions (Unity Catalog UDFs) | Reusable metric definitions; eligible for Trusted designation. |
| Curation | Knowledge Store (preview) | Glossaries, business definitions, prompt-matching aids. |
| Quality | Benchmarks (text → expected SQL → expected result) | Scored evaluation harness; auto-suggested in 2026. |
| Sharing | Permission levels: **CAN MANAGE / CAN EDIT / CAN RUN / CAN VIEW** | Curator vs consumer separation. |
| Operations | Monitoring tab, Weekly digest, Quality Review (Beta) | Feedback signal for the next iteration. |
| Integration | Conversation API (`/api/2.0/genie/spaces/...`) | Embed Genie in custom apps; OAuth U2M or M2M. |

Hard limits worth knowing up front:

- **30** tables/views/metric views per space. Consolidate with views if you exceed this.
- **20** questions per minute per workspace (free tier reference: ~5/min).
- **10,000** conversations per space. Plan for archival/cloning before exhaustion.

---

## The shortest path to a high-quality space

Use this when standing up a new space. Copy the checklist into your response and tick as you go.

```
- [ ] Define one audience, one domain, one north-star question shape (write it down)
- [ ] Identify ≤ 30 tables/views; pre-join into views or metric views if you'd exceed
- [ ] Verify Unity Catalog: PK/FK declared, table+column descriptions populated, row filters/column masks attached
- [ ] Pick a Serverless SQL warehouse; verify CAN USE for the space owner
- [ ] Create the space; set Title, Markdown Description, Thumbnail, Tags
- [ ] Add 5–10 Common Questions covering the dominant question shapes
- [ ] Write General Instructions in four sections: Scope, Clarification, Metric definitions, Summary style
- [ ] Add 8–15 parameterized Example SQL queries for the dominant shapes; mark each as a candidate for Trusted
- [ ] Promote stable metrics to SQL Functions in Unity Catalog; reference them from Example SQL
- [ ] Review auto-generated JOINs; remove or rewrite any that are wrong
- [ ] Build a benchmark of ≥ 20 questions with expected SQL + expected result; let Genie auto-suggest more
- [ ] Share with a *small* pilot group (CAN RUN); collect thumbs-up/down + "Fix it" feedback for one week
- [ ] Process Monitoring tab feedback into new Example SQL / SQL Functions / instruction edits
- [ ] Re-run benchmarks; only roll out to all account users after the pass rate stabilizes
```

If any box is "no" when the space ships, expect quality complaints proportional to the number of unchecked boxes.

---

## Known gotchas (load `references/ANTIPATTERNS.md` for the full list)

- **General Instructions doing the work of SQL.** "Always exclude test customers" written in prose will be inconsistently applied. Encode it in the Example SQL `WHERE` clause or in a SQL Function.
- **Auto-generated JOINs from missing FKs.** If PK/FK aren't declared in Unity Catalog, Genie infers joins from column-name similarity. Declare keys explicitly and review the JOIN panel before sharing.
- **One mega-space.** A 28-table space spanning Sales + Marketing + Support will produce wrong joins under load. Split into focused spaces; clone settings between them.
- **Display strings in Example SQL.** `WHERE region = 'EMEA'` works until someone renames it to `'Europe'`. Use SQL Functions or stable IDs.
- **Skipping benchmarks because "it answered correctly once."** A benchmark exists to catch regressions when you edit an instruction. Without it, every curation change is a gamble.
- **Treating thumbs-down as noise.** Each downvote is a labeled training signal you already paid for. Process them weekly.

---

## Validating your work (self-correcting loop)

Before declaring a space ready for general access:

1. Run the benchmark set (≥ 20 questions). Target ≥ 80% Trusted answers and ≥ 95% factually-correct answers on the benchmark.
2. Open `references/ANTIPATTERNS.md` and audit the space against each item — fix or accept-with-reason.
3. Pilot with the smallest group that gives realistic queries. Rate-limit access by permission, not by communication.
4. Process the Monitoring tab weekly and edit curation. **Iterate before broad rollout, not after.**
5. Repeat until the benchmark pass rate is stable across two consecutive weeks of real traffic.

---

## Pointers to related skills

- `aws-genai-lens` / `aws-well-architected` — when Genie is part of a broader AWS GenAI architecture (governance, cost, security pillars).
- `domain-driven-design` — bounded contexts map cleanly onto one-space-per-domain.
- `event-driven-design` — when Genie answers depend on streamed CDC sources hydrating Delta tables.
- `api-design-principles` — designing the wrapper API around the Genie Conversation API for embedded use cases.
