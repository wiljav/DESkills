# Log Query Templates

## Self-managed Airflow (local files / journald)

```bash
# last 200 lines of a task log
airflow tasks logs --dag-id {dag_id} --task-id {task_id} --run-id {run_id}

# scheduler errors
journalctl -u airflow-scheduler -n 500 --no-pager | grep -iE "error|exception"

# worker errors
journalctl -u airflow-worker -n 500 --no-pager | grep -iE "error|exception"
```

## Cloud Composer (Cloud Logging)

```text
resource.type="cloud_composer_environment"
resource.labels.environment_name="{env_name}"
log_id("airflow-scheduler")
severity>=ERROR
```

For task logs, filter by the task name and run id:

```text
resource.type="cloud_composer_environment"
resource.labels.environment_name="{env_name}"
textPayload:"{dag_id}" OR textPayload:"{task_id}"
severity>=ERROR
```

## MWAA (CloudWatch)

```text
{log_group_name}/TaskLogs  # per-task log streams
```

Search for `ERROR`/`Traceback` in the DAG's task stream; check
`scheduler` and `worker` log groups for platform-level errors.

## Metadata DB queries (read-only)

```sql
SELECT dag_id, run_id, state, start_date, end_date
FROM dag_run
WHERE dag_id = '{dag_id}' AND state = 'failed'
ORDER BY start_date DESC LIMIT 5;
```

Run through `airflow db shell` or the platform SQL access; read-only only.