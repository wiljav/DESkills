# Warehouse Sizing

## Credit mechanics

- Warehouse size doubles credits/hour: XS=1, S=2, M=4, L=8, XL=16, 2XL=32...
- Query time + warehouse size = cost. A 2x bigger warehouse halves query
  time at the same cost for single queries.
- `AUTO_SUSPEND` is the dominant idle-cost control.

## Scaling rules

1. Start X-SMALL; run the workload.
2. If queries take too long: scale up (not out) for single-query latency.
3. If many concurrent queries queue: multi-cluster
   (`MAX_CLUSTER_COUNT > 1`) for throughput.
4. Monitor `QUERY_HISTORY` for `QUEUE_OVERFLOW`/waiting states — that is
   the signal to scale.

## Multi-clustering

```sql
ALTER WAREHOUSE de_wh SET MIN_CLUSTER_COUNT = 1 MAX_CLUSTER_COUNT = 4;
```

- Clusters add concurrency, not speed per query.
- Auto-scaling runs on demand; cost is per cluster-hour.

## Per-workload warehouses

| Workload | Warehouse |
| --- | --- |
| ingest/COPY | small, short-lived |
| transformation | sized to the heaviest model |
| BI/analytics | multi-cluster for concurrency |

Isolating workloads prevents one BI dashboard from starving the nightly
build.
