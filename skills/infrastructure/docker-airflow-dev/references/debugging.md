# Debugging Locally

## Where to look

| Symptom | Log |
| --- | --- |
| DAG not in UI | `docker compose logs scheduler` (import errors) |
| Task never starts | scheduler logs; check `state=queued` |
| Task fails | task logs in the UI (the executor's stdout) |
| Webserver slow/500 | `docker compose logs webserver` |

## Re-running a task

```bash
docker compose exec scheduler airflow tasks clear {dag} --task-id {task} -d 2024-01-01
docker compose exec scheduler airflow dags trigger {dag}
```

- `airflow tasks clear` resets task state for the date range, then
  re-trigger the DAG.
- For logic debugging prefer `airflow tasks test` (in-process, isolated).

## Common local issues

- **dags folder not mounted**: container sees the DAGs baked at image
  build — re-check the bind mount path.
- **Port conflicts** (8080 busy): change `ports: ["8081:8080"]`.
- **Timezones**: set `AIRFLOW__CORE__DEFAULT_TIMEZONE=UTC` and keep DAG
  schedules in UTC to match production.
- **OOM in scheduler**: give Docker more memory (Docker Desktop
  settings); Airflow 2.x schedules in-process.