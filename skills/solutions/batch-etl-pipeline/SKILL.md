---
name: batch-etl-pipeline
metadata:
  category: Solutions
description: >-
  Builds an end-to-end batch ETL pipeline from sources to analytics with
  ingestion, transformation, quality gates, and orchestration. Use when
  designing or assembling a new batch pipeline. Don't use for single-step
  tasks (use the relevant domain skill) or streaming (use
  streaming-analytics-pipeline).
allowed-tools:
  - python
  - sql
  - bash
---

# Batch ETL Pipeline

The reference recipe for batch pipelines: ingestion -> bronze -> silver ->
gold, orchestrated, tested, and observed. This is the assembly skill — it
composes the domain skills.

## Prerequisites

- The domain skills listed under Related Skills (ingestion, dbt, quality,
  observability, orchestration).
- Access to the source and target platforms per the auth skill.
- The data-contracts requirements for the dataset being built.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: dry runs, `EXPLAIN`, sampling sources, schema
  inspection.
- **Tier M (mutation)**: writing to the lakehouse/warehouse, DAG
  deployment, and backfills. Every write path must be idempotent; first
  production runs require confirmation per the data contracts.

## Workflow

### 1. Design the Flow

```
source (API/DB/files)
  -> ingestion: dlt / Airbyte / Spark (bronze, raw)
  -> transformation: dbt (silver, cleaned)
  -> modeling: dbt (gold, marts)
  -> quality gates at each hop
  -> orchestration: Airflow/Dagster scheduling + retries
  -> serving: warehouse tables + docs
```

Rules:

- Medallion naming: `bronze_*` raw, `silver_*` conformed, `gold_*`
  semantic.
- Each hop idempotent (partition-scoped overwrite or upsert).
- Contracts defined at the silver boundary (data-contracts).

### 2. Build Ingestion (Bronze)

```python
# dlt pipeline (per dlt-python-ingestion)
import dlt

pipeline = dlt.pipeline(
    pipeline_name="orders",
    destination="bigquery",
    dataset_name="bronze",
)
source = dlt.resource(orders_api_stream, name="orders")
pipeline.run(source, write_disposition="replace", table_name="orders")
```

Rules:

- Load raw as-is: no business logic at ingest (reprocessing freedom).
- Track source watermark (load timestamp, partition) for incremental
  reads.

### 3. Transform (Silver)

```sql
-- dbt model silver_orders.sql
SELECT
  order_id,
  customer_id,
  SAFE_CAST(amount AS DECIMAL(12,2)) AS amount,
  DATE(event_ts) AS event_date
FROM {{ source('bronze', 'orders') }}
WHERE event_ts IS NOT NULL
```

Rules:

- Casting + cleaning at silver; business semantics at gold.
- dbt tests at every model boundary (uniqueness, not-null — dbt tests &
  macros).

### 4. Model (Gold)

```sql
-- dbt model gold_daily_sales.sql
SELECT event_date, COUNT(*) AS orders, SUM(amount) AS revenue
FROM {{ ref('silver_orders') }}
GROUP BY event_date
```

- Gold models answer questions; name them for the question
  (`daily_sales`, `customer_lifetime`).

### 5. Add Quality Gates

- GE suite on silver: null rates, row-count deltas, freshness.
- dbt tests: uniqueness/relationships on keys.
- Volume alert: row count day-over-day outside `[0.95x, 1.05x]` -> page
  (data-observability).
- Fail fast: gate downstream on gate failure (`sensors`/`branching`).

### 6. Orchestrate

```python
# Airflow DAG skeleton
with DAG("orders_daily", schedule="@daily", catchup=True) as dag:
    ingest = DummyOperator(task_id="dlt_ingest")   # or dlt task
    transform = DummyOperator(task_id="dbt_run")
    test = DummyOperator(task_id="dbt_test")
    quality = DummyOperator(task_id="ge_suite")
    ingest >> transform >> [test, quality] >> notify
```

Rules:

- One DAG per dataset boundary; `catchup=True` + idempotency = backfill
  freedom.
- Retries on transient failures; alert on final failure.

### 7. Backfill and Rerun

- Backfill: re-run the DAG over the date range (`airflow dags backfill`).
- Rerun semantics: overwrite the affected partitions (idempotent models).
- Validate counts after backfill vs before (quality gate re-runs).

## Validation

- End-to-end run succeeds: bronze -> silver -> gold with tests green.
- Row counts: source sample == gold output for the test window.
- Freshness SLA met (gold loaded by the contracted time).
- Rerun of the same window produces identical gold output (idempotency
  proven).

## Definition of Done

- Pipeline live with ingestion, transformation, gold marts, and quality
  gates.
- Orchestration with retries + alerting; backfill path tested.
- Contracts published; observability dashboards live.

## Reference Directory

- [Layer Design](references/layers.md): medallion details and boundaries.
- [Idempotency Patterns](references/idempotency.md): the write patterns
  that make reruns safe.

## Related Skills

- [dlt Python Ingestion](../../ingestion/dlt-python-ingestion/SKILL.md):
  the ingest hop.
- [dbt Core](../../transformation/dbt-core/SKILL.md): the transform hop.
- [Airflow DAG Authoring](../../orchestration/airflow-dag-authoring/SKILL.md):
  the orchestration hop.
- [Data Observability](../../quality/data-observability/SKILL.md): the
  gates.
- [Data Contracts](../../governance/data-contracts/SKILL.md): the
  promises.