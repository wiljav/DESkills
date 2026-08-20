# Data Loading

## COPY INTO variants

| Source | Statement |
| --- | --- |
| S3 stage | `COPY INTO t FROM @stage FILE_FORMAT=(TYPE=PARQUET)` |
| GCS stage | same, stage URL `gcs://...` with integration |
| Snowflake-managed internal stage | `COPY INTO t FROM @~/files` (user stage) |
| Streams (near-real-time) | `COPY INTO t FROM STREAM` via pipes |

## Idempotency

- COPY tracks loaded files per target table — re-running loads nothing new.
- Force reload: `FORCE = TRUE` (reloads files; use only after a validated
  fix, e.g. schema correction).

## Semi-structured data

```sql
COPY INTO t (id, payload, ts)
FROM @stage
FILE_FORMAT = (TYPE = JSON)
ON_ERROR = SKIP_FILE;

SELECT payload:customer_id::STRING AS customer_id,
       payload:amount::NUMBER AS amount
FROM t;
```

- JSON lands as VARIANT; extract + cast at query time.
- Prefer flattening to columns in transformation (dbt) over heavy
  query-time parsing.

## Error handling

- `ON_ERROR = SKIP_FILE` + count reconciliation.
- `REJECTED_RECORD_ACCOUNT` returns the skip count for verification.
- Load errors land in the target table's `COPY_HISTORY`; check
  `REJECTED_RECORDS` there before declaring success.