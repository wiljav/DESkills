# Validation Recipes

## Count parity

```sql
-- source
SELECT COUNT(*) FROM source.orders;
-- target (lakehouse)
SELECT COUNT(*) FROM curated.orders;
```

Equal at every cutover point. Track the delta if dual-writing.

## Checksum on key columns

```sql
SELECT COUNT(*) FROM source.orders
UNION ALL
SELECT COUNT(*) FROM curated.orders;
-- plus sampled value checks:
SELECT order_id, amount FROM source.orders ORDER BY order_id LIMIT 1000;
SELECT order_id, amount FROM curated.orders ORDER BY order_id LIMIT 1000;
```

Automate with a diff script comparing sampled rows (diff of sorted
outputs).

## Null and type sanity

- Compare null rates per column (source vs target).
- Compare column types (warehouse `DESCRIBE` vs lakehouse schema).
- Run the source's dbt test suite against the lakehouse copy — parity of
  guarantees, not just data.

## Freshness during parallel run

- Daily: gold table outputs must match (count + checksum) for the prior
  day.
- Any mismatch: stop the wave, fix, restart that table (idempotent).