# Governance for Genie Spaces

Genie inherits Unity Catalog's authorization model. The space is not a new ACL surface — it is a delivery surface. Get the catalog right, and the space behaves correctly by construction.

## Contents

1. The trust boundary
2. Permission levels (recap)
3. Row filters and column masks
4. Embedded warehouse credentials — implications
5. PII and sensitive data
6. Multi-tenant and cross-region patterns
7. Audit and traceability
8. Sharing decisions

---

## 1. The trust boundary

Two layers:

- **Unity Catalog** — *what data the user is allowed to see*. Per-user, per-row, per-column. This is the authoritative authorization layer.
- **Genie Space ACLs** — *whether the user can use this particular space at all*. Coarse-grained. Doesn't grant data access by itself.

A user with `CAN RUN` on the space but no `SELECT` on the underlying table sees no data — Genie surfaces a clear authorization error. Conversely, granting `SELECT` does not grant space access.

**Implication.** Never use General Instructions or Example SQL as the access-control mechanism ("Don't show salary to non-managers"). Users phrase around prose. Apply column masks in Unity Catalog instead.

(Reinforced by Kleppmann, *Designing Data-Intensive Applications, 2e*, O'Reilly — push authorization to the lowest possible layer.)

## 2. Permission levels (recap)

| Level | Curate | Share | Ask | View prior |
|---|---|---|---|---|
| `CAN MANAGE` | ✓ | ✓ | ✓ | ✓ |
| `CAN EDIT` | ✓ | ✗ | ✓ | ✓ |
| `CAN RUN` | ✗ | ✗ | ✓ | ✓ |
| `CAN VIEW` | ✗ | ✗ | ✗ | ✓ |

Pattern: assign by group, not by user. Map the data-product domain group (e.g., `revops-emea`) to `CAN RUN` and a small curator group to `CAN EDIT`.

## 3. Row filters and column masks

Both are Unity Catalog features, both apply transparently to Genie.

**Row filter** — narrows the rows a user sees per query.

```sql
CREATE FUNCTION sales.opportunity_region_filter(p_region STRING)
RETURNS BOOLEAN
RETURN p_region IN (
  SELECT region FROM access.user_region_grants
  WHERE user_email = current_user()
);

ALTER TABLE sales.fact_opportunity
  SET ROW FILTER sales.opportunity_region_filter ON (region);
```

**Column mask** — replaces a sensitive column's value per query.

```sql
CREATE FUNCTION pii.mask_email(email STRING)
RETURNS STRING
RETURN CASE
  WHEN is_account_group_member('pii_readers') THEN email
  ELSE 'REDACTED'
END;

ALTER TABLE crm.dim_contact
  ALTER COLUMN email SET MASK pii.mask_email;
```

Genie sees the same view of the data the user would see in a SQL editor. No special configuration needed in the space. If a user complains "I see different numbers from my colleague", it's almost certainly a row filter — not a Genie bug.

## 4. Embedded warehouse credentials — implications

The warehouse credentials configured on the space are used to **execute** generated SQL, but Unity Catalog **authorisation is per-end-user**. So:

- End users do not need their own warehouse access — they piggyback on the space's embedded credentials.
- Per-user data filtering still happens because Unity Catalog evaluates ACLs against the **caller's identity**, not the warehouse's.
- Cost is attributed to the warehouse the space points at — not to the calling user. Plan FinOps accordingly: tag the warehouse with the data-product owner, not "Genie".

Don't try to use a personal access token in the warehouse to "lock down" execution — that breaks the per-user authorisation story.

## 5. PII and sensitive data

If the source tables contain PII or otherwise sensitive columns:

1. **Tag** the columns in Unity Catalog (`pii`, `phi`, `confidential` — your standard tagging vocabulary).
2. **Mask** them with column masks tied to a privileged group; default to redacted.
3. **Decide the space's posture** explicitly:
   - *Sensitive-allowed* — only members of the privileged group get `CAN RUN`. Others see the redacted view if at all.
   - *Sensitive-excluded* — exclude the sensitive columns from the space's table list entirely; build a sanitised view and reference *that*.
4. **Note in the space Description** which posture this space adopts so consumers don't expect data they're not getting.

Never include PII in Example SQL, General Instructions, or Common Questions — those are visible to anyone with `CAN VIEW`.

## 6. Multi-tenant and cross-region patterns

For SaaS multi-tenant scenarios where each tenant should only see their own data:

- Use a single space backed by tables with a `tenant_id` row filter keyed to `current_user()`'s mapping.
- Embed the space behind your authenticated SaaS surface using **OAuth U2M** (so the user identity reaches Unity Catalog).
- Never rely on M2M auth + "we'll add the tenant filter in the prompt" — that's a critical security defect in the making.

For cross-region/data-residency:

- Use a separate workspace per region with its own Unity Catalog metastore.
- Replicate space *configuration* (clone) but *not* data across regions.
- Tag the space's region in the Description and Tags.

## 7. Audit and traceability

Every Genie interaction emits audit events. Wire them into your standard audit pipeline:

- Who asked → user identity from the OAuth token.
- What was asked → message content (be aware: this is logged; treat questions themselves as potentially sensitive in your log retention policy).
- What was returned → generated SQL + Trusted-asset reference + result row count.
- Where it ran → warehouse + correlation_id.

For incident response, the `correlation_id` ties Genie audit events to the warehouse query history and to your application's request id. Make sure your wrapper API logs it.

## 8. Sharing decisions

A short flowchart for "who should this be shared with?":

```
Is the space scope tied to one domain?
├─ No → split into per-domain spaces first; revisit
└─ Yes
   │
   Are row filters / column masks in place for sensitive data?
   ├─ No → fix Unity Catalog first; do not share yet
   └─ Yes
      │
      Has it run a benchmark with ≥ 95% pass and ≥ 60% Trusted?
      ├─ No → pilot with ≤ 20 named users at CAN RUN; iterate weekly
      └─ Yes → CAN RUN to the domain group; review monitoring weekly
```

(Sources: Databricks docs — *Securing Genie Spaces*, *Unity Catalog row filters and column masks*; Reis & Housley, *Fundamentals of Data Engineering*, O'Reilly — governance chapter; Dehghani, *Data Mesh*, O'Reilly — federated computational governance.)
