---
name: parquet-file-formats
metadata:
  category: StorageAndLakehouse
description: >-
  Chooses and optimizes Parquet, ORC, Avro, and compression for analytic
  workloads: file layout, encoding, and when each format wins. Use when
  designing file formats for tables or diagnosing slow scans. Don't use for
  table-format questions (use iceberg/delta/hudi) or bucket design (use
  object-storage-basics).
allowed-tools:
  - python
  - duckdb
  - parquet-tools
---

# Parquet & File Formats

Columnar file formats determine scan speed, compression ratio, and schema
evolution. This skill covers the decision and the knobs that matter.

## Prerequisites

- Data being designed or diagnosed (files, tables, or a workload spec).
- `duckdb` (zero-copy inspection), `pyarrow`/`fastparquet`, and optionally
  `parquet-tools`/`parquet-cli`.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: inspecting files (`parquet-tools schema`,
  `duckdb DESCRIBE`, footer stats), measuring sizes, comparing formats on
  samples.
- **Tier M (mutation)**: rewriting files into a new format/compression,
  changing writer settings in pipelines. Rewrites touch shared data — confirm
  and validate counts before/after.

## Workflow

### 1. Choose the Format

| Format | Shape | Use |
| --- | --- | --- |
| Parquet | columnar | default for analytics/lakehouse |
| ORC | columnar | Hive/older ecosystems (best when the fleet is Hive-native) |
| Avro | row | write-heavy pipelines, event streaming, schema-evolution-first |
| CSV/JSON | text | interop only — never analytics serving |

Rules:

- Parquet for anything scanned by analytics engines.
- Avro for streaming/Kafka payloads where write cost matters.
- Never serve analytics from CSV/JSON directly.

### 2. Pick Compression

| Codec | Ratio | CPU | Use |
| --- | --- | --- | --- |
| snappy | medium | low | default for hot data |
| zstd | high | medium | archive/cold data; often worth it |
| gzip | high | high | legacy compatibility |
| lz4 | low | very low | write-heavy ingest |

Rules:

- zstd is the modern default for lakehouse tables (Delta/Iceberg support it).
- Compression is per-file, not per-column — mixed workloads may want
  separate tables instead of mixed codecs.

### 3. Set the Writer Knobs

- **Row group size**: 128 MB-1 GB; row groups are the parallel unit.
- **Page size**: 1 MB (default) fine; tune only for pathological columns.
- **Dictionary encoding**: on for low-cardinality columns; off for
  high-cardinality unique IDs (bloats).
- **Statistics**: enable page/file statistics (default) — engines use them
  for predicate pruning; `min/max` stats are the free lunch.

```python
import pyarrow as pa
import pyarrow.parquet as pq

table = pa.Table.from_pandas(df)
pq.write_table(
    table,
    "out.parquet",
    compression="zstd",
    row_group_size=512 * 1024 * 1024,
    use_dictionary=["status", "region"],
)
```

### 4. Verify the Result

```bash
parquet-tools schema out.parquet
duckdb -c "SELECT count(*), avg(length(amount::varchar)) FROM read_parquet('out.parquet')"
ls -lh out.parquet
```

Check: compressed size vs source (report the ratio), row-group count sane,
stats present (`parquet-tools inspect` shows column stats).

### 5. Standardize Across Pipelines

- One writer config per platform (document in the platform docs):
  format=parquet, codec=zstd, row-group=512 MB.
- Enforce in the lakehouse table options (`write.parquet.compression-codec`
  in Iceberg, `delta.compression` in Delta).

## Validation

- Format/codec chosen per workload table (matrix documented).
- Compression ratio reported; row-group sizing sane for the engine.
- Predicate pruning works: a filter on a statted column scans few row
  groups (`EXPLAIN` shows it).
- Writer settings standardized in the platform config.

## Definition of Done

- Format decision documented per table tier.
- Compression + row-group knobs set and verified.
- Statistics enabled; pruning verified with EXPLAIN.
- Writer config standardized; no ad-hoc format drift.

## Reference Directory

- [Format Comparison](references/format-comparison.md): depth on Parquet vs
  ORC vs Avro internals.
- [Encoding & Statistics](references/encoding.md): dictionary, RLE, and
  stats mechanics.

## Related Skills

- [Iceberg Basics](../iceberg-basics/SKILL.md) and
  [Delta Lake Basics](../delta-lake-basics/SKILL.md): formats above the file
  layer.
- [Object Storage Basics](../object-storage-basics/SKILL.md): where files
  live.
- [Spark Optimization](../../processing/spark-optimization/SKILL.md):
  file sizing interplay.
