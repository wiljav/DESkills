# Indexing & Key Generation

## Index types

| Index | How it locates files | Use |
| --- | --- | --- |
| BLOOM | bloom filter per file | default; good balance |
| BUCKET | hash of key -> bucket file | simplest for fixed keys |
| HBase | external lookup | huge tables with random upserts (ops cost) |

Rules:

- BUCKET index: bucket count ~ partitions; stable keys required.
- BLOOM: automatic; tune `hoodie.bloom.index.filter.estimate` for large
  key spaces.
- Index changes require table rebuild — decide once, early.

## Key generation

- `SimpleKeyGenerator`: `recordkey` = one column; partition path from one
  column.
- `ComplexKeyGenerator`: composite record keys (tuple of columns).
- `TimestampBasedKeyGenerator`: partition by event time — watch timezone
  consistency.

## Precombine discipline

- `precombine.field` MUST be a monotonic column (`updated_at`, `seq_no`).
- Wrong precombine (e.g. `id` itself) makes upserts non-deterministic:
  the "latest" record by file order wins, not by time.
- Document the precombine column per table — it IS the conflict-resolution
  policy.