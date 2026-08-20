# Cost Control

## Byte-based pricing levers

1. Partition + cluster (the #1 lever).
2. Column pruning (`SELECT` only what is needed).
3. Partition filters in `WHERE` (never scan all history).
4. Materialize hot aggregations (summary tables) instead of rescanning.
5. `dry_run` before every big ad-hoc query.

## INFORMATION_SCHEMA cost queries

```sql
-- top consumers today
SELECT user_email, SUM(total_bytes_processed) AS bytes
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
GROUP BY 1 ORDER BY bytes DESC LIMIT 10;
```

## Slots (capacity pricing)

- Slots are the compute units; a job uses `total_slot_ms`.
- Contention = queued jobs (`state='PENDING'` long).
- Options: reservation sizing, or move low-priority jobs to off-peak.

## Budgets & alerts

- Set BQ budgets + alerts at the project level (Tier M to configure —
  confirmed).
- Alert on daily bytes > baseline * 2 via the observability framework.