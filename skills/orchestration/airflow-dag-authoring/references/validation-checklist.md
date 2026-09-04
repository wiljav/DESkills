# Validation Checklist

Run these in order. Any failure stops the flow and MUST be diagnosed before
proceeding.

## Pre-deploy (local)

```bash
ruff check dags/
python - <<'PY'
from airflow.models import DagBag
b = DagBag(dag_folder="dags/", include_examples=False)
assert not b.import_errors, b.import_errors
print("OK: dagbag imports clean")
PY
airflow dags show {dag_id} --save /tmp/graph.png
```

## Post-deploy (target environment)

```bash
airflow dags list-import-errors   # must be empty
airflow dags list | grep {dag_id}
airflow dags show {dag_id} --save /tmp/graph_target.png
```

## Test run

```bash
airflow dags trigger {dag_id}
airflow dags list-runs --dag-id {dag_id} --state success --limit 1
```

Watch the first run end-to-end; confirm:

- tasks execute in declared dependency order;
- XCom sizes are small;
- retries are not firing repeatedly (a retry storm indicates a
  non-idempotent task);
- the DAG is idempotent: re-triggering with the same `logical_date`
  produces the same result.
