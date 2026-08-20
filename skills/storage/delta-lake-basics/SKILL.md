---
name: delta-lake-basics
metadata:
  category: StorageAndLakehouse
description: >-
  Uses Delta Lake tables for ACID transactions, versioning, and time
  travel in lakehouse pipelines: table creation, writes, merge, vacuum,
  and migration from Parquet. Use when building on Delta (Databricks,
  OSS Spark, or standalone) or migrating existing Parquet workloads. Don't
  use for Iceberg-specific catalogs (use iceberg-basics).
allowed-tools:
  - spark-sql
  - python
---

# Delta Lake Basics

Delta Lake is an open storage layer with ACID transactions, scalable
metadata, and time travel on top of Parquet files, driven by a
transaction log.

## Prerequisites

- Spark with Delta (`spark-sql --packages io.delta:delta-spark_2.12:{version}`)
  or Databricks runtime; the standalone `delta-rs` for non-Spark engines.
- Object storage per object-storage-basics.
- Catalog/credentials per the auth skill.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `DESCRIBE HISTORY`, `DESCRIBE DETAIL`,
  time-travel reads, `VACUUM DRY RUN`.
- **Tier M (mutation)**: `CREATE`, writes, `MERGE`, `VACUUM`, `RESTORE`,
  and `DELETE` statements. `VACUUM` physically deletes old files and
  `RESTORE` replaces table data — confirm with the blast radius stated.

## Workflow

### 1. Create a Delta Table

```sql
CREATE TABLE curated.events (
    event_id  STRING,
    customer_id STRING,
    amount    DECIMAL(12,2),
    event_date DATE
)
USING delta
PARTITIONED BY (event_date)
LOCATION 's3://{bucket}/warehouse/curated/events';
```

Rules:

- `PARTITIONED BY` on low-cardinality filter columns.
- `LOCATION` explicit for lakehouse tables; catalog tracks the location.
- Optionally set `delta.targetFileSize` for file sizing.

### 2. Write Data Idempotently

```python
# Spark
df.write.format("delta").mode("overwrite").option("overwriteSchema", "false") \
  .partitionBy("event_date") \
  .save("s3://{bucket}/warehouse/curated/events")
```

Rules:

- Overwrite replaces whole table/partition set — the idempotent choice for
  full-window recompute.
- Never mix `overwriteSchema` on by default; schema changes are explicit.

### 3. Use MERGE for Upserts

```sql
MERGE INTO curated.events AS t
USING updates AS u
ON t.event_id = u.event_id AND t.event_date = u.event_date
WHEN MATCHED THEN UPDATE SET t.amount = u.amount
WHEN NOT MATCHED THEN INSERT *;
```

- `MERGE` is the recommended CDC/upsert path — it is transactional and
  idempotent when the source is deduped.
- Keep the `ON` condition keyed on the table's natural key.

### 4. Time Travel and History

```sql
SELECT * FROM curated.events VERSION AS OF 12345;
SELECT * FROM curated.events TIMESTAMP AS OF '2024-01-01T00:00:00';

DESCRIBE HISTORY curated.events LIMIT 10;
```

Rules:

- History is retained per `delta.logRetentionDuration` (default 30d);
  beyond that, only `VACUUM` keeps files (it does not, by design — vacuumed
  files are unrecoverable).
- Never rely on `VACUUM`-protected files for long-term recovery; back up
  via snapshots/export instead.

### 5. Maintain the Table

```sql
VACUUM curated.events RETAIN 168 HOURS;   -- delete files older than 7d
VACUUM curated.events RETAIN 168 HOURS DRY RUN;  -- preview first
OPTIMIZE curated.events;                  -- compact small files
OPTIMIZE curated.events ZORDER BY (customer_id);  -- clustering for filters
```

Schedule:

- `OPTIMIZE`: weekly (or when small files detected).
- `VACUUM`: after OPTIMIZE; retention >= the max snapshot-retention SLA.
- Run `VACUUM ... DRY RUN` before every real vacuum (preview what is
  deleted).

### 6. Migrate from Parquet

```sql
CREATE TABLE curated.events_clean
USING delta
AS SELECT * FROM parquet.`s3://{bucket}/legacy/events/`;
```

Rules:

- Migrate in a maintenance window; validate row counts + schemas before and
  after.
- For live pipelines use the Delta streaming/CDC patterns instead of a
  one-shot copy.

## Validation

- Table created; partition pruning works (query on `event_date` scans only
  that partition).
- Writes are ACID: concurrent readers see a consistent snapshot.
- `DESCRIBE HISTORY` shows the expected commits; time travel returns the
  expected version.
- `OPTIMIZE` reduced file count; `VACUUM DRY RUN` output reviewed before the
  real run.

## Definition of Done

- Tables created with explicit partitioning and locations.
- Writes idempotent; upserts via `MERGE` where needed.
- Maintenance (OPTIMIZE/VACUUM) scheduled with DRY RUN discipline.
- Migration (if any) validated with counts and schema diff.
- Retention policy documented (log retention vs vacuum window).

## Reference Directory

- [Delta Log & Transactions](references/log-transactions.md): how the log
  works, isolation levels, and conflict handling.
- [Maintenance & Tuning](references/maintenance.md): OPTIMIZE/ZORDER/
  VACUUM details and file sizing.

## Related Skills

- [Iceberg Basics](../iceberg-basics/SKILL.md): the alternative open format.
- [Spark Basics](../../processing/spark-basics/SKILL.md): the engine doing
  the writes.
- [Metadata Catalog Comparison](../../governance/metadata-catalog-comparison/SKILL.md):
  catalog choices around Delta.