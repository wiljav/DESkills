---
name: dbt-core
metadata:
  category: DataTransformation
description: >-
  Models, tests, and documents warehouse data with dbt projects: project
  structure, models, materializations, sources, and seeds. Use when starting
  or extending a dbt transformation layer. Don't use for writing dbt tests
  and macros (use dbt-tests-macros) or for CI/CD setup (use ci-cd-for-dbt).
allowed-tools:
  - dbt
  - python
---

# dbt Core

dbt is the transformation layer for warehouses: models are SQL (or Python),
materialized by dbt into tables/views, with lineage, tests, and docs built
in. This skill covers project foundation.

## Prerequisites

- `dbt-core` plus the adapter for the target warehouse
  (`dbt-bigquery`, `dbt-snowflake`, `dbt-redshift`, `dbt-postgres`, ...).
- Warehouse credentials per `data-engineering-auth`, exposed via env vars
  (`DBT_*` or profile env templating).
- Access to the raw/source data the models will read.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `dbt debug`, `dbt parse`, `dbt compile`, `dbt ls`,
  `dbt show`, `dbt docs generate`, `dbt build --select <model> --dry-run`-style
  previews (`--show`).
- **Tier M (mutation)**: `dbt run`, `dbt build`, `dbt run --full-refresh`,
  `dbt snapshot`, and `dbt seed`. Full refresh rebuilds tables (drops and
  recreates data) and MUST be confirmed with the blast radius stated.

## Workflow

### 1. Initialize and Configure the Project

```bash
dbt init {project_name}
cd {project_name}
dbt debug
```

Check the generated `profiles.yml`/`dbt_project.yml`: target database,
schema conventions (`schema: analytics`), and `profile` name must match the
adapter config. Never commit `profiles.yml` with credentials — use env vars:

```yaml
# profiles.yml (not committed)
bigquery:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: "{{ env_var('BQ_PROJECT') }}"
      dataset: analytics_dev
```

### 2. Define Sources

Declare upstream tables in `models/staging/_sources.yml`:

```yaml
sources:
  - name: raw
    database: "{{ env_var('BQ_PROJECT') }}"
    schema: raw
    tables:
      - name: events
        loaded_at_field: _loaded_at
        freshness:
          warn_after: { count: 6, period: hour }
```

Sources give dbt lineage roots and enable freshness checks.

### 3. Author Models

Staging models first (clean, typed, minimal), then intermediate and marts:

```sql
-- models/staging/stg_events.sql
SELECT
    id,
    customer_id,
    CAST(event_time AS TIMESTAMP) AS event_time,
    SAFE_CAST(amount AS NUMERIC) AS amount
FROM {{ source('raw', 'events') }}
```

Rules:

- Follow the staging -> intermediate -> marts layering; marts are the
  consumer-facing models.
- Every model MUST be idempotent: materializations (`table` with overwrite,
  incremental with `is_incremental()`) ensure re-runs converge.
- Column typing MUST happen in staging, never at marts.
- Use `ref()` for model dependencies, never raw table names — refs drive
  lineage and run ordering.

### 4. Choose Materializations

| Materialization | Use |
| --- | --- |
| view | lightweight, always fresh, used for simple passthrough |
| table | snapshot at run time; good for transformed summaries |
| incremental | append/merge by `is_incremental()`; MUST be idempotent |
| ephemeral | inlined CTEs; avoid in production (hides lineage) |
| snapshot | type-2 history for slowly changing dimensions |

### 5. Run and Verify

```bash
dbt run --select stg_events+     # model + downstream
dbt show --select stg_events     # preview first rows without writing
dbt build --select stg_events    # run + test in dependency order
```

Rules:

- Preview (`dbt show`) before the first full run of new models.
- Run in `--select` increments (staging -> marts), verifying each layer.
- Never `dbt run --full-refresh` on shared/production targets without
  confirmation and a stated data-loss risk.

### 6. Generate Documentation

```bash
dbt docs generate
dbt docs serve
```

Verify the DAG view shows sources -> staging -> marts and every model has a
description.

## Validation

- `dbt debug` passes (profile + connection).
- `dbt build --select <model>` succeeds; model + its tests pass.
- `dbt run --full-refresh` NOT used without confirmation; idempotent
  re-runs verified (`dbt run --select x` twice -> same row counts).
- Freshness checks configured for key sources; `dbt source freshness`
  passes or flags expected issues.

## Definition of Done

- Project initialized; profiles use env vars; credentials not committed.
- Sources declared with freshness where applicable.
- Models layered (staging -> marts), typed in staging, using `ref()`.
- Materializations chosen and idempotent; incremental logic verified.
- Docs generated; lineage DAG correct.

## Reference Directory

- [Project Structure](references/project-structure.md): folders, YAML
  conventions, and naming.
- [Incremental & Materialization Guide](references/materializations.md):
  incremental strategies per warehouse and gotchas.

## Related Skills

- [dbt Tests & Macros](../dbt-tests-macros/SKILL.md): quality gates for
  models written here.
- [CI/CD for dbt](../../infrastructure/ci-cd-for-dbt/SKILL.md): deploying
  the project safely.
- [dbt Data Quality Tests](../../quality/dbt-data-quality-tests/SKILL.md):
  test-first data quality.
