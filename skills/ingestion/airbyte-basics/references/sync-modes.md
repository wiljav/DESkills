# Sync Modes & Cursors

## Modes

| Mode | Semantics | Best for |
| --- | --- | --- |
| Full refresh | delete + reload whole stream | small/stateless |
| Incremental append | only rows with cursor > last state | append-only logs |
| Incremental dedup | upsert by PK (destinations supporting it) | mutable entities |

## Cursor rules

- Cursor column MUST be monotonically increasing (`updated_at`, `id`).
- Rows with cursor == state may be skipped on re-sync — use
  `cursor granularity`/`date_format` correctly to avoid losing same-timestamp
  rows.
- Deletes are invisible to incremental append: if sources delete rows,
  choose full refresh or dedup mode, or emit tombstones.

## State and resets

- Connection state is stored per stream; `reset` deletes destination data
  and resets cursors — confirm before running.
- After a source schema change that invalidates the cursor, a reset +
  full re-sync is the only clean path; schedule it in a maintenance window.

## Validation of incremental

After two consecutive syncs:

- Second sync emitted 0 rows when the source is unchanged.
- Adding one source row then syncing emits exactly 1 row.
- Destination `_airbyte_emitted_at` matches sync windows.