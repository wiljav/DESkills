# Engine-Specific Levers

| Lever | BigQuery | Snowflake | Redshift |
| --- | --- | --- | --- |
| Partitioning | `PARTITION BY date` (required on big tables) | `CLUSTER BY` (optional) | `SORTKEY` + zone maps |
| Clustering | `CLUSTERING FIELDS` (max 4) | `CLUSTER BY` on filter columns | `DISTKEY`/`SORTKEY` |
| Materialization | `CREATE MATERIALIZED VIEW` | `MATERIALIZED VIEW` / `TASK` refreshes | `CREATE MATERIALIZED VIEW` (auto-refresh) |
| Column pruning | `SELECT` columns only | same | same |
| Join tuning | auto-optimized; dedupe keys | same | distkey alignment; `DS_DIST` removal |
| Compute | slots/reservations | warehouse size + multi-cluster | node count / `ALL` diststyle |

## Cross-engine notes

- BigQuery: partitioning is mandatory practice; clustering is the fine
  tuning. Cost = bytes scanned.
- Snowflake: clustering is optional and adds maintenance cost — only when
  measured need exists. Cost = warehouse seconds.
- Redshift: design at table creation; retrofitting means table rebuild.
  Cost = cluster hours + storage.

## Priority mapping

| Symptom | Lever |
| --- | --- |
| Scanning too much data | partitioning/clustering/sort keys |
| Reading too many columns | column pruning |
| Same query repeatedly | materialize |
| Slow joins | key alignment, dedupe |
| Queue waits (BQ/Snowflake) | compute sizing |
