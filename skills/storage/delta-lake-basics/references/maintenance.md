# Maintenance & Tuning

## OPTIMIZE

- Bin-packs small files into target-sized files (`delta.targetFileSize`,
  default 1 GB).
- ZORDER on filter-heavy, high-cardinality columns (like a coarse
  co-clustering); max 4 columns, prefer the ones used in `WHERE`.
- OPTIMIZE is safe to schedule weekly; run more often when pipelines emit
  small files.

## VACUUM

- Deletes files no longer referenced (older than the retention window).
- `RETAIN` must exceed: time-travel SLA + log retention + downstream
  readers' lag.
- ALWAYS run `DRY RUN` first and review the file list.
- VACUUM makes deleted files unrecoverable — treat it as destructive.

## File size tuning

- Too many small files: slow scans, metadata cost.
- Too few huge files: poor parallelism for small clusters.
- Target 128 MB-1 GB per file; adjust `delta.targetFileSize` and the
  writer's partitioning accordingly.

## Monitoring

- Table size: `DESCRIBE DETAIL`.
- File count + size distribution: `DESC HISTORY` + files under
  `_delta_log` statistics; alert when file count grows faster than data.
