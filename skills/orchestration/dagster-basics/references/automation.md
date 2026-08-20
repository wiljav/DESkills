# Schedules, Sensors & Automation

## Schedules

- `ScheduleDefinition(job=..., cron_schedule="...")` — cron string, MUST
  include an explicit timezone when the platform supports it.
- Use `@schedule(job=..., cron_schedule=...)` decorator when the schedule
  needs context (e.g. computing partitions from `datetime`).

## Sensors

Sensors trigger runs on external events:

```python
from dagster import sensor

@sensor(job=materialize_all)
def new_file_sensor(context):
    files = list_files("gs://{bucket}/inbox/")
    return RunRequest(run_key=files[-1].name, partition_key=files[-1].date)
```

- `run_key` deduplicates triggers; a new `run_key` creates a new run, the
  same key is skipped. This is the idempotency primitive for sensors.
- Refresh sensors on intervals (`minimum_interval_seconds`); keep probing
  cheap.

## Failure handling

- Dagster retries: `@op(retry_policy=RetryPolicy(max_retries=2))` for ops;
  jobs inherit from ops.
- Failure hooks: `on_execute_failure` on jobs for alerts.
- For data-quality failures prefer asset checks over job failure — a check
  failure keeps the run "succeeded" while flagging the asset, which is the
  correct semantics for pipeline health.