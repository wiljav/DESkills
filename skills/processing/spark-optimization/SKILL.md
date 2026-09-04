---
name: spark-optimization
metadata:
  category: DataProcessing
description: >-
  Tunes Apache Spark jobs: partitioning, joins, memory, shuffles, and file
  sizing to reduce runtime and cost. Use when a Spark job is slow, spilling
  to disk, or generating excessive small files. Don't use for writing new
  jobs (use spark-basics) or diagnosing crashes (use spark-troubleshooting).
allowed-tools:
  - spark-submit
  - pyspark
  - python
---

# Spark Optimization

This skill takes a working-but-slow Spark job and makes it fast: read the
plan, size partitions, fix joins, tune memory, and validate the result.

## Prerequisites

- A running Spark job with the Spark UI accessible (or event logs).
- Baseline measurements: current runtime, shuffle read/write, spill, and
  input size.
- Cluster details: executor count, cores, memory per executor.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `df.explain()`, reading Spark UI metrics, running
  small samples, computing sizes.
- **Tier M (mutation)**: changing cluster configs, `spark.sql.adaptive.*`
  settings that affect execution semantics, and re-running production jobs
  with new configs. Each config change MUST be confirmed and reverted if it
  does not improve the metric.

## Workflow

### 1. Establish the Baseline

Record from the Spark UI (or event logs):

- Total input size and file count.
- Shuffle read/write bytes.
- Spill (memory vs disk) per stage.
- Runtime per stage; the slowest stage is the target.

```python
df.explain("extended")   # confirm plan shape (joins, scans, filters)
```

### 2. Fix Data Skew and Partitioning

Target: each task processes similar-sized partitions.

```python
# repartition by the join key dimension when imbalance is severe
df = df.repartition(F.col("customer_id"))

# reduce tiny files: coalesce on write
df.coalesce(16).write.parquet("s3a://bucket/out/")
```

Rules:

- Check partition count vs input size: aim for ~128-256 MB per partition
  before shuffle.
- `coalesce` for reducing partitions (no shuffle), `repartition` for
  increasing/balancing.
- Never `repartition` to 1 for "simplicity" on large data.

### 3. Optimize Joins

- Confirm join type matches intent; prefer `broadcast` for small tables
  (`spark.sql.autoBroadcastJoinThreshold`, default 10 MB):

```python
from pyspark.sql import functions as F
small = spark.read.parquet("s3a://bucket/dim/")
large.join(F.broadcast(small), "key", "left")
```

- For large joins, verify no skew: group the join key and check the max
  group size. Fix skew with salting or `skewedHint`.
- Filter and select BEFORE the join (pushdown), never after.

### 4. Tune Memory and Shuffle

Set only what the baseline justifies (confirm each):

```bash
spark-submit \
  --conf spark.sql.adaptive.enabled=true \
  --conf spark.sql.adaptive.coalescePartitions.enabled=true \
  --conf spark.sql.shuffle.partitions=256 \
  --conf spark.executor.memoryOverhead=1g \
  job.py
```

Rules:

- AQE (Adaptive Query Execution) is the first lever: it coalesces shuffle
  partitions and switches join strategies at runtime. Enable and measure.
- `spark.sql.shuffle.partitions` should be ~2-4x the executor cores, not a
  magic constant.
- Memory: give `memoryOverhead` for containers; spill SHOULD drop to zero
  after partition fixes.

### 5. Control Output File Sizes

- Set `spark.sql.files.maxPartitionBytes` (default 128 MB) to control read
  partition size.
- Write with target file sizing: Iceberg/Delta support
  `write.parquet.compression` and compaction; for plain Parquet, set
  `spark.sql.adaptive.coalescePartitions.parallelismFirst=false` so
  coalescing targets bytes not tasks.
- Target ~256 MB-1 GB per output file for warehouse-friendly reads.

### 6. Re-measure and Compare

Re-run the job with the new config and compare against the baseline:

| Metric | Baseline | After | Delta |
| --- | --- | --- | --- |
| Runtime | | | |
| Shuffle read (GB) | | | |
| Spill (GB) | | | |
| Output files | | | |

Keep only configs that measurably improved a metric. Revert the rest.

## Validation

- Slowest-stage runtime decreased; total runtime improved or neutral.
- Spill is zero (or strictly reduced) after memory/partition fixes.
- Output file count is within the target range (no small-file storm).
- Row counts and data content are identical before/after optimization
  (compare `df.count()` and a checksum of key columns).

## Definition of Done

- Baseline and after metrics recorded and compared.
- AQE evaluated; configs that improved metrics documented.
- Skew addressed (repartition/salting) if present.
- Output file sizes within target range.
- Data correctness verified post-change.

## Reference Directory

- [Join Strategy Reference](references/joins.md): broadcast, sort-merge,
  skewed joins, and hints.
- [Memory Model](references/memory.md): executor/overhead/spark memory
  breakdown and spill mechanics.

## Related Skills

- [Spark Basics](../spark-basics/SKILL.md): foundations this tuning builds on.
- [Spark Troubleshooting](../spark-troubleshooting/SKILL.md): if tuning
  changes cause failures.
- [Parquet & File Formats](../../storage/parquet-file-formats/SKILL.md):
  file-size and compression interplay with output tuning.
