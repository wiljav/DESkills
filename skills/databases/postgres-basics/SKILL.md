---
name: postgres-basics
metadata:
  category: Databases
description: >-
  Configures and tunes PostgreSQL for data-platform use: roles, indexes,
  partitioning, logical replication, and CDC integration. Use when running
  Postgres as a source or operational store. Don't use for warehouse design
  (use warehousing skills) or cloud-managed specifics beyond connection
  (vendor docs).
allowed-tools:
  - psql
  - python
---

# PostgreSQL Basics

PostgreSQL is the default transactional database in most platforms: the
source of operational data, the orchestrator metadata store, or a serving
store. This skill covers what a data engineer needs to run it well.

## Prerequisites

- A running PostgreSQL instance (local, RDS/Aurora, or GCP Cloud SQL).
- `psql` client; `pg_dump`/`pg_restore` for backup moves.
- Credentials with scoped roles per the auth skill.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `SELECT`, `EXPLAIN`, `\d+` inspections,
  `pg_stat_*` views.
- **Tier M (mutation)**: DDL/DML writes, index creation, logical
  replication setup, and partition management. Replication and partition
  changes affect production traffic — confirm before applying.

## Workflow

### 1. Inspect the Instance

```bash
psql "host={host} dbname={db} user={user}" -c "\l"
psql ... -c "\dt"
psql ... -c "SELECT version();"
```

### 2. Create Roles and Grants

```sql
CREATE ROLE de_readonly LOGIN PASSWORD '{pwd}';
GRANT CONNECT ON DATABASE analytics TO de_readonly;
GRANT USAGE ON SCHEMA public TO de_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO de_readonly;
```

Rules:

- Pipeline roles get the minimum: read roles for extraction, write roles
  scoped to schema.
- Never use `superuser` in pipeline code.

### 3. Index and Tune for Reads

```sql
CREATE INDEX idx_orders_customer ON orders (customer_id, event_date);
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders WHERE customer_id = 'C42';
```

Rules:

- Index the filter and join columns; composite indexes for multi-column
  filters (leftmost-prefix).
- `EXPLAIN (ANALYZE)` before/after to prove an index helps.
- Avoid index sprawl: each index costs writes.

### 4. Partition Large Tables

```sql
CREATE TABLE events (id bigint, ts timestamptz, payload jsonb)
PARTITION BY RANGE (ts);

CREATE TABLE events_2024_01 PARTITION OF events
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

Rules:

- Partition tables that exceed ~100 GB or are dominated by date-range
  access.
- Dropping an old partition is instant (vs DELETE) — the retention lever.

### 5. Enable CDC with Logical Replication

```sql
-- wal_level must be logical (restart required)
SHOW wal_level;

CREATE PUBLICATION de_pub FOR TABLE orders, customers;

-- on the subscriber (e.g. Kafka via Debezium)
```

Rules:

- Logical replication feeds Debezium/Kafka CDC (see kafka-connect) —
  publication per pipeline, slots per consumer.
- Monitor replication lag (`pg_replication_slots`); lag = stale streams.

### 6. Back Up and Restore

```bash
pg_dump -h {host} -U {user} -d analytics -Fc -f analytics.dump
pg_restore -h {host} -U {user} -d analytics --clean analytics.dump
```

- Schedule `pg_dump` (or managed backups); test restore quarterly.

## Validation

- `EXPLAIN (ANALYZE)` shows index usage on hot queries; scans dropped.
- Partitions prune (`EXPLAIN` shows only the relevant partition).
- Replication slot lag < threshold; CDC events flowing.
- Restore test succeeds from the latest dump.

## Definition of Done

- Roles scoped and documented; no superuser in code.
- Indexes proven with EXPLAIN; partition plan applied where needed.
- CDC (logical replication) configured and lag-monitored.
- Backup + quarterly restore test in place.

## Reference Directory

- [Indexing & EXPLAIN](references/indexing-explain.md): reading plans and
  choosing indexes.
- [Replication & CDC](references/replication-cdc.md): logical replication
  details and Debezium wiring.

## Related Skills

- [Kafka Connect](../../ingestion/kafka-connect/SKILL.md): consuming the
  CDC stream.
- [Airflow Basics](../../orchestration/airflow-basics/SKILL.md): Postgres
  as Airflow's metadata store.
- [dbt Core](../../transformation/dbt-core/SKILL.md): analytics on
  Postgres.