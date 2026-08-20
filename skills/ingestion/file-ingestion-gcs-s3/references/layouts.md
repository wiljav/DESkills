# File Layout Contracts

## Naming and prefixes

```
inbox/{source}/date={YYYY-MM-DD}/{uuid}.parquet
archive/{source}/date={YYYY-MM-DD}/{uuid}.parquet
quarantine/{source}/date={YYYY-MM-DD}/{uuid}.parquet + .reason.json
```

- `{uuid}` guarantees uniqueness; never reuse names across loads.
- `date=`-style prefix partitions match lakehouse partition layouts.
- A `manifest.json` per date lists files + row counts + checksums — the
  load's source of truth.

## Schema-on-read vs write

- **Schema-on-read** (lakehouse): files define the schema; tables evolve
  with them. Lower friction, needs schema-change governance.
- **Schema-on-write**: the pipeline validates against a pinned contract and
  rejects drift. Higher safety, more maintenance.

Choose per table tier: contract-pinned for marts, schema-on-read for raw.

## Manifest example

```json
{
  "date": "2024-01-01",
  "files": [
    {"path": "inbox/events/date=2024-01-01/abc.parquet", "rows": 12000, "md5": "..."}
  ]
}
```

## Quarantine reasons

`.reason.json` records: file, failure type (schema/checksum/parse), sample
error. Quarantine is an operator queue, not a black hole — alert on it.