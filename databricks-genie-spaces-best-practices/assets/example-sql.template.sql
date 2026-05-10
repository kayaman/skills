-- ============================================================================
-- Title:               <One-line title in user voice>
-- Question this answers: "<Verbatim sample user question>"
-- Parameters:          :<param_1> (<type>), :<param_2> (<type>), ...
-- Trusted asset?       <yes / no — yes when this is the canonical answer>
-- Last reviewed:       <YYYY-MM-DD by @owner>
-- ============================================================================
--
-- Curation rules embodied in this template:
--   1. Title and "Question this answers" drive matching — write in user voice.
--   2. Parameterize anything the user might vary; do not hard-code dates,
--      regions, or limits.
--   3. Project only the columns the answer needs — extras degrade matching.
--   4. Reference SQL Functions for metrics that appear in more than one example.
--   5. Filter out test/sandbox rows in the source view, not here.
--
-- Replace the body below with the canonical query for one question shape.
-- ============================================================================

SELECT
  /* projection — only what the user needs */
  <expr_1>,
  <expr_2>
FROM <catalog>.<schema>.<fact_or_view>  AS f
JOIN <catalog>.<schema>.<dim>           AS d  USING (<key>)
WHERE 1 = 1
  AND f.<filter_col> = :<param_1>
  AND f.<date_col>  BETWEEN :<param_start> AND :<param_end>
GROUP BY <expr_1>
ORDER BY <expr_1>
LIMIT :<limit>;
