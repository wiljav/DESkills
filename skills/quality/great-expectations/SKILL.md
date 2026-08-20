---
name: great-expectations
metadata:
  category: DataQuality
description: >-
  Defines, runs, and monitors data expectations against batch data with
  Great Expectations: expectations, checkpoints, and data docs. Use when
  adding declarative quality gates to pipelines or validating data before
  consumption. Don't use for SQL-embedded tests (use dbt tests) or for
  lightweight pipeline checks (use soda-basics).
allowed-tools:
  - python
  - great_expectations
---

# Great Expectations

Great Expectations (GX) validates data against declarative "expectations"
(column rules, distributions, batch invariants) and renders human-readable
data docs.

## Prerequisites

- Python 3.9+; `pip install great_expectations` (GX 1.x) or the version
  matching the project.
- A data source reachable (files, warehouse tables, object storage).
- A GX project directory (`great_expectations/`) initialized.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `gx validate`, `gx checkpoint run`, reading data
  docs, `gx datasource list`.
- **Tier M (mutation)**: `gx init`, adding datasources, editing
  expectations suites, and running checkpoints that write results to shared
  stores. Confirm before checkpoint runs against production data
  (they can raise alerts downstream).

## Workflow

### 1. Initialize the Project

```bash
gx init --directory great_expectations
```

This creates the project structure (expectations, checkpoints, plugins).

### 2. Connect a Data Source

```bash
gx datasource new
```

Choose the connector (Pandas/SQL/files). For warehouses prefer SQLAlchemy
datasources so expectations push down as SQL.

### 3. Define Expectations

Programmatic (recommended for maintainability):

```python
from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.data_context import FileDataContext

context = FileDataContext.create(project_root_dir="great_expectations")

expectations = [
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "order_id"},
    ),
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "amount", "min_value": 0},
    ),
    ExpectationConfiguration(
        expectation_type="expect_table_row_count_to_be_between",
        kwargs={"min_value": 1000, "max_value": 10_000_000},
    ),
]
```

Rules:

- Start with invariant expectations (not-null, ranges, PK uniqueness);
  distribution expectations are useful but drift-sensitive — set thresholds
  from observed percentiles.
- Use `mostly=` for acceptable exception rates instead of hard 100%.
- Never encode business secrets into expectations; expectations are visible
  in data docs.

### 4. Build Checkpoints

Checkpoints bind expectations to batches:

```bash
gx checkpoint new my_checkpoint
```

```yaml
# checkpoint yaml
name: my_checkpoint
config_version: 1.0
validations:
  - batch_request:
      datasource_name: my_datasource
      data_asset_name: orders
      options: {}
    expectation_suite_name: orders_suite
```

### 5. Run and Review

```bash
gx checkpoint run my_checkpoint
gx docs build --directory great_expectations
```

Review the data docs: each expectation shows pass/fail counts and
distribution plots. The run exit code is non-zero when the checkpoint fails
— wire it into the pipeline as a hard gate.

### 6. Operationalize

- Add the checkpoint to the pipeline (Airflow `PythonOperator`/`BashOperator`
  calling `gx checkpoint run`), or the validation-result store to an
  observability backend.
- Alert on checkpoint failure via the orchestrator's failure hooks.

## Validation

- Checkpoint runs clean against the expected (good) batch.
- A deliberately-broken batch (e.g. null PKs) fails the checkpoint — prove
  the gate actually gates.
- Data docs render and show pass/fail per expectation.

## Definition of Done

- Datasource connected; expectations suite covers invariants.
- Checkpoint bound to the right batches; runs and exits correctly.
- Failure behavior verified with a broken-batch test.
- Integration into the pipeline confirmed; alerts wired.

## Reference Directory

- [Expectations Catalogue](references/expectations.md): the rule types
  available and when to use them.
- [Operational Patterns](references/operations.md): checkpoints in
  orchestrators, result stores, and docs hosting.

## Related Skills

- [Soda](../soda-basics/SKILL.md): lighter-weight alternative for simple
  checks.
- [Data Observability](../data-observability/SKILL.md): continuous monitoring
  beyond batch validation.
- [dbt Data Quality Tests](../dbt-data-quality-tests/SKILL.md): SQL-native
  tests inside the transformation layer.