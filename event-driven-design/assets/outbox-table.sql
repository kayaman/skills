-- Transactional Outbox — reference DDL
--
-- Write this table in the same schema / database as the service's business tables.
-- Insert a row within the same local transaction that mutates business state;
-- a relay process (in-service poller, Debezium, or the DB's logical decoding)
-- reads unpublished rows and forwards them to the broker.
--
-- See PATTERNS.md §3 for the full recipe.
-- Vendor examples: PostgreSQL below. MySQL / SQL Server equivalents: replace
-- JSONB with JSON and TIMESTAMPTZ with TIMESTAMP(6) + server-side UTC conversion.

CREATE TABLE outbox (
  id              UUID        PRIMARY KEY,                -- event.id (UUIDv7/ULID)
  aggregate       TEXT        NOT NULL,                   -- e.g., 'Order'
  aggregate_id    TEXT        NOT NULL,                   -- partition key for the downstream topic
  type            TEXT        NOT NULL,                   -- event.type (e.g., 'OrderPaid')
  version         INT         NOT NULL,                   -- schema version
  topic           TEXT        NOT NULL,                   -- where the relay should publish
  headers         JSONB       NOT NULL,                   -- source, occurredAt, causationId, correlationId, metadata
  payload         JSONB       NOT NULL,                   -- event.data
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at    TIMESTAMPTZ                             -- NULL until relay has forwarded to the broker
);

-- Index for the relay's "find unpublished" query. Partial index keeps it small.
CREATE INDEX outbox_unpublished_idx
  ON outbox (created_at)
  WHERE published_at IS NULL;

-- Secondary index for observability / investigations (optional).
CREATE INDEX outbox_correlation_idx
  ON outbox ((headers ->> 'correlationId'));

-- Retention: after publish, keep rows for a period (e.g., 7 days) to aid debugging and
-- idempotent republish on consumer request. Then delete or archive.
-- Example cleanup query (run from a scheduled job):
--   DELETE FROM outbox WHERE published_at < now() - INTERVAL '7 days';

-- Relay pseudocode:
--
--   BEGIN;
--     SELECT id, topic, headers, payload
--       FROM outbox
--      WHERE published_at IS NULL
--      ORDER BY created_at
--      LIMIT 100
--     FOR UPDATE SKIP LOCKED;            -- multiple relay instances safely share work
--   -- publish each row to the broker (with retries) --
--   UPDATE outbox SET published_at = now() WHERE id = ANY($1);
--   COMMIT;
--
-- Note: the relay may publish-then-crash-before-update. That is fine.
-- Consumers dedupe on event.id (PATTERNS.md §4).
