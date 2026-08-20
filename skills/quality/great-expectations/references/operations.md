# Operational Patterns

## Checkpoints in orchestrators

Airflow example:

```python
from airflow.operators.python import PythonOperator
from great_expectations.data_context import FileDataContext

def run_gx_checkpoint(**context):
    gx = FileDataContext.create(project_root_dir="great_expectations")
    result = gx.run_checkpoint("my_checkpoint")
    if not result.success:
        raise RuntimeError("Great Expectations checkpoint failed")

run_gx_checkpoint_task = PythonOperator(
    task_id="gx_checkpoint",
    python_callable=run_gx_checkpoint,
    dag=dag,
)
```

A failed checkpoint MUST fail the task — never log-and-continue.

## Result stores

- Default: local `uncommitted/validations/`.
- Production: S3/GCS result store + shared docs site so the team can see
  history: `gx checkpoint run` then `gx docs build` into the same bucket.

## Data docs

- Host the rendered `data_docs/` on object storage and link from the
  warehouse catalog entry (DataHub description) so consumers self-serve.
- Regenerate after suite edits; stale docs mislead.

## Alerting

- Alert on checkpoint failure via orchestrator hooks; include the failing
  expectation names in the alert body.
- Separate "checkpoint run failed" (pipeline) from "data violates
  expectations" (data quality incident) — the runbook skill covers the
  latter's response flow.