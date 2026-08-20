---
name: soda-basics
metadata:
  category: DataQuality
description: >-
  Writes and runs data quality checks with Soda Core and the Soda Checks
  Language: freshness, volume, schema, and custom SQL checks. Use when adding
  lightweight, YAML-first quality checks to pipelines. Don't use for
  SQL-embedded transformation tests (use dbt tests) or for heavyweight
  expectation suites (use great-expectations).
allowed-tools:
  - soda
  - python
---

# Soda Basics

Soda validates data with declarative checks in YAML ("Soda Checks Language"),
scanning tables with minimal setup and clear pass/fail output.

## Prerequisites

- `soda-core` plus the warehouse adapter
  (`soda-core-bigquery`, `soda-core-snowflake`, `soda-core-postgres`, ...).
- Warehouse connection configured via environment variables (see auth
  skill).
- A directory holding `checks/` YAML files.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `soda scan`, `soda test-connection`, reading scan
  results.
- **Tier M (mutation)**: adding data sources that write results to shared
  stores, and running scans against production with alerting enabled. Confirm
  before production scans that page/notify.

## Workflow

### 1. Configure the Data Source

`configuration.yml`:

```yaml
data_source orders_db:
  type: postgres
  host: ${POSTGRES_HOST}
  port: 5432
  database: ${POSTGRES_DB}
  username: ${POSTGRES_USER}
  password: ${POSTGRES_PASSWORD}
  schema: public
```

All credentials MUST come from environment variables.

### 2. Write Checks

`checks/orders.yml`:

```yaml
checks for orders:
  - freshness(loaded_at) < 6h
  - row_count > 10000
  - duplicate_count(order_id) = 0
  - missing_count(customer_id) = 0
  - avg(amount) between 50 and 500
  - schema:
      fail:
        when required column missing: [order_id, customer_id, amount]
```

Rules:

- One checks file per table/domain; checks read top-down like tests.
- Prefer the built-in metric checks (`row_count`, `freshness`,
  `duplicate_count`, `missing_count`, `avg`, `min`, `max`, percentiles).
- `warn` and `fail` thresholds: warn = watch, fail = gate.

### 3. Custom SQL Checks

```yaml
checks for orders:
  - failed rows:
      fail query:
        SELECT 1 FROM orders WHERE total < 0 LIMIT 1
```

Custom queries MUST return zero rows on success. Use them for rules the
metrics cannot express (multi-table invariants).

### 4. Run the Scan

```bash
soda scan -d orders_db -c configuration.yml checks/orders.yml
```

Exit code: 0 = pass, 1 = warn, 2 = fail. Wire into the orchestrator:

```bash
soda scan -d orders_db -c configuration.yml checks/ && echo "quality ok"
```

### 5. Review Results

Output shows per-check status with measured values vs thresholds. Fix
thresholds ONLY from observed history, never to silence alerts.

## Validation

- `soda test-connection` passes against the data source.
- A scan on known-good data passes; a deliberately broken check (wrong
  threshold) fails with exit code 2.
- Secrets resolve from env vars; config contains none.

## Definition of Done

- Data source configured with env-var credentials.
- Checks cover freshness, volume, uniqueness, and required columns.
- Scan passes on good data; failure behavior verified.
- Pipeline integration wired and confirmed.

## Reference Directory

- [Checks Language Reference](references/checks-language.md): metric
  catalogue and threshold syntax.
- [Scheduling & Alerting](references/scheduling.md): cron scans, Slack/email
  notifications, and result stores.

## Related Skills

- [Great Expectations](../great-expectations/SKILL.md): heavier suites for
  complex profiling.
- [dbt Data Quality Tests](../dbt-data-quality-tests/SKILL.md): SQL-native
  checks in the transformation layer.
- [Data Quality Incident Runbook](../data-quality-incident-runbook/SKILL.md):
  responding when scans fail.