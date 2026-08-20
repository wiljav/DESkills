# Encoding & Statistics

## Dictionary encoding

- Column values replaced by integer codes + dictionary table.
- Wins big on low-cardinality columns (enums, regions, statuses).
- Hurts high-cardinality unique values (IDs, hashes) — disable per column.

## RLE / bit-packing

- Parquet/ORC compress runs of repeated values.
- Sorting data by a column before write improves its RLE ratio massively
  (sorting by date before writing date-partitioned tables is nearly free).

## Statistics & predicate pruning

- File/row-group `min/max` stats let engines skip irrelevant data.
- Sorting by the filter column sharpens min/max ranges -> better pruning.
- Statistics are only useful if the engine is configured to read them
  (verify with EXPLAIN).

## Null handling

- Nulls encoded in the definition levels; wide sparse columns still cost
  bytes — consider dropping columns with >90% nulls before serving.