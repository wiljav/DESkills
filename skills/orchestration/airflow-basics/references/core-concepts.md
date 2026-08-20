# Core Concepts

## Components

| Component | Role |
| --- | --- |
| Scheduler | Parses DAGs, enqueues task instances per schedule and dependencies |
| Webserver | UI/API; trigger runs, view logs, manage config |
| Worker(s) | Execute tasks (LocalExecutor: in-process; Celery: distributed; Kubernetes: per-task pods) |
| Metadata DB | Source of truth for DAGs, runs, task instances, variables, connections |

## Executor comparison

| Executor | Scale | Best for |
| --- | --- | --- |
| SequentialExecutor | 1 task at a time | smoke tests only |
| LocalExecutor | many threads on one host | dev/small teams |
| CeleryExecutor | N workers | medium production |
| KubernetesExecutor | pod per task | production, isolation, autoscaling |

## Scheduling model

- A DAG run is created for each schedule interval; tasks run when upstream
  dependencies complete.
- `execution_date` (renamed `logical_date` in Airflow 2.4+) is the start of
  the interval, not the run time — backfills iterate over intervals.
- Catchup replays missed intervals; production DAGs default to
  `catchup=False`.
- DAG parsing happens every `dag_dir_list_interval` seconds; top-level code in
  DAG files runs on every parse, so keep it free of I/O.

## Failure and retry model

- Task failure triggers retries per `retries`/`retry_delay`; exhausted
  retries mark the run failed.
- `on_failure_callback` can page teams; `max_active_runs_per_dag` limits
  overlapping runs.
- Scheduler down time does not drop schedules; missed intervals are handled
  by catchup or backfill.