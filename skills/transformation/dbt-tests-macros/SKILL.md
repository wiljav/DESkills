---
name: dbt-tests-macros
metadata:
  category: DataTransformation
description: >-
  Writes singular and generic dbt tests, reusable macros, and packages for
  reliable transformation projects. Use when adding data-quality gates to a
  dbt project or refactoring repeated SQL into macros. Don't use for initial
  project setup (use dbt-core) or for warehouse-specific quality checks
  (use great-expectations or soda).
allowed-tools:
  - dbt
  - python
---

# dbt Tests & Macros

This skill extends a dbt project with a test suite and macro library:
generic tests, singular tests, unit tests, and reusable Jinja.

## Prerequisites

- A working dbt project per `dbt-core` (models compile).
- Warehouse access for `dbt build`/`dbt test`.
- `dbt-utils`, `dbt_expectations`, or `dbt_meta_testing` packages installed
  via `packages.yml` if their tests/macros are used.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `dbt compile`, `dbt test --select <model>`,
  `dbt ls --resource-type test`, `dbt parse`.
- **Tier M (mutation)**: `dbt build`, `dbt run` (needed to create models for
  tests), `dbt test` against production targets, and package installs that
  modify the lockfile. Confirm before running against shared targets.

## Workflow

### 1. Install the Utility Package

`packages.yml`:

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: "1.1.1"
```

Then:

```bash
dbt deps
```

Verify the package resolves in `dbt_project.yml` (`dispatch` config for
cross-adapter macros).

### 2. Write Generic Tests in YAML

Attach tests to models/columns:

```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_id
    tests:
      - dbt_utils.expression_is_true:
          expression: "total_amount >= 0"
```

Rules:

- Every primary key: `unique` + `not_null`.
- Every foreign key: `relationships` to the parent model.
- Business rules as `expression_is_true` or custom generic tests.

### 3. Write Singular Tests

`tests/assert_fct_orders_fresh.sql`:

```sql
-- fails when data is older than the freshness SLA
SELECT 1
FROM {{ ref('fct_orders') }}
WHERE max(order_date) < current_date - INTERVAL 2 DAY
HAVING count(*) > 0;
```

Singular tests are plain SQL: zero rows = pass. Name them
`assert_*`/`expect_*` for clarity.

### 4. Author Reusable Macros

`macros/percent_change.sql`:

```jinja
{% macro percent_change(current, previous) %}
  case
    when {{ previous }} = 0 then null
    else round(100 * ({{ current }} - {{ previous }}) / {{ previous }}, 2)
  end
{% endmacro %}
```

Rules:

- Macros for repeated expressions/patterns ONLY — a macro per query is
  over-engineering.
- Macro arguments use column names (not raw SQL) so callers pass expressions.
- Document each macro with a doc block (`{% docs %}`) and unit-test complex
  ones (step 5).

### 5. Add dbt Unit Tests (1.8+)

```yaml
unit_tests:
  - name: test_percent_change
    model: int_order_metrics
    given:
      - input: ref('stg_orders')
        rows:
          - {order_id: 1, amount: 100}
    expect:
      rows:
        - {order_id: 1, pct_change: 0.0}
```

Run:

```bash
dbt test --select test_percent_change
```

Unit tests verify logic without warehouse round-trips — fast feedback for
macro/model logic.

### 6. Run the Full Suite

```bash
dbt test                 # all tests
dbt build                # run + test in dependency order
dbt build --select fct_orders+   # model + its tests + downstream
```

## Validation

- `dbt deps` resolves; no version conflicts.
- Every model has at least a primary-key uniqueness test (grep the YAML).
- Full `dbt build` passes on the dev target with zero failures.
- Unit tests for macros pass locally without warehouse access.

## Definition of Done

- Generic tests on all PK/FK columns and business rules.
- Singular tests for cross-model invariants.
- Macros documented and unit-tested where non-trivial.
- `dbt build` green on dev; production test run confirmed by the user.

## Reference Directory

- [Generic Test Library](references/generic-tests.md): catalog of built-in
  and package tests with usage.
- [Macro Patterns](references/macro-patterns.md): dispatch, hooks, and
  cross-adapter portability.

## Related Skills

- [dbt Core](../dbt-core/SKILL.md): project foundation these tests protect.
- [dbt Data Quality Tests](../../quality/dbt-data-quality-tests/SKILL.md):
  warehouse-level quality gates beyond tests.
- [CI/CD for dbt](../../infrastructure/ci-cd-for-dbt/SKILL.md): running the
  suite in pull requests.