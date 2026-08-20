# Task Design Patterns

## PythonOperator vs provider operators

- Use provider operators (`BigQueryInsertJobOperator`, `SnowflakeOperator`,
  `KubernetesPodOperator`) when the task is a single well-defined call — they
  bring idempotency and retries for free.
- Use `PythonOperator` when the logic is custom; keep the callable small,
  importable, and free of side effects at import time.
- Wrap long-running external jobs with `ExternalTaskSensor` or
  `TimeSensor` rather than sleeping.

## Branching

Use `BranchPythonOperator` only when the branch is a cheap pure function of
task inputs. For data-dependent branching prefer a single task that computes
the target and triggers it, or conditional task mapping (`expand`).

## XComs

- XComs are stored in the metadata DB: keep payloads small (<= tens of KB).
- Pass explicit values via `return_value`/`xcom_push`; avoid passing whole
  DataFrames.
- When a large artifact must move between tasks, write it to object storage
  and pass the URI as the XCom value.

## Task groups and dynamic tasks

- `TaskGroup` groups related tasks in the UI; it does not change execution.
- Dynamic task mapping (`dag.partial(...).expand(...)`) is the modern way to
  fan out; map over URIs/keys, not over data payloads.
- Keep the number of mapped tasks bounded (e.g. < 1000) and documented.

## Idempotency recipes

| Workload | Pattern |
| --- | --- |
| Warehouse insert | `DELETE WHERE logical_date = {{ ds }}` then insert |
| Object storage | write to `.../logical_date=.../` prefix (partitioned) |
| Append-only logs | dedup by event id on read |
| ML feature table | `INSERT OVERWRITE PARTITION` semantics |