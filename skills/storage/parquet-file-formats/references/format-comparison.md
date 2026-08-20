# Format Comparison

## Parquet

- Columnar storage with nested types, statistics, dictionary encoding.
- Row-group-based: row groups are compressed independently and read in
  parallel.
- Splittable at row-group boundaries (good for object storage + engines).
- Best all-round default for analytics.

## ORC

- Columnar, similar to Parquet; stronger built-in compression (RLE-heavy),
  stripe layout.
- Historically faster full-table scans in Hive; modern engines narrowed the
  gap.
- Choose when the fleet is Hive-native or the org standard is ORC.

## Avro

- Row-oriented with embedded schema.
- Low write CPU, append-friendly: ideal for streaming/event payloads.
- Analytics scans pay full-file reads; never serve BI from Avro directly.

## Decision matrix

| Requirement | Format |
| --- | --- |
| Analytics default | Parquet |
| Hive-native fleet | ORC |
| Streaming payloads | Avro |
| Interop with external vendors | depends on the vendor's spec |

## Migration notes

- Converting formats is a rewrite: plan a window, validate counts and
  schema diffs, swap readers only after verification.