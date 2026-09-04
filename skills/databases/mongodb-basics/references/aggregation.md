# Aggregation & Extraction

## Pipeline stage order

1. `$match` — prune with indexed fields FIRST.
2. `$project` — drop heavy fields early (smaller intermediate docs).
3. `$unwind` — flatten arrays when the target is tabular.
4. `$group` — aggregate.
5. `$sort` / `$limit` — last, cheap once data is small.

## Flattening for the warehouse

```js
// nested -> columns
db.orders.aggregate([
  { $match: { created_at: { $gte: cutoff } } },
  { $project: {
      order_id: "$_id",
      customer_id: 1,
      "address.city": "$address.city",
      items_count: { $size: "$items" },
  } },
]);
```

- Flatten depth to match the target schema; keep arrays as-is if the
  warehouse supports nested types (BigQuery/Snowflake VARIANT).
- Deterministic projection order: schema drift in downstream consumers is
  prevented by fixed projections.

## Change streams vs batch

| | Change streams | Batch export |
| --- | --- | --- |
| Latency | near-real-time | scheduled |
| Volume | moderate | any |
| Completeness | needs resumeToken discipline | full-scan reliable |
| Use | operational serving | analytics ingest |

## Resume tokens

- Persist `resumeToken` with the pipeline run (offset store).
- Resume on restart: `watch(pipeline, { resumeAfter: token })`.
- Tokens expire from the oplog — monitor lag like binlog retention.
