# I/O Patterns

## Object storage

- S3: use the Hadoop AWS connector (`s3a://`) or the native S3A faster
  options; set `fs.s3a.path.style.access=true` for EMRFS-compatible layouts.
- GCS: `gs://` via the GCS connector jar; pass `google.cloud.auth.service.account.enable=true`
  when using a key file (short-lived preferred).
- Always read directories (`s3a://b/prefix/*.parquet`) rather than
  per-file loops; Spark lists and parallelizes internally.

## Warehouses

- BigQuery: `com.google.cloud.spark.bigquery` — pushdown of filters and
  column pruning; set `materializationDataset` explicitly.
- Snowflake: Snowflake Spark connector; pass `sfDatabase`, `sfSchema`,
  `sfWarehouse`; prefer stage-based I/O.
- JDBC: last resort; use `fetchsize` and `numPartitions` bounds; never read a
  whole table with a single partition.

## Lakehouse formats

| Format | Read | Write | Notes |
| --- | --- | --- | --- |
| Iceberg | `format("iceberg")` | `df.writeTo("catalog.db.t")` | transactional, time travel |
| Delta | `format("delta")` | `df.write.format("delta")` | ACID, vacuum |
| Hudi | `format("hudi")` | with `hoodie.datasource.write.*` opts | upserts |

## Partitioning writes

- Partition on columns with low cardinality relative to row count
  (date/region), and columns actually used in filters.
- Avoid over-partitioning: a partition with tiny files defeats predicate
  pruning and bloats metadata.