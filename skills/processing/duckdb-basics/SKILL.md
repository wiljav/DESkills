---
name: duckdb-basics
metadata:
  category: DataProcessing
description: >-
  Uses DuckDB for local analytics, in-process OLAP, and zero-copy queries
  over Parquet and other files: installation, query patterns, and extension
  usage. Use when analyzing data locally or embedding analytics in scripts.
  Don't use for distributed workloads or large-cluster processing (use
  spark-basics) or as a production serving warehouse.
allowed-tools:
  - duckdb
  - python
---

# DuckDB Basics

DuckDB is an in-process analytical database with zero external dependencies,
designed for local analysis and embedding. This skill covers setup, querying,
and the extensions that make it a daily driver in data engineering.

## Prerequisites

- `duckdb` CLI or Python package installed (`pip install duckdb` /
  `uv tool install duckdb`).
- Data files (Parquet, CSV, JSON) accessible locally or via object storage
  extensions.
- Enough local RAM for the working set; DuckDB is memory-bound.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `SELECT` queries, `DESCRIBE`, `EXPLAIN`, and
  reading files.
- **Tier M (mutation)**: `CREATE`/`INSERT`/`UPDATE`/`DELETE` against
  persistent databases, `COPY` to shared paths, and installing extensions
  that write. Must be confirmed; DuckDB has no multi-user locking — writes
  can clobber.

## Workflow

### 1. Start DuckDB

```bash
duckdb my_analysis.duckdb
# or in-memory
duckdb
```

Python:

```python
import duckdb
con = duckdb.connect("my_analysis.duckdb")
```

### 2. Query Files Directly

```sql
SELECT region, count(*)
FROM read_parquet('/data/events/*.parquet')
WHERE status = 'active'
GROUP BY region;
```

- `read_parquet`, `read_csv` (auto-detect), `read_json` — no load step
  required.
- Globs supported: `read_parquet('/data/*/part-*.parquet')`.

### 3. Use the Object Storage Extensions

```sql
INSTALL httpfs; LOAD httpfs;
SELECT * FROM read_parquet('s3://bucket/prefix/*.parquet');
SELECT * FROM read_parquet('gs://bucket/prefix/*.parquet');
```

Set credentials via `SET s3_region`, `SET s3_access_key_id`, etc. — from
environment variables, never literals (see auth skill).

### 4. Zero-Copy Joins Between Sources

```sql
CREATE TEMP TABLE dim AS SELECT * FROM read_parquet('dim.parquet');
SELECT e.customer_id, d.name
FROM read_parquet('events/*.parquet') e
JOIN dim d USING (customer_id);
```

DuckDB optimizes this into a single fused scan; no data movement.

### 5. Analyze and Export

```sql
COPY (SELECT * FROM read_parquet('events/*.parquet')) TO 'summary.csv' (HEADER, DELIMITER ',');
```

Python integration for reports:

```python
df = con.execute("SELECT * FROM read_parquet('events/*.parquet')").df()
```

## Validation

- Query results match an independent count (e.g. `wc -l` on CSV, or a second
  engine for a sample).
- Explain plans show the expected join/scan strategy
  (`EXPLAIN ANALYZE SELECT ...`).
- No secrets in queries or config; credentials via env vars.

## Definition of Done

- DuckDB CLI/Python available; extensions loaded for the data source.
- Queries produce verified results; exports validated.
- Working files (`.duckdb`) not committed to the repo; data accessed
  read-only unless confirmed otherwise.

## Reference Directory

- [Query Patterns](references/query-patterns.md): window functions, PIVOT,
  and the SQL dialect notes.
- [Extensions](references/extensions.md): httpfs, postgres, iceberg, and
  spatial usage.

## Related Skills

- [Parquet & File Formats](../../storage/parquet-file-formats/SKILL.md):
  formats DuckDB reads natively.
- [Spark Basics](../spark-basics/SKILL.md): when the workload outgrows local
  memory.
- [Data Engineering Stack Setup](../../platform/de-stack-getting-started/SKILL.md):
  installation context.
