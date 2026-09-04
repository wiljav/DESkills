---
name: file-ingestion-gcs-s3
metadata:
  category: DataIngestion
description: >-
  Ingests files from object storage (GCS, S3) into lakehouse tables with
  schema inference, partitioning, and validation: file layout design,
  listing strategies, and load patterns. Use when bulk-loading files into
  tables or designing file-based ingestion contracts. Don't use for
  event-stream ingestion (use kafka-connect) or API-based syncs (use
  airbyte-basics or dlt-python-ingestion).
allowed-tools:
  - gcloud
  - aws
  - python
  - duckdb
---

# File Ingestion (GCS/S3)

Most batch pipelines start with files. This skill covers the durable
patterns: where files land, how they are named, how loads detect them, and
how tables stay correct.

## Prerequisites

- Object storage access (GCS or S3) with credentials per the auth skill.
- A target lakehouse/warehouse with table-write access.
- Python with the cloud SDK of choice (`google-cloud-storage`,
  `boto3`).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: listing objects, reading file metadata, previewing
  files, computing checksums.
- **Tier M (mutation)**: moving/deleting files, loading into tables
  (`INSERT`/`OVERWRITE`), and creating staging prefixes. Confirm before any
  destructive move (archiving deletes the file from the inbox).

## Workflow

### 1. Design the Landing Zone

Layout contract (applies to S3 and GCS):

```text
gs://{bucket}/inbox/{source}/{date=YYYY-MM-DD}/{filename}.parquet
```

Rules:

- `inbox` = landing (unprocessed); `archive/` = processed; `quarantine/` =
  rejected files.
- Partition by date at the prefix level — listing becomes the schedule.
- Immutable filenames (UUID suffix) prevent overwrite confusion.

### 2. Discover Files

```bash
gsutil ls gs://{bucket}/inbox/{source}/date=2024-01-01/**
aws s3 ls s3://{bucket}/inbox/{source}/date=2024-01-01/ --recursive
```

Python (boto3):

```python
import boto3

s3 = boto3.client("s3")
keys = [
    obj["Key"]
    for obj in s3.list_objects_v2(Bucket=bucket, Prefix=prefix)["Contents"]
]
```

Rules:

- List with prefixes, never `list all + filter` on huge buckets.
- Track processed keys in the target table metadata
  (`_ingested_at`, `_source_file`) for idempotent re-runs.

### 3. Validate Before Loading

Per file batch:

- Schema: read headers/schema of a sample (`duckdb read_parquet` or the
  engine's schema inference).
- Row counts vs expected (from manifest or `wc -l` for CSV).
- Checksums: compare source object ETag/MD5 against the recorded manifest.

Rejected files go to `quarantine/` with a reason file — never silently
dropped.

### 4. Load into the Table

Partitioned + idempotent pattern (engine-agnostic):

```python
# 1. stage: load new files only
# 2. dedupe by _source_file (files are immutable)
# 3. INSERT into the target partition
```

For lakehouse tables, the engine handles it transactionally:

```python
# Iceberg via Spark
df.writeTo("catalog.raw.events").overwritePartitions()
```

### 5. Mark Processed

After successful load: move files `inbox -> archive/{date}/` (or record
processed keys in a control table).

Rules:

- Move files only after the table commit succeeds — a crash mid-move
  corrupts the at-least-once guarantee.
- Keep a control table (`ingestion.control` with `source_file`, `loaded_at`,
  `row_count`) for audit and re-run safety.

### 6. Verify the Load

```sql
-- expected rows per date
SELECT date, count(*) FROM raw.events WHERE date = '2024-01-01' GROUP BY date;
```

Compare against the manifest; alert on mismatch via the orchestrator.

## Validation

- All inbox files for the window were either loaded or quarantined
  (no orphans).
- Table row counts per partition match the manifest.
- Re-running the load adds 0 duplicate rows (idempotency proven).
- Archive and control table agree.

## Definition of Done

- Landing zone layout documented (inbox/archive/quarantine, naming).
- Discovery + validation pipeline implemented.
- Load is idempotent (dedup by source file) and partitioned.
- Files archived only after commit; control table updated.
- Counts verified; mismatches alerted.

## Reference Directory

- [File Layout Contracts](references/layouts.md): naming, manifests, and
  schema-on-read vs write.
- [Load Patterns](references/load-patterns.md): copy vs external-table vs
  staged load per engine.

## Related Skills

- [Object Storage Basics](../../storage/object-storage-basics/SKILL.md):
  bucket design and lifecycle.
- [dlt (Python) Ingestion](../dlt-python-ingestion/SKILL.md): code-first
  alternative for API-ish sources.
- [Parquet & File Formats](../../storage/parquet-file-formats/SKILL.md):
  what makes files load fast.
