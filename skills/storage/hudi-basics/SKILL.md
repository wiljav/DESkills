---
name: hudi-basics
metadata:
  category: StorageAndLakehouse
description: >-
  Manages Apache Hudi tables for incremental upserts and table services on
  lakehouse data: copy-on-write vs merge-on-read, indexing, clustering,
  and compaction. Use when working with Hudi tables or workloads needing
  frequent upserts on object storage. Don't use for other lakehouse formats
  (use iceberg-basics or delta-lake-basics).
allowed-tools:
  - spark-sql
  - python
---

# Apache Hudi Basics

Apache Hudi (Hadoop Upserts Deletes and Incrementals) is a lakehouse table
format optimized for fast upserts and incremental reads on object storage.

## Prerequisites

- Spark with the Hudi bundle (`--packages org.apache.hudi:hudi-spark3.4-bundle_2.12:{version}`)
  or a Hudi-enabled platform (EMR/Databricks).
- Object storage per object-storage-basics.
- Credentials per the auth skill.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `DESCRIBE`, `SHOW COMMIT`, time-travel reads,
  `clustering plan`/`compaction plan` previews.
- **Tier M (mutation)**: writes, upserts, `delete` ops, compaction and
  clustering runs, and table drops. Compaction/clustering rewrite files and
  MUST be confirmed when first scheduled.

## Workflow

### 1. Create a Hudi Table

```sql
CREATE TABLE curated.events (
    event_id  STRING,
    customer_id STRING,
    amount    DECIMAL(12,2),
    event_date DATE,
    PRIMARY KEY (event_id) NOT ENFORCED
)
USING hudi
PARTITIONED BY (event_date)
OPTIONS (
  type = 'cow',
  hoodie.index.type = 'BLOOM',
  hoodie.table.keygenerator.class = 'org.apache.hudi.keygen.SimpleKeyGenerator'
)
LOCATION 's3://{bucket}/warehouse/curated/events';
```

Rules:

- Table type: `cow` (copy-on-write) for read-heavy analytics;
  `mor` (merge-on-read) for write-heavy upserts.
- `PRIMARY KEY` + key generator define upsert identity — choose
  `SimpleKeyGenerator` (single key) or `ComplexKeyGenerator` (composite).

### 2. Write and Upsert

```python
df.write.format("hudi") \
  .option("hoodie.datasource.write.operation", "upsert") \
  .option("hoodie.datasource.write.recordkey.field", "event_id") \
  .option("hoodie.datasource.write.precombine.field", "updated_at") \
  .option("hoodie.datasource.write.partitionpath.field", "event_date") \
  .mode("append") \
  .save("s3://{bucket}/warehouse/curated/events")
```

- `precombine.field` decides the winner when two records share a key —
  MUST be a monotonic timestamp.
- Operations: `upsert`, `insert`, `bulk_insert`, `delete`.

### 3. Read Incrementally

```sql
SELECT * FROM hudi_events
WHERE _hoodie_commit_time > '{last_commit}';
```

Rules:

- Incremental reads need a recorded last commit (`SHOW COMMIT` /
  `call show_commit_metadata`).
- `_hoodie_commit_time` is Hudi's internal watermark — do not invent your
  own from wall time.

### 4. Run Table Services

Compaction (MOR only):

```bash
spark-submit --packages org.apache.hudi:{bundle} \
  --class org.apache.hudi.utilities.HoodieCompactor \
  --props compaction.properties
```

Clustering (COW/MOR):

```bash
spark-submit --packages org.apache.hudi:{bundle} \
  --class org.apache.hudi.utilities.HoodieClusteringJob \
  --props clustering.properties
```

Schedule: compaction based on log growth; clustering when small files
accumulate. Preview plans (`compaction plan`, `clustering plan`) before
runs.

### 5. Clean and Archive

- `HoodieCleaner` removes old file versions per
  `hoodie.cleaner.policy`/`retainCommits` — run on schedule.
- Archival moves old commits to `_archive` (bounded metadata).

## Validation

- Table created with the right type/index/key-gen; upserts land correctly
  (same key re-written -> one row, latest precombine wins).
- Incremental read returns exactly the delta since the last commit.
- Compaction/clustering plans reviewed; runs completed without errors.
- Cleaner/archiver logs confirm bounded metadata.

## Definition of Done

- Table type and index chosen deliberately (cow vs mor).
- Upsert semantics verified (record key + precombine).
- Incremental read pattern documented and working.
- Table services scheduled with plan-preview discipline.

## Reference Directory

- [COW vs MOR](references/cow-mor.md): when each table type wins.
- [Indexing & Key Generation](references/indexing.md): bloom vs bucket vs
  HBase index.

## Related Skills

- [Delta Lake Basics](../delta-lake-basics/SKILL.md): alternative upsert
  semantics via MERGE.
- [Spark Basics](../../processing/spark-basics/SKILL.md): the engine.
- [Metadata Catalog Comparison](../../governance/metadata-catalog-comparison/SKILL.md):
  catalog integration.
