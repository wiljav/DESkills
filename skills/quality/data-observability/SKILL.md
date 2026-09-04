---
name: data-observability
metadata:
  category: DataQuality
description: >-
  Instruments data pipelines with continuous observability: freshness,
  volume, schema drift, distribution anomalies, and lineage-aware
  alerting. Use when moving from build-time checks to ongoing monitoring
  of production data. Don't use for one-off validation (use dbt tests or
  soda) or for responding to incidents (use data-quality-incident-runbook).
allowed-tools:
  - python
  - dbt
  - airflow
---

# Data Observability

Data observability monitors the "five pillars" — freshness, volume,
schema, distribution, and lineage — continuously, so anomalies are detected
before consumers are affected.

## Prerequisites

- The pipeline's quality gates exist (dbt tests / soda / GX) — observability
  builds on them, not instead of them.
- A metrics sink: warehouse table, Prometheus, or an observability vendor.
- Orchestrator hooks or a scheduler for the monitor jobs.
- An alerting channel with per-check ownership (Slack/email/pager).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: computing metrics, querying history, viewing
  dashboards, dry-run monitors.
- **Tier M (mutation)**: creating monitor tables/jobs, enabling alerts,
  changing thresholds, and silencing checks. All MUST be confirmed; false
  alarms erode trust, so alert enablement is a real change.

## Workflow

### 1. Inventory What to Monitor

List production tables by criticality (SLA tier):

- Tier 1: consumer-facing marts — full pillar coverage.
- Tier 2: intermediate models — freshness + volume.
- Tier 3: staging — minimal (schema + volume).

Record owners and expected cadence per table.

### 2. Emit the Core Metrics

A monitor job computes per run:

```python
import datetime as dt
import os

import duckdb

con = duckdb.connect()
metrics = con.execute(
    """
    SELECT
        current_timestamp AS measured_at,
        count(*) AS row_count,
        count(DISTINCT order_id) AS unique_keys,
        max(loaded_at) AS max_loaded_at,
        count(*) FILTER (WHERE amount < 0) AS negatives
    FROM read_parquet('s3://bucket/marts/*.parquet')
    """
).fetchone()

# ship to the metrics table/prometheus
print(dict(zip(["measured_at", "row_count", "unique_keys", "max_loaded_at", "negatives"], metrics)))
```

Store metrics in a dedicated `monitoring` schema with columns
`(table_name, measured_at, metric, value)` — a long, queryable history.

### 3. Detect Anomalies

Rules of thumb:

- **Freshness**: `max_loaded_at` vs expected window per cadence.
- **Volume**: z-score vs trailing 30d mean (`abs(v - mean) / std > 3`).
- **Schema**: compare `DESCRIBE` against the pinned schema (from data
  contracts) — added/removed/renamed columns.
- **Distribution**: quantile drift on key numeric columns; null-rate jumps.

Prefer simple, explainable rules over ML for v1; ML-based anomaly detection
only after 3+ months of history exists.

### 4. Alert with Lineage Awareness

- Map each alert to its owning team via the lineage graph (see
  openlineage-basics): alert the producer of the broken node AND the
  consumers at risk.
- Alert routing: warn -> Slack channel of the owner; error -> page/on-call.
- Every alert MUST link to the metric history and the affected table.

### 5. Review and Tune

Weekly: review fired alerts; re-baseline thresholds; escalate 3x-firing
warns. Monthly: report on MTTR and alert precision (aim: < 30% noise).

## Validation

- Monitor job runs on schedule and writes metrics with correct timestamps.
- A deliberately broken table (e.g. empty partition) triggers the alert path
  in dev/staging before enabling in production.
- Alert routing reaches the documented owner channel.
- Metric history exists for at least the retention window needed by
  thresholds.

## Definition of Done

- Tier 1/2 tables have freshness + volume monitors running.
- Anomaly detection rules documented and baselined on history.
- Alerts routed by ownership with lineage context.
- Monitoring job failures alert like pipeline failures (monitor-the-monitors).

## Reference Directory

- [Metric Schema](references/metric-schema.md): recommended monitoring
  schema and retention.
- [Anomaly Detection Rules](references/anomaly-rules.md): thresholds,
  z-scores, and baselining procedure.

## Related Skills

- [OpenLineage](../../governance/openlineage-basics/SKILL.md): the lineage
  graph for alert routing.
- [Data Quality Incident Runbook](../data-quality-incident-runbook/SKILL.md):
  what happens when an alert fires.
- [dbt Data Quality Tests](../dbt-data-quality-tests/SKILL.md): build-time
  gates feeding the same tables.
