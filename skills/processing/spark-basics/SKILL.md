---
name: spark-basics
metadata:
  category: DataProcessing
description: >-
  Writes, runs, and debugs PySpark batch jobs against lakehouse tables,
  covering SparkSession configuration, DataFrame API patterns, and reading
  from object storage and warehouses. Use when starting a new Spark job or
  porting an existing one to a new cluster. Don't use for tuning an
  underperforming job (use spark-optimization) or diagnosing failures
  (use spark-troubleshooting).
allowed-tools:
  - spark-submit
  - pyspark
  - python
---

# Apache Spark Basics

Apache Spark is a unified distributed processing engine. This skill covers
the foundation: session setup, DataFrame patterns, I/O with object storage and
warehouses, and local-to-cluster execution.

## Prerequisites

- A Spark distribution or managed Spark (Dataproc, EMR, Databricks, Glue).
- Local `pyspark` for development; a cluster (or session/notebook) for real
  scale.
- Java 17+ installed (`JAVA_HOME` set) — see stack-setup troubleshooting.
- Credentials per `data-engineering-auth` for cloud object stores.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: reading data (`spark.read`), `df.show/explain`,
  local `pyspark` sessions, cluster API calls that only list/inspect.
- **Tier M (mutation)**: writing to shared paths/warehouse tables, `OVERWRITE`
  modes, launching cluster jobs, and installing packages on the cluster. All
  MUST be confirmed; `OVERWRITE` requires stating exactly what will be
  replaced.

## Workflow

### 1. Establish the Session

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("job_name")
    .config("spark.sql.shuffle.partitions", "200")
    .enableHiveSupport()
    .getOrCreate()
)
```

Set `spark.sql.shuffle.partitions` explicitly; the default of 200 is rarely
right for your data size (see spark-optimization).

### 2. Read Data

Object storage (S3/GCS) with file listing and schema inference:

```python
df = spark.read.parquet("s3a://bucket/path/*.parquet")
df = spark.read.format("iceberg").load("catalog.db.table")   # Iceberg catalog
```

Warehouse tables (BigQuery via the Spark BigQuery connector, Snowflake via
the Snowflake connector, JDBC for others). Prefer the native connectors over
JDBC where available; they push down filters.

### 3. Transform with DataFrames

```python
from pyspark.sql import functions as F

result = (
    df.filter(F.col("status") == "active")
    .groupBy("customer_id")
    .agg(F.sum("amount").alias("total"))
)
```

Rules:

- Prefer the DataFrame API and SQL over UDFs; UDFs break optimization and
  serialization (see spark-optimization).
- Verify logic on a sample before full-cluster runs.
- Keep transformations in functions (pure, testable) instead of a long
  top-level script.

### 4. Write Output

```python
result.write.mode("overwrite").partitionBy("date").parquet("s3a://bucket/out/")
```

Rules:

- Explicit `mode`: `overwrite` (MUST be confirmed), `append`, `errorifexists`,
  or `ignore`. Never default to silent overwrite.
- Partition on low-cardinality, filterable columns (`date`, `region`), never
  on high-cardinality keys.
- For lakehouse tables prefer `df.writeTo("catalog.db.table")` (Iceberg) or
  Delta `df.write.format("delta")` so commits are transactional.

### 5. Run and Verify

Local:

```bash
spark-submit --master local[4] job.py
```

Cluster (after confirmation):

```bash
spark-submit --master yarn --deploy-mode cluster job.py
```

Verify:

- The job's `stages` complete; shuffle spill = 0 (see spark-optimization).
- Output location contains the expected partitions/files.
- Row counts match expectations; spot-check with `df.count()`.

## Validation

- Read of source data matches source expectations (schema, row count).
- Transformation outputs pass the pipeline's quality checks (see the quality
  skills).
- Job completes with no failed tasks and no spill to disk.
- Output written to the confirmed target with the confirmed mode.

## Definition of Done

- SparkSession configured with explicit shuffle partitions.
- Job is a set of pure, testable transformations (no UDFs unless justified).
- Output mode is explicit and was confirmed for overwrites.
- Job ran successfully; row counts verified; output inspected.
- No credentials in code; storage/writer config resolved via the session's
  cluster credentials.

## Reference Directory

- [Core Concepts](references/core-concepts.md): RDD vs DataFrame vs SQL,
  stages/tasks, and execution model.
- [I/O Patterns](references/io-patterns.md): connectors for object storage,
  warehouses, and lakehouse formats.

## Related Skills

- [Spark Optimization](../spark-optimization/SKILL.md): make the job fast.
- [Spark Troubleshooting](../spark-troubleshooting/SKILL.md): when runs fail.
- [Parquet & File Formats](../../storage/parquet-file-formats/SKILL.md):
  choose the right file format for reads/writes.
