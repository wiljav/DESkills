# Failure Signatures

Decision tree for Airflow failures. Start with the signature, run the
diagnosis commands, then follow the fix.

## 1. Import error

Signal: `airflow dags list-import-errors` returns rows.

Diagnosis:

```bash
airflow dags list-import-errors
airflow dags show {dag_id} 2>&1 | head -20   # repeats the traceback
```

Fix: fix the code defect (syntax, missing provider, bad import), then redeploy
per `airflow-dag-authoring`. Verify the error disappears from
`list-import-errors` after one parse cycle.

## 2. Task failed with exception

Signal: task state `failed`; log contains a Python traceback.

Diagnosis:

```bash
airflow tasks logs --dag-id {dag_id} --task-id {task_id} --run-id {run_id} | tail -200
```

Classification by exception:

| Exception | Likely cause |
| --- | --- |
| `FileNotFoundError` / `NotFound` (object storage) | missing upstream data or wrong key/prefix |
| `OperationalError` (DB) | connection/database down or schema drift |
| `PermissionDenied` / `AccessDenied` | credentials or IAM scope issue |
| `OutOfMemoryError` / connector limit | resource limits (see #5) |
| `DuplicateKeyError` | non-idempotent write; data may be partially written |

Fix: resolve per root cause (data, credentials, resources, code). Only then
clear and rerun.

## 3. Task stuck in running

Signal: `running` for longer than the expected duration.

Diagnosis:

```bash
airflow tasks list-runs --dag-id {dag_id} --state running
airflow celery flower 2>/dev/null   # Celery: check worker queue depth
airflow scheduler log tail          # scheduler: check "Scheduler heartbeat" freshness
```

Fix: if scheduler heartbeats are stale, restart the scheduler (mutation,
confirmed). If workers are saturated, scale workers or reduce parallelism;
then clear the stuck task.

## 4. Retry storm

Signal: multiple consecutive `failed` states with identical tracebacks on the
same task.

Diagnosis: confirm identical `last_exception` across runs.

Fix: the failure is deterministic — fix the root cause, then clear. Do NOT
increase retries to mask a deterministic failure; that only delays alerting.

## 5. Missing run

Signal: no DAG run for an expected interval.

Diagnosis:

```bash
airflow dags list-runs --dag-id {dag_id} --limit 10
airflow config get-value core dag_dir_list_interval
```

Fix: if `catchup=False`, missed intervals are not replayed automatically —
run an explicit backfill after confirming the data window is recoverable.

## 6. Upstream data issue

Signal: task reads a table/partition/file that does not exist or is empty.

Diagnosis (read-only):

```bash
# example: BigQuery
bq show {project}:{dataset}.{table}   # confirm table exists
# example: object storage
aws s3 ls s3://{bucket}/{prefix}/ | tail -5
```

Fix: wait for/restart the upstream producer, or adjust the task to use an
`ExternalTaskSensor`/data sensor. Never retry downstream tasks while the
upstream is still broken — you will repeat failures and burn retries.
