# Idempotency Patterns

## The three write patterns

| Pattern | Use | Rerun result |
| --- | --- | --- |
| Partition overwrite | full recompute of a window | identical (last wins) |
| MERGE/upsert | CDC / daily snapshots | identical (deduped) |
| Append | event log / raw bronze | DUPLICATES — never use alone |

## Rules

- Every DAG task's output must be reproducible: rerun today = rerun
  yesterday's results.
- Bronze: partition-scoped replace (re-ingest same window = same files).
- Silver: dedupe key defined (natural key); upsert or overwrite per
  window.
- Gold: derived from silver — idempotent if silver is.

## Proven pattern (windowed)

1. Compute the window (e.g. `event_date = yesterday`).
2. Overwrite that partition in the target.
3. Test the partition after write (row count vs source window count).

## Backfill

- `catchup=True` + windowed overwrite = backfill is just re-running dates.
- Never backfill with append semantics — you will ship duplicates and
  the dedup cost lands on consumers.