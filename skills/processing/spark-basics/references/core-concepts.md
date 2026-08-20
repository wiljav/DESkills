# Core Concepts

## Execution model

- A job = one action (`count`, `write`, `show`). Actions trigger execution;
  transformations are lazy.
- A job is split into **stages** at wide dependencies (shuffles); stages are
  split into **tasks**, one per partition.
- Plan inspection: `df.explain("extended")` shows the logical and physical
  plans. Use it before running anything non-trivial.

## DataFrame vs RDD vs SQL

| API | When to use |
| --- | --- |
| DataFrame/SQL | 95% of batch work; optimizer (Catalyst) applies predicate pushdown, join reorder |
| RDD | custom partitioning, low-level control; almost never needed |
| UDFs | only when SQL functions cannot express the logic — they block optimization and add serialization cost |

## Shuffle

- A shuffle transfers data across executors when grouping/joining/repartitioning.
- Shuffle size is governed by `spark.sql.shuffle.partitions` (default 200).
- Visible as "Shuffle Write/Read" in the UI; spill means shuffle exceeded
  memory.

## Catalogs

- Hive Metastore / Glue / Unity Catalog / Iceberg REST catalogs let Spark
  resolve `db.table` names to storage locations.
- Prefer catalog-backed tables over raw path reads: schema and partitioning
  are managed, and lakehouse formats give ACID commits.