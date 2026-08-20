---
name: bigquery-basics
metadata:
  category: Warehousing
description: >-
  Manages datasets, tables, and jobs in BigQuery: DDL/DML, loading data,
  query optimization patterns, and cost controls. Use when interacting with
  BigQuery for pipelines or analysis. Don't use for cross-engine warehouse
  tuning (use warehouse-optimization) or BigQuery-specific AI/ML (see the
  data platform solution skills).
allowed-tools:
  - bq
  - gcloud
  - python
---

# BigQuery Basics

BigQuery is a serverless, disaggregated warehouse: storage and compute scale
independently, and you pay for query bytes scanned.

## Prerequisites

- A GCP project with BigQuery enabled; credentials per the auth skill.
- `bq` CLI or `google-cloud-bigquery` Python client.
- IAM roles scoped to the dataset(s) the work touches (read-only first).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `SELECT`, `bq show`, `bq ls`, `EXPLAIN`-style
  dry runs (`bq query --dry_run`), `INFORMATION_SCHEMA` queries.
- **Tier M (mutation)**: DDL/DML that writes (`CREATE`, `INSERT`, `MERGE`,
  `DELETE`, `DROP`), loading data, and dataset/table creation. `DROP` and
  truncation are irreversible — confirm with the blast radius stated.

## Workflow

### 1. Inspect the Environment

```bash
bq ls --project_id {project}
bq show {project}:{dataset}.{table}
bq query --dry_run --use_legacy_sql=false "SELECT * FROM \`{project}.{dataset}.{table}\`"
```

The dry run reports bytes scanned BEFORE paying for the real query.

### 2. Create Datasets and Tables

```bash
bq mk --dataset --location=US {project}:{dataset}
bq mk --table --schema order_id:STRING,amount:NUMERIC,event_date:DATE \
  --time_partitioning_field event_date --clustering_fields customer_id \
  {project}:{dataset}.orders
```

Rules:

- Partition every large table by date (`--time_partitioning_field`).
- Cluster on the join/filter columns used together (`--clustering_fields`,
  max 4).
- Use partitioned + clustered tables for ALL analytics tables — costs drop
  by orders of magnitude (see warehouse-optimization).

### 3. Load Data

```bash
bq load --source_format=PARQUET \
  --autodetect {project}:{dataset}.orders \
  gs://{bucket}/orders/*.parquet
```

Rules:

- Prefer Parquet over CSV/JSON (columnar, typed, faster).
- For repeated loads, use partition decorators
  (`table$20240101`) or `MERGE` for upserts; see load patterns in
  file-ingestion-gcs-s3.

### 4. Query Effectively

```sql
SELECT customer_id, SUM(amount) AS total
FROM `{project}.{dataset}.orders`
WHERE event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY customer_id;
```

Rules:

- Filter on the partition column — scans only relevant partitions.
- Avoid `SELECT *`; select only needed columns (columnar pricing).
- Use `EXPLAIN`/dry runs to check estimated bytes before big queries.

### 5. Check Costs and Slots

```bash
bq query --use_legacy_sql=false \
  "SELECT job_id, total_bytes_processed, total_slot_ms FROM \`region-us\`.INFORMATION_SCHEMA.JOBS_BY_PROJECT WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)"
```

- Identify top-byte consumers; review whether their scans are justified.
- If the org is on capacity pricing (slots), watch `total_slot_ms` for
  contention.

## Validation

- Dry run bytes within the expected order of magnitude before executing.
- Partition pruning works: query with a partition filter scans only the
  window (`INFORMATION_SCHEMA.PARTITIONS` / query stats confirm).
- Loads verified: row counts match, schema types correct
  (`bq show` on the table).
- No `SELECT *` on big tables; no unbounded scans.

## Definition of Done

- Datasets/tables created with partitioning + clustering where appropriate.
- Loads performed with the right format; counts verified.
- Queries use partition filters; dry-run discipline applied.
- Cost-check query run; anomalous consumers identified or ruled out.

## Reference Directory

- [Cost Control](references/cost.md): byte-pricing levers, slots, and
  reservation basics.
- [Query Patterns](references/query-patterns.md): windows, joins, and
  array/struct handling.

## Related Skills

- [Warehouse Optimization](../warehouse-optimization/SKILL.md): tuning
  beyond the basics.
- [Snowflake Basics](../snowflake-basics/SKILL.md): the multi-cloud
  alternative.
- [dbt Core](../../transformation/dbt-core/SKILL.md): transformation layer
  on BigQuery.