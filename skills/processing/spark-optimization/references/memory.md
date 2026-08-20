# Memory Model

## Executor memory breakdown

| Region | Purpose |
| --- | --- |
| Spark memory (unified) | execution (shuffle, join buffers) + storage (cached RDDs) |
| User memory | UDF/user structures |
| Reserved | framework overhead |
| Overhead (`spark.executor.memoryOverhead`) | JVM overhead, containers, native libs |

## The unified pool

- Execution and storage share one pool; execution can evict cached storage.
- Cache tables deliberately (`df.cache()`/`persist`) only when reused across
  actions; otherwise caching wastes memory.
- Spill: when execution memory is exhausted, Spark spills shuffle data to
  disk (`spark.local.dir`). Spill is the #1 symptom of memory misconfiguration.

## Tuning rules

1. Start from the container budget: for `spark.executor.memory=4g`, set
   `spark.executor.memoryOverhead` to ~1g (or 10-20% on managed Spark).
2. Reduce spill by fixing partitioning (fewer, larger tasks) before growing
   memory.
3. `spark.memory.offHeap.enabled` + `spark.memory.offHeap.size` only when the
   workload benefits from off-heap (rare on JVM workloads).
4. Driver memory (`spark.driver.memory`) matters for `collect()` — never
   `collect()` large results; use `df.write` to storage instead.

## Diagnosing from the UI

- Stage page: "Spill (Memory)" vs "Spill (Disk)" — nonzero disk spill means
  memory pressure.
- Executors page: "Shuffle Spill (Disk)" per executor identifies which
  executors are constrained.
- GC time: >10% of task time indicates heap pressure — increase memory or
  reduce per-task allocation.