# Delta Log & Transactions

## The transaction log

- `_delta_log/` holds JSON commits; each commit = a transaction (add/remove
  files, metadata, protocol).
- Readers replay the log to build the table snapshot — small log = fast
  opens.
- `DESCRIBE HISTORY` reads the same log; the log IS the audit trail.

## Isolation & conflicts

- Delta uses optimistic concurrency: writers commit only if the table
  version they based on is unchanged.
- Conflicts surface as `ConcurrentAppendException` etc.; retry or design
  around (partition-scoped writes reduce conflicts).

## Log retention

- `delta.logRetentionDuration` (default 30 days) controls log pruning.
- Keeping the log longer = longer time-travel windows; cost is log storage.

## Idempotency mechanics

- Overwrite of the same partition set: two runs converge (last commit
  wins).
- `MERGE` with a deduped source: re-runs produce identical results.
- Appends without dedup: duplicates — the transformation layer must dedup.
