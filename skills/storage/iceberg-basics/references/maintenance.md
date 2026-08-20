# Maintenance Playbook

## Cadence

| Task | Cadence | Command (Spark SQL) |
| --- | --- | --- |
| Expire snapshots | daily | `CALL {catalog}.system.expire_snapshots(table => '...', older_than => TIMESTAMP '{yesterday}', retain_last => 1)` |
| Rewrite data files | weekly (or when small files detected) | `CALL {catalog}.system.rewrite_data_files(table => '...', strategy => 'binpack')` |
| Rewrite manifests | after bulk writes | `CALL {catalog}.system.rewrite_manifests('...')` |
| Remove orphan files | monthly | `CALL {catalog}.system.remove_orphan_files(table => '...')` |

## Detecting small files

```sql
SELECT count(*) AS file_count, sum(file_size_in_bytes) / 1024 / 1024 AS size_mb
FROM curated.events.files;
```

If `file_count * 512MB > size_mb * 4`-ish (many files per MB), run
`rewrite_data_files`.

## Snapshot retention policy

- Keep snapshots long enough to cover: time-travel SLA, incremental-read
  consumers, and the maintenance window itself (e.g. 7-30 days).
- `retain_last` >= 1 always — the current snapshot must never expire.

## Scheduling

- Run maintenance as orchestrator tasks (Airflow/Dagster) with the same
  retry/alerting as pipelines — "maintenance never runs" is the classic
  cause of runaway storage cost.
- Maintenance tasks are Tier M: confirmed on first setup, then scheduled
  with owner approval.