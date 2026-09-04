# Incremental State Deep Dive

## Where state lives

- Destination table `_dlt_pipeline_state` holds per-pipeline state (keys:
  resource name -> last cursor).
- `dlt pipeline state` / `show` displays it read-only.

## Reset paths

| Action | Effect | When |
| --- | --- | --- |
| delete state row for a resource | next run starts from `initial_value` | source history lost or cursor broken |
| `--full-refresh` | wipe destination + state | dev only |

Rules:

- Resetting state does NOT replay history — after reset, set
  `initial_value` to the oldest needed date and run a full load.
- NEVER reset state while consumers depend on the destination table
  without agreement (missing data window).

## Multi-resource coordination

- Resources with different cadences keep separate cursors — fine.
- For "load everything atomically" pipelines, run all resources in one
  pipeline run; partial failure leaves completed resources' state intact.

## Failure behavior

- Failed loads leave state at the last checkpoint: re-running resumes from
  there — no duplicates for `merge`, possible duplicates for `append`
  (dedup in transformation layer).
