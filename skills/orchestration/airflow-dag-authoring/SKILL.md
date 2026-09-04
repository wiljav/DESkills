---
name: airflow-dag-authoring
metadata:
  category: Orchestration
description: >-
  Authors production-grade Apache Airflow DAGs: idempotent tasks, correct
  dependencies, retries, catchup policy, and validation before deployment.
  Use when creating or extending a DAG for any Airflow environment. Don't use
  for authoring Python unrelated to Airflow, or for configuring the Airflow
  platform itself (use airflow-basics).
allowed-tools:
  - airflow
  - python
  - ruff
  - gcloud
---

# Airflow DAG Authoring

This skill guides the authoring and validation of DAGs that are safe to
deploy to production: deterministic, idempotent, observable, and lint-clean.

## Prerequisites

- Target environment identified: Airflow version (2.x vs 3.x), executor,
  provider versions.
- A local environment with `airflow` CLI available (see `docker-airflow-dev`
  for the Dockerized dev setup).
- `ruff` installed for static analysis.
- Access to the DAGs folder (local dev or GCS bucket for managed Airflow).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: linting, DAG parsing checks, `dags list-import-errors`,
  diff review of local DAG files.
- **Tier M (mutation)**: uploading DAGs to a shared DAGs folder (GCS/EB/EFS),
  triggering test runs (`dags trigger`), and backfills. These impact shared
  environments and MUST be confirmed by the user first.

## Workflow

### 1. Inspect the Target Environment

Before writing code, determine constraints:

```bash
airflow version
airflow providers list 2>/dev/null | grep -E "apache-airflow-providers-.* " | head
```

For managed Airflow (Cloud Composer / MWAA), inspect the image version and
installed packages via the platform CLI (`gcloud composer environments
describe ...`). Record: Airflow major version, providers, and Python version.

### 2. Author the DAG

Follow these MUST rules:

- **Idempotency**: every task MUST be rerunnable with the same
  `logical_date` producing the same result (use `INSERT OVERWRITE`-style
  semantics, `delete + reload`, or unique-key dedup).
- **No top-level execution**: no DB queries, API calls, or heavy compute at
  module import time — the scheduler imports the file every parse cycle.
- **Catchup policy**: set `catchup=False` unless backfilling is explicitly
  required; set `max_active_runs=1` for single-instance pipelines.
- **Retries**: define `default_args` with `retries=2`, `retry_delay`,
  `retry_exponential_backoff=True`, and `max_retry_delay`.
- **Observability**: set `retries` on the DAG level, add
  `on_failure_callback` (e.g. Slack) only when explicitly requested, and log
  with `task_instance.log` / `get_logger`.

```python
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "data-platform",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(hours=1),
}

with DAG(
    dag_id="example_batch",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["example"],
) as dag:

    def transform(logical_date, **context):
        # idempotent: recompute the full interval then replace
        print(f"processing interval {logical_date}")

    run_transform = PythonOperator(
        task_id="transform",
        python_callable=transform,
    )
```

### 3. Static Analysis & Linting

```bash
ruff check dags/
```

- Fix all findings; errors (E/F) MUST be zero, warnings SHOULD be zero.
- Check for the classic mistakes: imports of DAG files with side effects,
  use of `Variable.get` at module level, `datetime.now()` inside
  `default_args`, and missing `catchup=False`.

### 4. Local Validation

Parse the DAG without running tasks:

```bash
python -c "from airflow.models import DagBag; b = DagBag(dag_folder='dags/', include_examples=False); assert not b.import_errors, b.import_errors"
```

Then verify the task graph renders: `airflow dags show {dag_id}` and
`airflow dags list | grep {dag_id}`.

### 5. Deploy to the Target Environment

Only after user confirmation, upload the file to the shared DAGs folder:

```bash
# managed Airflow on GCP
gcloud storage cp dags/{dag_file}.py gs://{bucket}/dags/
# self-managed: place in DAGS_FOLDER
cp dags/{dag_file}.py {DAGS_FOLDER}/
```

### 6. Verify in the Environment

Wait one parse cycle (`dag_dir_list_interval`, typically 60s), then:

```bash
airflow dags list-import-errors          # MUST be empty
airflow dags show {dag_id} --save /tmp/graph.png  # MUST render
```

If the user approves a test run:

```bash
airflow dags trigger {dag_id}
airflow tasks list {dag_id}
```

Monitor the run via `airflow dags list-runs --dag-id {dag_id}` until success
or failure; on failure, hand off to `airflow-job-failure-troubleshooting`.

## Validation

- `DagBag` import produces zero import errors locally and in the environment.
- `ruff` passes with zero errors.
- A triggered run completes successfully for a sample `logical_date`, or the
  failure was reproduced and diagnosed, not ignored.
- Graph renders; DAG appears in `dags list`.

## Definition of Done

- DAG is idempotent, has explicit catchup/retry policy, and no top-level I/O.
- Lint clean; import errors zero in the target environment.
- Deployment confirmed by the user and verified (listed, renders, runs).
- Logs from the test run reviewed; anomalies explained.
- No credentials or secrets in the DAG file; connections come from
  Airflow-level secrets.

## Reference Directory

- [Task Design Patterns](references/task-design-patterns.md): PythonOperator
  vs providers, branching, XComs, and task groups.
- [Airflow 2 vs 3](references/airflow-2-vs-3.md): API changes that break
  authoring between major versions.
- [Validation Checklist](references/validation-checklist.md): the exact
  commands to run before and after deployment.

## Related Skills

- [Airflow Basics](../airflow-basics/SKILL.md): platform-level setup and
  connections this DAG relies on.
- [Airflow Job Failure Troubleshooting](../airflow-job-failure-troubleshooting/SKILL.md):
  when the test run fails.
- [Dockerized Airflow Development](../../infrastructure/docker-airflow-dev/SKILL.md):
  local dev loop that validates before deploy.
