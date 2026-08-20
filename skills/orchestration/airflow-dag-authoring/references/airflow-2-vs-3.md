# Airflow 2 vs 3

Authoring differences that matter when migrating or targeting mixed fleets.

| Area | Airflow 2 | Airflow 3 |
| --- | --- | --- |
| `execution_date` | deprecated alias | use `logical_date` |
| `@task` decorators | stable | stable (preferred entry point) |
| `DAG(...)` context manager | supported | supported |
| scheduler serialization | DAG processors | native (bundled) DAG processor, no `dag_processor_manager` |
| `BaseOperator.retries` default | 0 | 0 (unchanged; set explicitly) |
| providers | versioned separately | same model; require >= matching release |
| `airflow dags list-import-errors` | available | available |
| task flow API | mature | expanded `expand` kwargs (`partial`, `zip`) |

## Migration tips

- Replace all `execution_date` references with `logical_date`.
- Recreate the virtual environment with the new Airflow version; provider
  pins from 2.x may not be compatible.
- Run the validation checklist in the target environment before and after
  the migration; import errors are the top migration failure.
- Keep `catchup=False` during migration cutover; backfill after the move is
  verified.