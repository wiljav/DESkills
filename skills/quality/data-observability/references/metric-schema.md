# Metric Schema

## Recommended monitoring schema

```sql
CREATE TABLE monitoring.metrics (
    table_name     STRING NOT NULL,      -- fully-qualified asset name
    measured_at    TIMESTAMP NOT NULL,
    metric         STRING NOT NULL,      -- row_count | max_loaded_at | null_rate_* | ...
    value          FLOAT,
    run_id         STRING                -- pipeline run id for correlation
)
PARTITION BY date(measured_at);
```

Long format is query-friendly: one row per metric per run.

## Retention

- Raw metrics: 90 days (trend baselining + incident replay).
- Downsampled daily aggregates: 400 days.
- Alert history: as long as the alerting system allows.

## Write pattern

- Appends only; idempotent per `(table_name, measured_at, metric, run_id)`.
- The monitor writes via the same auth/audit path as the pipeline (no
  bypass credentials).

## Recommended dashboards

- Freshness heatmap (table x last-loaded age).
- Volume trend (table x z-score bands).
- Alert count and MTTR weekly.
