---
name: iceberg-basics
metadata:
  category: StorageAndLakehouse
description: >-
  Creates and manages Apache Iceberg tables: catalogs, snapshots, time
  travel, schema evolution, and maintenance. Use when building lakehouse
  tables with open table format or migrating existing Parquet to Iceberg.
  Don't use for Delta-specific features (use delta-lake-basics) or for
  choosing a format (see metadata-catalog-comparison).
allowed-tools:
  - python
  - spark-sql
  - duckdb
---

# Apache Iceberg Basics

Iceberg is an open table format for huge analytic tables: ACID
commits, time travel, schema evolution, and hidden partitioning on object
storage.

## Prerequisites

- Object storage (see object-storage-basics) and a catalog: REST catalog,
  Hive Metastore, Glue, or a file-based catalog.
- An engine with Iceberg support: Spark 3.3+, Flink, Trino, DuckDB
  (`iceberg` extension), or pyiceberg.
- Catalog credentials per the auth skill.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `DESCRIBE TABLE`, `SHOW SNAPSHOTS`, time-travel
  reads, catalog listings.
- **Tier M (mutation)**: `CREATE TABLE`, writes, `EXPIRING SNAPSHOTS`,
  `DELETE FILES`, schema evolution, and dropping tables. Dropping or
  expiring snapshots removes data — MUST be confirmed with the blast radius
  stated.

## Workflow

### 1. Create a Catalog

REST catalog (the modern default):

```bash
# example: dockerized Iceberg REST catalog for dev
docker run -p 8181:8181 tabulario/iceberg-rest
```

```python
from pyiceberg.catalog import load_catalog

catalog = load_catalog(
    "rest",
    uri="http://localhost:8181",
    warehouse="s3://{bucket}/warehouse",
)
```

Register namespaces per zone: `raw`, `curated`.

### 2. Create Tables

Spark SQL:

```sql
CREATE TABLE curated.events (
    event_id  STRING,
    customer_id STRING,
    amount    DECIMAL(12,2),
    event_date DATE
)
USING iceberg
PARTITIONED BY (event_date);
```

Rules:

- `PARTITIONED BY` uses hidden partitioning — filters on the column prune
  automatically regardless of partition layout.
- Partition on low-cardinality, filter-heavy columns.
- Define `write.target-file-size-bytes` (default 512 MB) per workload.

### 3. Write Data Transactionally

```python
# Spark
df.writeTo("curated.events").overwritePartitions()
```

- Writes commit atomically: readers never see partial data.
- `overwritePartitions` replaces only the affected partitions — the
  idempotent pattern for reruns.

### 4. Use Time Travel and Incremental Reads

```sql
SELECT * FROM curated.events
AS OF VERSION {snapshot_id};

SELECT * FROM curated.events
FOR SYSTEM_TIME AS OF '2024-01-01T00:00:00Z';

-- incremental: rows changed since a snapshot
SELECT * FROM curated.events
FOR VERSION AS OF {base} VERSION AFTER {snapshot};
```

Rules:

- Time travel works only within `snapshot retention` — expired snapshots
  are gone (see maintenance).
- Use incremental reads for downstream incremental pipelines.

### 5. Maintain the Table

```sql
CALL {catalog}.system.expire_snapshots(
  table => 'curated.events',
  older_than => TIMESTAMP '2024-01-01',
  retain_last => 1);

CALL {catalog}.system.rewrite_data_files(
  table => 'curated.events',
  strategy => 'binpack');

CALL {catalog}.system.rewrite_manifests('curated.events');
```

Schedule maintenance:

- `expire_snapshots`: daily (or per retention policy).
- `rewrite_data_files`: weekly when small files accumulate.
- `rewrite_manifests`: after bulk writes.
- `remove_orphan_files`: monthly.

### 6. Evolve the Schema

```sql
ALTER TABLE curated.events ADD COLUMN country STRING;
ALTER TABLE curated.events RENAME COLUMN customer_id TO cust_id;
```

- Additive changes are safe and cheap.
- Renames/drops affect consumers — coordinate via data contracts.

## Validation

- Table created in the right namespace with the right partitions.
- A write commit is atomic (concurrent readers saw old or new, never
  partial).
- Time travel returns the expected historical snapshot.
- Maintenance ran; snapshot retention matches policy.

## Definition of Done

- Catalog configured; namespaces match the platform zones.
- Tables created with hidden partitioning and target file size.
- Writes idempotent via `overwritePartitions` or merge patterns.
- Maintenance scheduled (expire/rewrite); retention policy documented.
- Schema evolution used deliberately with consumer coordination.

## Reference Directory

- [Catalog Options](references/catalogs.md): REST vs Hive vs Glue vs
  Nessie/Dremio.
- [Maintenance Playbook](references/maintenance.md): exact maintenance
  commands and cadence per workload.

## Related Skills

- [Delta Lake Basics](../delta-lake-basics/SKILL.md): the other mainstream
  format.
- [Metadata Catalog Comparison](../../governance/metadata-catalog-comparison/SKILL.md):
  choosing catalogs.
- [Parquet & File Formats](../parquet-file-formats/SKILL.md): the file layer
  under Iceberg.