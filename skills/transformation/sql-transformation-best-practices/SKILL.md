---
name: sql-transformation-best-practices
metadata:
  category: DataTransformation
description: >-
  Writes performant, maintainable, and reviewable transformation SQL:
  CTE structure, typing, naming, and anti-patterns. Use when writing or
  reviewing SQL models for any warehouse or engine. Don't use for dbt
  project mechanics (use dbt-core) or engine-specific tuning (use
  warehouse-optimization).
allowed-tools:
  - sqlfluff
  - python
---

# SQL Transformation Best Practices

This skill standardizes transformation SQL across engines: readable,
typed, tested-by-inspection, and performant.

## Prerequisites

- A target warehouse/engine (BigQuery, Snowflake, Redshift, DuckDB, Spark
  SQL).
- `sqlfluff` installed for linting (`uv tool install sqlfluff`).
- Access to read the source schemas being transformed.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: linting, `EXPLAIN`/`EXPLAIN ANALYZE` on reads,
  `SELECT` previews, and reviewing plans.
- **Tier M (mutation)**: creating tables/views, `INSERT`, and any `MERGE`
  that writes. Confirmed per the hosting pipeline's normal mutation rules.

## Workflow

### 1. Structure the Query with CTEs

One CTE per concept, top to bottom = data flow:

```sql
with
raw_events as (
    select * from `project.raw.events`
),

valid_events as (
    select
        id,
        customer_id,
        timestamp_trunc(event_time, hour) as event_hour,
        amount
    from raw_events
    where status = 'valid'
),

hourly_totals as (
    select
        event_hour,
        customer_id,
        sum(amount) as total_amount
    from valid_events
    group by 1, 2
)

select * from hourly_totals
```

Rules:

- Name CTEs by their meaning (`raw_`, `valid_`, `_totals`); no CTEs named
  `a`, `cte1`.
- Each CTE does ONE job; the query reads like a pipeline.
- `select *` only at the very first ingestion of a table, never later.

### 2. Type Everything Early

Cast at first reference, then reuse:

- Dates/timestamps: explicit `CAST(... AS DATE/TIMESTAMP)` with documented
  formats.
- Numeric: `SAFE_CAST`/`TRY_CAST` where bad data is possible; decide and
  document the policy (null-out vs error) per column.
- Booleans/strings: normalize case/whitespace at the boundary.

### 3. Filter Before Join, Project Before Group

- Push `WHERE` into the earliest CTE (predicate pushdown depends on it).
- Select only needed columns before joins/aggregations.
- Avoid `DISTINCT` as a "fix"; it masks join blowups — fix the join.

### 4. Handle Nulls and Aggregations Explicitly

- State `COALESCE` policy per column in comments.
- Watch NULL in `NOT IN` — use `NOT EXISTS` (NULL-safe) for anti-joins.
- Aggregations: `sum()` ignores NULLs; `count(col)` vs `count(*)` differ —
  be deliberate.

### 5. Lint and Review

```bash
sqlfluff lint models/ --dialect bigquery   # or snowflake/redshift/postgres
sqlfluff fix models/ --dialect bigquery
```

Review checklist (write it in PR descriptions):

- One CTE per concept; flow reads top-down.
- No `select *` beyond the boundary; no implicit casts.
- No cartesian joins; join keys typed consistently.
- Comments explain WHY (business rules), not what.

### 6. Verify with the Plan

```sql
EXPLAIN select ...;
```

Confirm: filter pushdown into the scan, join order sane, no full-table
scans on huge tables where partition pruning should apply.

## Validation

- `sqlfluff lint` passes on the dialect (or exceptions documented).
- The plan shows expected pushdowns/pruning.
- Result spot-checks match an independent aggregation on a sample.
- No anti-patterns from the reference remain.

## Definition of Done

- Query structured with named single-purpose CTEs.
- Types cast at the boundary; null policy documented.
- Lint clean; plan verified; sample results checked.
- Reviewed against the anti-pattern list (reference).

## Reference Directory

- [Anti-Patterns](references/anti-patterns.md): the top ten mistakes and
  fixes.
- [Style Guide](references/style-guide.md): formatting, naming, and comment
  conventions.

## Related Skills

- [dbt Core](../dbt-core/SKILL.md): hosting these queries in a project.
- [Warehouse Optimization](../../warehousing/warehouse-optimization/SKILL.md):
  engine-level tuning when performance is still poor.
- [Parquet & File Formats](../../storage/parquet-file-formats/SKILL.md):
  file-level factors affecting scan efficiency.