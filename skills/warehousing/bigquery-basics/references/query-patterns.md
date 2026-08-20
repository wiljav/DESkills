# Query Patterns

## Windows

```sql
SELECT order_id, customer_id,
  SUM(amount) OVER (PARTITION BY customer_id ORDER BY event_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM orders;
```

## Joins

- Prefer small-to-large join ordering; BigQuery optimizes automatically, but
  duplicate/expanded keys blow up — dedupe before join.
- Use `JOIN ... USING` where column names match (cleaner + avoids ambiguity).

## Arrays & structs

```sql
SELECT customer_id, ARRAY_AGG(STRUCT(order_id, amount) ORDER BY event_date) AS orders
FROM orders GROUP BY customer_id;
```

- Arrays keep related data denormalized; flatten with `UNNEST` when needed.
- `ARRAY_AGG(DISTINCT x)` for dedup inside aggregation.

## MERGE upsert pattern

```sql
MERGE orders T
USING staged_orders S
ON T.order_id = S.order_id
WHEN MATCHED THEN UPDATE SET amount = S.amount
WHEN NOT MATCHED THEN INSERT (order_id, amount, event_date)
  VALUES (S.order_id, S.amount, S.event_date);
```

- Idempotent rerun: same staged input -> same result.
- Keep the staged table partitioned the same as the target for cheap
  merges.