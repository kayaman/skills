# Worked Examples

Two end-to-end examples. Each shows the General Instructions block, two parameterized Example SQL queries, one SQL Function, three benchmark questions, and a Common Questions list — i.e., the minimum viable curation surface for a domain.

## Contents

1. Example 1 — EMEA Sales Pipeline (RevOps audience)
2. Example 2 — Industrial IoT Telemetry (Reliability audience)

---

## 1. Example 1 — EMEA Sales Pipeline

### Audience and scope

**Title:** EMEA Pipeline & Forecast — RevOps
**Description (Markdown):**

```markdown
Answers questions about **new-business pipeline and forecast for EMEA** for
the current and previous four quarters, sourced from Salesforce + finance
ledger reconciliation.

**In scope:** open pipeline, stage progression, win/loss, net new ARR, coverage.
**Out of scope:** renewals (see *EMEA Renewals*), services revenue (see *Services GTM*),
forecast beyond +1 quarter (see *Annual Plan*).
```

### Tables (≤ 30)

- `sales.fact_opportunity` — one row per opportunity (current state). Refreshed hourly.
- `sales.dim_account` — account dimension with region, industry, segment.
- `sales.dim_user` — sellers, managers, hierarchy.
- `sales.dim_stage` — stage definitions and ordering.
- `sales.fact_quota` — quarterly quota by user.
- View: `sales.v_pipeline_clean` — pre-joined, test accounts excluded, region normalised.

### Common Questions

1. What's our open EMEA pipeline closing this quarter?
2. Show me net new ARR by quarter for the last four quarters.
3. Top 10 accounts by ARR closed in 2026 Q1.
4. Pipeline coverage by manager.
5. Win rate this quarter vs last for EMEA mid-market.

### General Instructions

```markdown
## Scope

This space answers questions about EMEA new-business pipeline and forecast.
Refuse out-of-scope questions and direct the user to the correct space:
- Renewals → "EMEA Renewals"
- Services revenue → "Services GTM"
- > 1 quarter forecast → "Annual Plan"

## Clarification

If the user mentions "revenue" without a time qualifier, ask whether they mean:
QTD, last completed quarter, or trailing twelve months.

If "EMEA" is qualified by an ambiguous sub-region (e.g., "DACH"), default to
DE + AT + CH and note the assumption in the answer.

If "top accounts" is asked without a metric, ask: by closed ARR, open pipeline,
or logo count?

## Metric definitions

- **Net new ARR** — use `analytics.net_new_arr(region, year)`. Excludes renewals
  and test accounts.
- **Pipeline coverage** — open pipeline closing in the quarter ÷ remaining quota.
  Use `analytics.pipeline_coverage(region, quarter)`.
- **Win rate** — closed-won count ÷ (closed-won + closed-lost) for the period,
  excluding stages "Disqualified".

## Summary style

Lead with a one-sentence headline, then the table. Round currency to nearest
thousand with suffix " K USD". Always cite the as-of timestamp from the data.
```

### Example SQL #1 — Net new ARR by quarter for a region

```sql
-- Title: Net new ARR by quarter for a region
-- Question this answers: "Show me net new ARR for EMEA in 2026"
-- Parameters: :region (string), :year (int)

SELECT
  CAST(DATE_TRUNC('quarter', o.close_date) AS DATE) AS quarter,
  SUM(o.amount_usd)                                  AS net_new_arr_usd
FROM sales.v_pipeline_clean o
JOIN sales.dim_account a USING (account_id)
WHERE o.stage = 'Closed Won'
  AND o.is_renewal = FALSE
  AND a.region = :region
  AND YEAR(o.close_date) = :year
GROUP BY 1
ORDER BY 1;
```

### Example SQL #2 — Top accounts by closed ARR

```sql
-- Title: Top N accounts by closed ARR for a region/period
-- Question: "Top 10 accounts by ARR closed in 2026 Q1 for EMEA"
-- Parameters: :region, :start_date, :end_date, :limit

SELECT
  a.account_name,
  SUM(o.amount_usd) AS closed_arr_usd
FROM sales.v_pipeline_clean o
JOIN sales.dim_account a USING (account_id)
WHERE o.stage = 'Closed Won'
  AND o.is_renewal = FALSE
  AND a.region = :region
  AND o.close_date BETWEEN :start_date AND :end_date
GROUP BY a.account_name
ORDER BY closed_arr_usd DESC
LIMIT :limit;
```

### SQL Function — Pipeline coverage

```sql
CREATE OR REPLACE FUNCTION analytics.pipeline_coverage(p_region STRING, p_quarter DATE)
RETURNS DOUBLE
COMMENT 'Pipeline coverage = open pipeline closing in the quarter / remaining quota.'
RETURN (
  SELECT
    SUM(CASE WHEN o.stage NOT IN ('Closed Won','Closed Lost')
             AND CAST(DATE_TRUNC('quarter', o.close_date) AS DATE) = p_quarter
        THEN o.amount_usd ELSE 0 END)
    /
    NULLIF(
      (SELECT SUM(q.quota_usd - q.attainment_usd)
         FROM sales.fact_quota q
         JOIN sales.dim_user u USING (user_id)
        WHERE q.quarter = p_quarter AND u.region = p_region),
      0
    )
  FROM sales.v_pipeline_clean o
  JOIN sales.dim_account a USING (account_id)
  WHERE a.region = p_region
);
```

### Benchmark questions (subset)

| # | Question | Expected SQL ref | Expected result |
|---|---|---|---|
| 1 | Net new ARR for EMEA in 2026 | Example SQL #1 with `:region='EMEA'`, `:year=2026` | 4 quarterly rows |
| 2 | Top 10 EMEA accounts by ARR closed in 2026 Q1 | Example SQL #2 | 10 ordered rows |
| 3 | Pipeline coverage for DACH this quarter | Function `analytics.pipeline_coverage('EMEA', current_quarter())` filtered to DE+AT+CH | scalar 0–5x range |

---

## 2. Example 2 — Industrial IoT Telemetry

### Audience and scope

**Title:** Plant-Floor Telemetry — Reliability Engineering
**Description:**

```markdown
Answers questions about **machine telemetry, anomalies, and downtime** for
the European plants over the last 90 days.

**In scope:** signal aggregations, anomaly counts, downtime duration, MTTR/MTBF
rollups.
**Out of scope:** financial impact (see *OEE Finance*), maintenance schedules
(see *CMMS*).
```

### Tables

- `iot.bronze_signals` — raw 1Hz sensor stream (last 90 days hot, partitioned by `event_date`).
- `iot.silver_anomalies` — detected anomalies with severity and signal context.
- `iot.fact_downtime_event` — start/end of each downtime, with cause code.
- `iot.dim_machine` — machine hierarchy: plant → line → machine.
- `iot.dim_signal` — signal definitions and units.

### Common Questions

1. Top 5 machines by downtime hours last week.
2. Anomaly count per shift this month for Plant 3.
3. MTBF for line A in 2026 vs 2025.
4. Show temperature trend for machine M-217 yesterday.
5. Which signals correlated with the 2026-04-12 outage on Line B?

### General Instructions

```markdown
## Scope

Answers questions about plant-floor telemetry, anomalies, and downtime for the
last 90 days. Refuse:
- Financial impact questions → "OEE Finance"
- Maintenance scheduling → "CMMS"
- Queries earlier than 90 days ago — bronze data is hot for 90 days only.

## Clarification

If the user asks about "downtime" without specifying planned vs unplanned,
ask which they mean (default: unplanned, `cause_code != 'PLANNED'`).

If a machine is referenced by friendly name only ("the welding robot"), ask
which line, since names repeat across plants.

## Metric definitions

- **MTBF** = total operating hours / number of unplanned downtime events.
  Use `analytics.mtbf(line_id, period_start, period_end)`.
- **Downtime hours** = sum of (end_ts - start_ts) for `cause_code != 'PLANNED'`.
- **Severity** — Anomalies have severity 1 (low) to 5 (critical).
  Critical-only questions use `severity = 5`.

## Summary style

Lead with a one-sentence headline + range covered. Round duration to one decimal
hour. For trends, prefer line charts (provide one-row-per-time-bucket SQL).
```

### Example SQL #1 — Top N machines by downtime hours

```sql
-- Title: Top N machines by unplanned downtime hours over a period
-- Question: "Top 5 machines by downtime hours last week"
-- Parameters: :start_ts, :end_ts, :limit

SELECT
  m.machine_id,
  m.machine_name,
  ROUND(SUM(TIMESTAMPDIFF(SECOND, d.start_ts, d.end_ts)) / 3600.0, 1) AS downtime_hours
FROM iot.fact_downtime_event d
JOIN iot.dim_machine m USING (machine_id)
WHERE d.cause_code <> 'PLANNED'
  AND d.start_ts >= :start_ts
  AND d.end_ts   <= :end_ts
GROUP BY m.machine_id, m.machine_name
ORDER BY downtime_hours DESC
LIMIT :limit;
```

### Example SQL #2 — Anomaly count per shift

```sql
-- Title: Anomaly count per shift for a plant
-- Question: "Anomaly count per shift this month for Plant 3"
-- Parameters: :plant_id, :month_start, :month_end, :min_severity

SELECT
  CAST(a.event_ts AS DATE)                              AS day,
  CASE WHEN HOUR(a.event_ts) BETWEEN 6 AND 13 THEN 'A'
       WHEN HOUR(a.event_ts) BETWEEN 14 AND 21 THEN 'B'
       ELSE 'C' END                                      AS shift,
  COUNT(*)                                               AS anomaly_count
FROM iot.silver_anomalies a
JOIN iot.dim_machine m USING (machine_id)
WHERE m.plant_id = :plant_id
  AND a.event_ts BETWEEN :month_start AND :month_end
  AND a.severity >= :min_severity
GROUP BY 1, 2
ORDER BY 1, 2;
```

### SQL Function — MTBF

```sql
CREATE OR REPLACE FUNCTION analytics.mtbf(p_line_id STRING, p_start TIMESTAMP, p_end TIMESTAMP)
RETURNS DOUBLE
COMMENT 'Mean time between failures (hours) for a line over a period.'
RETURN (
  SELECT
    DATEDIFF(SECOND, p_start, p_end) / 3600.0
    /
    NULLIF((
      SELECT COUNT(*)
        FROM iot.fact_downtime_event d
        JOIN iot.dim_machine m USING (machine_id)
       WHERE m.line_id = p_line_id
         AND d.cause_code <> 'PLANNED'
         AND d.start_ts BETWEEN p_start AND p_end
    ), 0)
);
```

### Benchmark questions (subset)

| # | Question | Expected SQL ref | Expected result |
|---|---|---|---|
| 1 | Top 5 machines by downtime hours last week | Example SQL #1 with last-week range, `:limit=5` | 5 rows ordered |
| 2 | Critical anomaly count per shift this month for Plant 3 | Example SQL #2 with `:min_severity=5` | rows × 3 shifts × N days |
| 3 | MTBF for Line A in 2026 vs 2025 | Function `analytics.mtbf` × 2 calls | two scalars |

---

## How to use these as templates

1. Pick the example closer to your domain.
2. Copy `assets/general-instructions.template.md` and fill in the four sections.
3. Copy `assets/example-sql.template.sql` for each dominant question shape; parameterize it.
4. Promote the high-value metric to a SQL Function in Unity Catalog.
5. Build the benchmark CSV (`assets/benchmark.template.csv`) and let Genie auto-suggest more from the space context.
6. Pilot with the smallest realistic group; iterate weekly per `MONITORING.md`.

(Example domains compiled from common deployment patterns; reinforced with Reis & Housley, *Fundamentals of Data Engineering*, O'Reilly — analytical data product patterns; Uttamchandani, *The Self-Service Data Roadmap*, O'Reilly — domain-aligned curation.)
