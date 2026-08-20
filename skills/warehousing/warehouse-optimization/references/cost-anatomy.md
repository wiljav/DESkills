# Cost Anatomy

## BigQuery — pay per byte scanned

- Cost = bytes read by queries (on-demand) or slot-time (reservations).
- Levers in order: partitioning > clustering > column pruning >
  materialization.
- Free tier and flat-rate notes: partition filters on `PARTITION BY` fields
  are the single biggest lever.

## Snowflake — pay per warehouse-second

- Cost = warehouse size x active time; storage is separate and cheap.
- Levers: auto-suspend/resume, sizing to measured need, clustering only
  when needed (clustering services cost credits).
- Idle cost kills: a warehouse left running 24/7 costs ~24x a
  suspend-at-60s warehouse with the same query load.

## Redshift — pay per cluster-hour

- Cost = node count x uptime + storage. Serverless variant charges per
  capacity used.
- Levers: right-size nodes, `ALL` diststyle for dimensions (avoids
  broadcast), vacuum/analyze hygiene, workload queues.
- Redshift is the least elastic: rightsizing requires resize or Serverless.

## Shared rule

- Materialization shifts cost from compute to storage — only when query
  repetition is proven.
- Every optimization must pay for its own complexity: if a change does not
  show up in the baseline metrics, revert it.