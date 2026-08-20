# Incremental & Materialization Guide

## Incremental basics

```sql
{{
  config(
    materialized='incremental',
    unique_key='event_id',
    incremental_strategy='merge',
    on_schema_change='append_new_columns'
  )
}}

SELECT * FROM {{ source('raw', 'events') }}
{% if is_incremental() %}
WHERE event_time > (SELECT max(event_time) FROM {{ this }})
{% endif %}
```

Rules:

- `is_incremental()` gates the incremental predicate on the second run.
- `unique_key` + `merge` makes reruns idempotent (update/insert semantics).
- `on_schema_change` MUST be set explicitly; default is `ignore`, which
  silently drops new columns.

## Strategy by warehouse

| Warehouse | Supported strategies |
| --- | --- |
| BigQuery | `merge`, `insert_overwrite` (partition) |
| Snowflake | `merge`, `append`, `delete+insert`, `microbatch` (dbt 1.9+) |
| Redshift | `merge`, `append`, `delete+insert` |
| Postgres | `append`, `delete+insert` (merge not native) |

- `insert_overwrite` on BigQuery: partition by date so failed days can be
  rebuilt independently.
- `microbatch` (Snowflake, dbt 1.9+): event-time batching with idempotent
  per-batch rebuilds; prefer for time-windowed loads.

## Full refresh

`dbt run --full-refresh` drops and recreates the model's data:

- Confirm with the user; state the affected models and downstream consumers.
- Prefer rebuilding a single failed partition (`insert_overwrite`) over a
  full refresh when possible.
- After a full refresh, run the model's tests before downstream models run.