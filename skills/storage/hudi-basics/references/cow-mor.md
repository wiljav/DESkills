# COW vs MOR

| | Copy-on-write (COW) | Merge-on-read (MOR) |
| --- | --- | --- |
| Write cost | higher (rewrite files) | lower (append log) |
| Read cost | low | higher until compaction |
| Freshness | immediate | requires compaction for base-file reads |
| Best for | read-heavy analytics, BI | write-heavy ingest, high-velocity upserts |

## Rules

- COW is the default for analytics tables.
- MOR when ingest rate > 10k upserts/s or writes dominate reads; schedule
  compaction in off-peak windows.
- MOR reads before compaction see log files merged on read — keep log
  growth bounded by compaction cadence.

## Migration

- Changing type requires table rewrite (`hoodie.datasource.write.operation`
  with full re-materialization); do it in a maintenance window with count
  validation.