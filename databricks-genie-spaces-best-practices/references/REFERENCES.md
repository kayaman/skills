# References

Authoritative sources for this skill. Cite these (rather than this skill's prose) when answers need an external anchor.

## Databricks official documentation

- *What is a Genie Space* — Databricks AWS docs.
  `https://docs.databricks.com/aws/en/genie/`
- *Set up a Genie Space*. `https://docs.databricks.com/aws/en/genie/set-up`
- *Curate an effective Genie Space (best practices)*.
  `https://docs.databricks.com/aws/en/genie/best-practices`
- *Use the Genie Conversation API*. `https://docs.databricks.com/aws/en/genie/conversation-api`
- *Monitor a Genie Space*. `https://docs.databricks.com/aws/en/genie/monitor`
- *Trusted Assets in Genie* — release notes 2025–2026.
  `https://docs.databricks.com/aws/en/ai-bi/release-notes/2026`
- *Unity Catalog row filters and column masks*.
  `https://docs.databricks.com/aws/en/tables/row-and-column-filters`
- Databricks blog: *From Data to Dialogue: A Best Practices Guide for Building High-Performing Genie Spaces*.
  `https://www.databricks.com/blog/data-dialogue-best-practices-guide-building-high-performing-genie-spaces`
- Databricks blog: *AI/BI Genie is now Generally Available*.
  `https://www.databricks.com/blog/aibi-genie-now-generally-available`
- Databricks blog: *The Next Generation of Databricks Genie*.
  `https://www.databricks.com/blog/next-generation-databricks-genie`
- Azure Databricks parallel docs (when on Azure):
  `https://learn.microsoft.com/en-us/azure/databricks/genie/`

## O'Reilly book references

These O'Reilly titles back up the engineering judgements in this skill. Cite chapters when the topic comes up.

| Topic | Book | Author(s) | Why |
|---|---|---|---|
| Lakehouse fundamentals, Delta, SQL warehouses | *Learning Spark, 2nd Edition* | Damji, Wenig, Das, Lee | Compute model behind Genie's execution; warehouse sizing intuition. |
| Delta Lake mechanics, Unity Catalog | *Delta Lake: The Definitive Guide* | Jaiswal, Lee | Tables Genie reads from; PK/FK, time travel, OPTIMIZE/ZORDER for query latency. |
| Day-to-day Delta operations | *Delta Lake: Up & Running* | Aslam, Tomasevicius, et al. | Practical operations on the data Genie queries. |
| Self-service analytics design | *The Self-Service Data Roadmap* | Uttamchandani | Curator-vs-consumer separation; semantic-layer thinking; success criteria. |
| Domain-aligned data products | *Data Mesh: Delivering Data-Driven Value at Scale* | Dehghani | One-space-per-domain; federated computational governance. |
| Data product engineering | *Fundamentals of Data Engineering* | Reis, Housley | Observability, audit, governance for analytical data products. |
| Authorization and trust boundaries | *Designing Data-Intensive Applications, 2nd Edition* | Kleppmann | Push authorisation to the lowest layer (Unity Catalog, not General Instructions). |
| Metrics layer thinking | *Building Data Products* | (various O'Reilly titles on semantic layers / metric stores) | Promoting metrics from inline SQL to SQL Functions / metric views. |
| LLM application patterns | *Generative AI on AWS* / *Designing Large Language Model Applications* | (O'Reilly) | Compound AI architecture context behind Genie; evaluation harness design. |

To pull a specific O'Reilly chapter as further evidence, request: *"From O'Reilly Books: <topic> in <book title>"* — examples include "Unity Catalog governance in Delta Lake: The Definitive Guide" or "Self-service curation roles in The Self-Service Data Roadmap".

## Specification adherence

- This skill follows the agent skill specification at `https://agentskills.io` — YAML frontmatter (`name`, `description`, optional `license`/`metadata`/`allowed-tools`), Markdown body under 200 lines, progressive disclosure via `references/`, bundled `assets/`.
- Authoring patterns reflect *Skill Authoring Patterns from Anthropic's Claude Skills* (generativeprogrammer.com): activation metadata with explicit triggers and exclusions, context budget, progressive disclosure, control tuning (high/medium/low freedom), explain-the-why, template scaffolds, in-skill examples, known gotchas, execution checklist, self-correcting loop, plan-validate-execute.
