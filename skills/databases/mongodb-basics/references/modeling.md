# Modeling Patterns

## Embed vs reference

| Case | Choice |
| --- | --- |
| Items read only with the order | embed (one read) |
| Shared entity (customer) updated often | reference by id |
| One-to-many beyond ~500 docs | reference (16MB doc limit) |
| Independent lifecycle | reference |

## Schema evolution

- Documents are schemaless: new fields appear silently.
- Add fields forward-compatibly; NEVER remove/repurpose without an
  extraction audit (downstream schemas break).
- Track the schema contract: MongoDB sample data should be validated
  against the data-contracts registry on extraction.

## _id discipline

- `_id` is unique + indexed; objectIds are fine, natural keys are better
  for dedup.
- Upsert key for idempotent extraction = `_id` (or a business key).

## Sharding notes (scale-out)

- Shard key must have high cardinality + even distribution + no monotonic
  hotspots (`customer_id` over `created_at` for writes).
- Re-sharding requires data migration — decide early.