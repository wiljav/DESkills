# Join Strategy Reference

## Join types

| Join | When Spark picks it | When you should force it |
| --- | --- | --- |
| Broadcast hash join | one side < `autoBroadcastJoinThreshold` (10 MB) | small dimensions, lookup tables |
| Sort-merge join | both large, keys sortable | default for big joins |
| Shuffled hash join | AQE decides by size | rare |
| Broadcast nested loop | no join condition | only for cartesian (avoid) |

## Hints

```python
from pyspark.sql import functions as F

# force broadcast when Spark underestimates a small table
small.join(F.broadcast(dim), "key", "left")

# merge hint for large joins that must not broadcast
large1.join(large2.hint("merge"), "key")
```

Rules:

- Broadcasting a table larger than the threshold is usually a regression:
  the driver serializes the whole table to every executor.
- AQE (`spark.sql.adaptive.enabled=true`) re-evaluates strategies at runtime
  using measured sizes — prefer AQE over manual hints.

## Skewed joins

Symptom: one or a few tasks run far longer than the rest of the stage.

Diagnosis:

```python
large.groupBy("key").count().orderBy(F.desc("count")).show(10)
```

Fixes:

1. Filter the hot keys and join them separately (two-path join).
2. Salt the hot keys: add a random suffix to both sides on the hot keys.
3. Use `skewedHint`/`shuffle` hints on the join when the engine supports it
   (Spark 3.3+ AQE skew join with `spark.sql.adaptive.skewJoin.enabled=true`).

Always re-measure after fixing skew; the slowest task time is the metric that
matters.