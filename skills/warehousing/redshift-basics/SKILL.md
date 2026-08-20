---
name: redshift-basics
metadata:
  category: Warehousing
description: >-
  Provisions clusters, designs distribution styles, and runs analytics on
  Amazon Redshift: cluster config, schema design, and loading. Use when
  operating Redshift for data platforms. Don't use for cross-engine tuning
  (use warehouse-optimization) or other warehouses (use bigquery-basics or
  snowflake-basics).
allowed-tools:
  - aws
  - psql
  - python
---

# Amazon Redshift Basics

Redshift is AWS's petabyte-scale warehouse built on columnar storage with
MPP distribution. Design decisions (distribution, sort keys) are made at
table creation — this skill covers them.

## Prerequisites

- AWS account with Redshift permissions per the auth skill.
- A provisioned cluster or Serverless workgroup; `psql` or the Redshift
  query editor for SQL access.
- IAM role attached to the cluster for S3 loads.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `SELECT`, `SVV_TABLE_INFO`, `STL_*` system views,
  `EXPLAIN`.
- **Tier M (mutation)**: DDL/DML writes, `CREATE TABLE`, `COPY`/`UNLOAD`,
  and cluster resize. Resizing a provisioned cluster pauses the cluster —
  confirm with the window.

## Workflow

### 1. Inspect the Cluster

```bash
aws redshift describe-clusters --cluster-identifier {cluster} \
  --query "Clusters[0].{NodeType,NumberOfNodes,NodeType,Status:ClusterStatus}"
```

```sql
SELECT * FROM svv_table_info ORDER BY size DESC LIMIT 10;
SELECT COUNT(*) FROM stl_query WHERE starttime > now() - interval '1 day';
```

### 2. Design Tables (The Critical Step)

```sql
CREATE TABLE analytics.orders (
    order_id    VARCHAR(64)  ENCODE zstd,
    customer_id VARCHAR(64)  DISTKEY,
    amount      DECIMAL(12,2),
    event_date  DATE         SORTKEY
)
DISTSTYLE KEY
SORTKEY (event_date);
```

Rules:

- **DISTKEY**: the column used in the most frequent joins/grouping — joins
  on the distkey are local (no data movement).
- **SORTKEY**: the most-filtered column; enables zone maps + merge joins.
- **ENCODE**: zstd for text/numeric; raw/az64 for dates/IDs as appropriate.
- Never default `DISTSTYLE EVEN` for large fact tables with joins.

### 3. Load Data from S3

```sql
COPY analytics.orders
FROM 's3://{bucket}/orders/'
IAM_ROLE 'arn:aws:iam::{account}:role/{redshift-role}'
FORMAT AS PARQUET
STATUPDATE ON;
```

Rules:

- Load via S3 + `COPY` (fastest); never row-by-row inserts.
- `STATUPDATE ON` refreshes statistics (the default for new tables).
- Use `MAXERROR` to bound tolerated bad rows; review `STL_LOAD_ERRORS`.

### 4. Query and Diagnose

```sql
EXPLAIN SELECT customer_id, SUM(amount)
FROM analytics.orders
WHERE event_date >= '2024-01-01'
GROUP BY customer_id;
```

Check the plan for:

- `DS_DIST`/`DS_BCAST` (data distribution) — if present, the join keys are
  misaligned; review distkeys.
- `XN Seq Scan` on huge tables without pruning — review sortkeys.
- `XN Hash Aggregate` — check if a pre-aggregated table is warranted.

### 5. Maintain the Cluster

```sql
VACUUM FULL analytics.orders;   -- reclaim space + sort
ANALYZE analytics.orders;       -- refresh stats (or AUTOVACUUM/AUTOANALYZE)
```

Schedule: vacuum on sort-heavy tables after big loads; analyze after loads
when `STATUPDATE OFF` was used.

## Validation

- `EXPLAIN` shows no `DS_DIST` on the join query (distkeys aligned).
- Load counts match the source manifest; `STL_LOAD_ERRORS` empty.
- `SVV_TABLE_INFO` shows healthy distribution (each slice similar size).
- Vacuum/analyze ran per schedule; query times improved.

## Definition of Done

- Tables designed with explicit distkey/sortkey/encoding.
- Loads via S3 COPY with IAM role; counts verified.
- Query plans reviewed for distribution/scan issues.
- Maintenance scheduled; stats current.

## Reference Directory

- [Distribution & Sort Design](references/distribution-sort.md): diststyle
  matrix and sortkey mechanics.
- [System Views for Diagnostics](references/system-views.md): the views to
  query when diagnosing.

## Related Skills

- [Warehouse Optimization](../warehouse-optimization/SKILL.md): tuning
  beyond table design.
- [BigQuery Basics](../bigquery-basics/SKILL.md): the alternative
  warehouse.
- [dbt Core](../../transformation/dbt-core/SKILL.md): the transformation
  layer.