---
name: warehouse-optimization
metadata:
  category: Warehousing
description: >-
  Reduces warehouse cost and improves query performance with partitioning,
  clustering, materialization, and workload analysis across BigQuery,
  Snowflake, and Redshift. Use when warehouse queries are slow or expensive.
  Don't use for writing new SQL (use sql-transformation-best-practices) or
  for engine-specific setup (use bigquery-basics, snowflake-basics, or
  redshift-basics).
allowed-tools:
  - bq
  - snowsql
  - aws
  - python
---

# Warehouse Optimization

This skill is the cross-engine playbook for warehouse performance and cost:
find the expensive/slow queries, apply the right lever, verify the change.

## Prerequisites

- Access to the warehouse's query history
  (BigQuery `INFORMATION_SCHEMA.JOBS`, Snowflake `QUERY_HISTORY`, Redshift
  `STL_QUERY`).
- Baseline measurements: top queries by cost and by duration.
- Permissions to read the target tables' metadata (sizes, partitions).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: query-history reads, `EXPLAIN`, dry runs, size
  checks.
- **Tier M (mutation)**: schema changes (partitioning, clustering), creating
  materialized tables/views, and warehouse sizing changes. Each change MUST
  be confirmed and reverted if it does not improve the baseline metric.

## Workflow

### 1. Baseline the Workload

Identify the pain:

```sql
-- BigQuery: top bytes
SELECT query, total_bytes_processed, total_slot_ms
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY total_bytes_processed DESC LIMIT 20;
```

Record per query: bytes/slots (BigQuery), credits + runtime (Snowflake),
runtime + slices (Redshift). Rank: cost top-20 and runtime top-20.

### 2. Apply the Lever Order

For each hot query, apply levers in this order:

1. **Partition pruning** — filter on the partition column; verify the scan
   shrank (`EXPLAIN`/dry-run before vs after).
2. **Column pruning** — drop unused columns from the SELECT.
3. **Clustering/sort keys** — align with the query's filter columns.
4. **Materialization** — summarize hot patterns into tables/views
   (marts or `MATERIALIZED VIEW`).
5. **Join order & keys** — dedupe keys, align distkeys (Redshift), use
   broadcast hints where the engine supports them.

### 3. Materialize with Discipline

```sql
-- BigQuery / Snowflake
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_sales AS
SELECT event_date, SUM(amount) AS total FROM orders GROUP BY event_date;
```

Rules:

- Materialize only patterns with proven repetition (3+ occurrences in the
  baseline).
- Keep materializations minimal: each one is another thing to refresh and
  maintain.
- Track refresh freshness per the data-observability framework.

### 4. Size Compute to the Workload

- Snowflake: scale the warehouse only when `QUEUE` waits appear; prefer
  multi-cluster for concurrency (see snowflake-basics).
- BigQuery: slot contention check via `state='PENDING'`; buy/reshape
  reservations only with measured need.
- Redshift: resize or move hot tables to `ALL`/better distkeys first.

### 5. Verify and Keep the Wins

| Metric | Before | After | Delta |
| --- | --- | --- | --- |
| Bytes scanned (BQ) | | | |
| Runtime (all) | | | |
| Credits/slots consumed | | | |
| Queue wait | | | |

Keep only changes with measured improvement; document in the warehouse's
runbook. Re-run the baseline monthly.

## Validation

- Top-20 hot queries improved (bytes/runtime) or justified as unavoidable.
- No change shipped without a before/after measurement.
- Materializations are fresh and correct (counts match recompute).
- No warehouse sizing change persisted without a contention signal.

## Definition of Done

- Baseline recorded (cost + runtime top-20).
- Lever order applied; each change measured.
- Materializations justified and monitored.
- Compute sized to measured need.
- Wins documented; monthly re-baseline scheduled.

## Reference Directory

- [Engine-Specific Levers](references/engine-levers.md): what maps where
  per warehouse.
- [Cost Anatomy](references/cost-anatomy.md): how each engine charges and
  the corresponding lever.

## Related Skills

- [BigQuery Basics](../bigquery-basics/SKILL.md) /
  [Snowflake Basics](../snowflake-basics/SKILL.md) /
  [Redshift Basics](../redshift-basics/SKILL.md): engine setup context.
- [SQL Transformation Best Practices](../../transformation/sql-transformation-best-practices/SKILL.md):
  the SQL-side rules.
- [Data Observability](../../quality/data-observability/SKILL.md): watching
  the metrics this skill improves.
