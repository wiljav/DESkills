---
name: dbt-data-quality-tests
metadata:
  category: DataQuality
description: >-
  Enforces uniqueness, not-null, referential, freshness, and custom quality
  guarantees inside dbt projects using tests, sources, and singular checks.
  Use when quality gates should live with the transformation code that
  produces the data. Don't use for engine-agnostic validation outside dbt
  (use soda or great-expectations).
allowed-tools:
  - dbt
  - python
---

# dbt Data Quality Tests

dbt is the natural home for quality gates on transformed data: tests ship
with the models, run in dependency order, and fail the build on violation.

## Prerequisites

- A dbt project per `dbt-core`.
- Warehouse connection configured; `dbt debug` passes.
- The `dbt-tests-macros` skill's patterns available (generic tests,
  `dbt_utils`).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `dbt compile`, `dbt test --select <model>`,
  `dbt source freshness`, previews via `dbt show`.
- **Tier M (mutation)**: `dbt build`/`dbt test` on production targets
  (tests fail loudly and may page), and adding `warn_if`-style soft gates.
  Confirm before production runs.

## Workflow

### 1. Enforce Primary-Key Integrity

Every fact/dimension model:

```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
```

- `unique` + `not_null` on every PK: non-negotiable.
- Composite keys: `dbt_utils.unique_combination_of_columns`.

### 2. Enforce Referential Integrity

```yaml
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_id
              severity: warn   # orphan-tolerant marts warn, facts fail
```

- Facts fail hard on broken FK; intermediate models may warn while lineage
  settles.
- Tag cross-team critical tests `tags: ['critical']` for CI fast-fail.

### 3. Add Freshness Gates on Sources

```yaml
sources:
  - name: raw
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
    loaded_at_field: _loaded_at
```

Run `dbt source freshness` in CI and on schedule; stale sources fail the
gate before models build on top of them.

### 4. Write Business-Rule Tests

Generic + singular:

```yaml
    tests:
      - dbt_utils.expression_is_true:
          expression: "total_amount >= 0"
          severity: error
```

```sql
-- tests/assert_fct_orders_positive_total.sql
SELECT order_id
FROM {{ ref('fct_orders') }}
WHERE total_amount < 0
LIMIT 10;
```

### 5. Use Soft Gates for Trend-Sensitive Rules

```yaml
      - name: amount
        tests:
          - dbt_expectations.expect_column_min_to_be_between:
              min_value: 0
              warn_if: "not between"
```

- `warn_if`/`severity: warn` for distribution-style rules: fail on hard
  invariants, warn on drift.
- Every warn gate MUST have a follow-up monitor (see data-observability).

### 6. Run and Verify

```bash
dbt test                     # all tests
dbt source freshness         # source freshness gates
dbt build --select fct_orders   # model + tests + downstream
```

Verify failure behavior: introduce a violating row in dev, confirm the test
fails and the build stops.

## Validation

- PK/FK/not-null tests exist on all marts (grep the YAML).
- `dbt build` green on dev; production test run confirmed.
- Freshness gates configured on critical sources and passing.
- Failure path verified (bad row -> test fails -> build fails).

## Definition of Done

- Integrity tests (unique/not_null/relationships) on all consumer models.
- Business-rule tests for the model's invariants.
- Freshness gates on critical sources.
- Severity policy documented (fail vs warn per model tier).
- `dbt build` verified green and failing correctly when violated.

## Reference Directory

- [Test Tiers & Severity Policy](references/test-tiers.md): which rules fail
  vs warn, and the review cadence.
- [Freshness & Volatility Gates](references/freshness.md): designing
  freshness thresholds per source cadence.

## Related Skills

- [dbt Tests & Macros](../../transformation/dbt-tests-macros/SKILL.md):
  authoring mechanics for these tests.
- [dbt Core](../../transformation/dbt-core/SKILL.md): the project these
  gates protect.
- [Data Observability](../data-observability/SKILL.md): continuous
  monitoring beyond build-time tests.
