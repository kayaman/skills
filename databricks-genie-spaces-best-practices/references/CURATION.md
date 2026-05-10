# Curating a Genie Space

Curation is what makes the difference between a space that delights users and one that quietly produces wrong answers. Genie's response quality is dominated by the curated artifacts — the LLM is incidental.

## Contents

1. The curation hierarchy (what to write where)
2. Schema metadata in Unity Catalog
3. JOIN configuration
4. General Instructions — structure and style
5. Example SQL Queries (parameterized)
6. SQL Functions
7. Trusted Assets — what gets the badge
8. Knowledge Store and synonyms
9. Curation feedback loop

---

## 1. The curation hierarchy

When teaching Genie a fact about your data, prefer mechanisms in this order — each one is more deterministic than the next:

1. **Unity Catalog metadata** (table/column descriptions, PK/FK) — applies everywhere, not just this space.
2. **SQL Functions** — encode metrics and business definitions as reusable, testable UDFs.
3. **Parameterized Example SQL** — canonical answers for high-traffic question shapes.
4. **General Instructions** — natural-language guidance for things SQL can't express (clarification, summary style, refusals).
5. **Synonyms / Knowledge Store** — last resort for terminology mapping that nothing above resolved.

**Rule of thumb:** if you can write the rule as SQL, do — text is interpreted by an LLM and will be applied inconsistently in long conversations.

(Source: Databricks blog *From Data to Dialogue*; reinforced by Uttamchandani, *The Self-Service Data Roadmap*, O'Reilly — semantic layer principles.)

## 2. Schema metadata in Unity Catalog

Genie reads table descriptions and column comments directly. These propagate across every space and dashboard, so invest here first.

**Tables.** A good `COMMENT` answers: *what is one row?*, *grain?*, *update cadence?*, *known caveats?*

```sql
COMMENT ON TABLE sales.fact_opportunity IS
  'One row per Salesforce opportunity at its current state.
   Grain: opportunity_id (unique). Refreshed hourly via Fivetran CDC.
   Excludes test_account = TRUE rows. Closed-Won amounts in USD as of close_date.';
```

**Columns.** Comment every column the user might reference by name. Distinguish synonyms from the canonical metric:

```sql
COMMENT ON COLUMN sales.fact_opportunity.amount_usd IS
  'Net opportunity amount in USD. Synonyms: revenue, deal size, ACV.
   Excludes one-time services. Use this column for any "revenue" question.';
```

**Anti-pattern.** AI-generated descriptions accepted without verification. The button is convenient — read every line before saving.

## 3. JOIN configuration

In 2026 Genie auto-creates JOIN relationships from primary keys and foreign keys declared in source tables. So:

- **Declare PK/FK on every join column in Unity Catalog.** This is the highest-leverage one-time fix.
- After adding tables to the space, open the **Joins** panel. Review every inferred join.
- Reject ambiguous ones (two tables share a `region_id` column with different domains? Either rename or hand-write the join).
- For many-to-many, define a bridge view in Unity Catalog and reference *that* — don't expect Genie to invent the bridge.

```sql
ALTER TABLE sales.fact_opportunity
  ADD CONSTRAINT pk_opportunity PRIMARY KEY (opportunity_id);

ALTER TABLE sales.fact_opportunity
  ADD CONSTRAINT fk_account FOREIGN KEY (account_id)
  REFERENCES sales.dim_account(account_id);
```

## 4. General Instructions — structure and style

Use four sections, in this order. Markdown is supported.

```markdown
## Scope

This space answers questions about EMEA new-business pipeline and forecast.
Questions about renewals, services revenue, or partner deals are out of scope —
direct the user to the "EMEA Renewals" or "Services GTM" spaces.

## Clarification

If the user asks about "revenue" without a time qualifier, ask whether they mean
quarter-to-date, last completed quarter, or trailing twelve months.

If a region is ambiguous (e.g., "DACH"), ask which countries they want included;
default to DE, AT, CH if they decline.

## Metric definitions

- **Pipeline coverage** = open pipeline closing in the quarter ÷ remaining quota.
  Use SQL Function `analytics.pipeline_coverage(p_region, p_quarter)`.
- **Net new ARR** = `amount_usd` for opportunities with `stage = 'Closed Won'`
  and `is_renewal = FALSE`. Use SQL Function `analytics.net_new_arr(...)`.

## Summary style

Reply with a single sentence headline, then the table.
Round currency to nearest thousand with the suffix "K USD".
Always cite the as-of timestamp.
```

**Style rules:**

- One concrete instruction per line. Bulleted, not paragraphed.
- Specify *trigger conditions* + *expected behaviour*. Not "ask for clarification when needed" — that does nothing. Instead: "When the user mentions 'top customers' without a metric, ask: by ARR, by logo count, or by gross margin?"
- Don't put metric formulas here if a SQL Function exists — link to it instead. Two sources of truth diverge.
- Keep the whole block under ~80 lines. Past that, conversational adherence drops.

## 5. Example SQL Queries (parameterized)

Example SQL teaches Genie how *you* answer common question shapes. Parameterize the variable parts so the same example covers many user phrasings.

```sql
-- Title: Net new ARR by quarter for a region
-- Question this answers: "Show me net new ARR for EMEA in 2026"
-- Parameters: :region (string), :year (int)

SELECT
  DATE_TRUNC('quarter', close_date) AS quarter,
  SUM(amount_usd)                   AS net_new_arr_usd
FROM sales.fact_opportunity o
JOIN sales.dim_account a USING (account_id)
WHERE o.stage = 'Closed Won'
  AND o.is_renewal = FALSE
  AND a.region = :region
  AND YEAR(o.close_date) = :year
GROUP BY 1
ORDER BY 1;
```

**Curation rules:**

- Parameterize anything the user might vary. A parameterized example covers an entire family of questions; a hard-coded one covers exactly one.
- Title and the "Question this answers" line drive matching — write them in user voice, not query voice.
- Keep examples *minimal* — only the joins, filters, and projections needed. Extra columns degrade matching.
- Cover the dominant question *shapes*, not specific questions. 8–15 well-chosen examples beat 50 redundant ones.

## 6. SQL Functions

A SQL Function is a Unity Catalog UDF — the strongest curation primitive because it's testable, versioned, and reused outside Genie too.

```sql
CREATE OR REPLACE FUNCTION analytics.net_new_arr(p_region STRING, p_year INT)
RETURNS TABLE (quarter DATE, arr_usd DECIMAL(18,2))
COMMENT 'Net new ARR by quarter for a region/year. Excludes renewals and test accounts.'
RETURN
  SELECT
    CAST(DATE_TRUNC('quarter', o.close_date) AS DATE),
    SUM(o.amount_usd)
  FROM sales.fact_opportunity o
  JOIN sales.dim_account a USING (account_id)
  WHERE o.stage = 'Closed Won'
    AND o.is_renewal = FALSE
    AND a.region = p_region
    AND YEAR(o.close_date) = p_year
    AND a.is_test = FALSE
  GROUP BY 1;
```

**When to promote an Example SQL to a SQL Function:**

- The metric is referenced in two or more example queries.
- The definition is policy-governed (must match Finance's ledger, must align with the metric view).
- A wrong number would be a credibility incident.

## 7. Trusted Assets — earning the badge

Genie marks an answer **Trusted** when its generated SQL is the exact text of a parameterized Example SQL or a SQL Function. The badge is an explicit accuracy signal users learn to look for.

Coverage strategy:

1. List the top 20 questions from the Monitoring tab.
2. For each, ensure either a parameterized Example SQL or a SQL Function exists.
3. Track the Trusted-rate weekly. **Target ≥ 60% of all answers Trusted; ≥ 90% of top-20-question answers Trusted.**
4. When a question's SQL is generated freely, it's a candidate for the next Example SQL.

(Source: Databricks docs — *Trusted Assets*; AI/BI release notes 2026.)

## 8. Knowledge Store and synonyms

Use these only for things 1–4 didn't cover.

- **Column synonyms** map alternate user terms to canonical columns: `revenue, ACV, deal size → amount_usd`. Scope is space-local.
- **Glossary entries** define business terms users assume Genie knows: *"Logo": a unique customer account, equivalent to `account_id`. We do not double-count parents and subsidiaries.*
- **Prompt-matching aids** in the Knowledge Store help map common phrasings to the right Example SQL.

Do not encode metric formulas here — they belong in SQL Functions.

## 9. Curation feedback loop

The Monitoring tab tells you exactly what to curate next. Treat the loop as a recurring engineering task, not adhoc maintenance.

1. **Each week**, sort the Monitoring tab by thumbs-down + "Fix it" + Quality-Review-flagged.
2. For each flagged answer:
   - If the SQL was wrong → add or repair an Example SQL / SQL Function.
   - If the metric was misunderstood → tighten the column comment or add a synonym.
   - If the question was out of scope → tighten General Instructions' Scope section to refuse it explicitly.
3. **Add the original question to the benchmark set** with the now-correct expected SQL.
4. Re-run the benchmarks. Diff the pass rate. Only then ship the curation change.
5. Reply to the user (or the Quality Review thread) confirming the fix.

The loop is the moat. A space that runs this loop weekly is structurally better in three months than a space that didn't.
