# Query Patterns

## SQL dialect notes

- DuckDB follows PostgreSQL-ish syntax with columnar execution.
- Case-insensitive identifiers; quote with double quotes.
- `DESCRIBE SELECT ...` inspects result schema without running.

## Window & analytical functions

```sql
SELECT
  customer_id,
  amount,
  sum(amount) OVER (PARTITION BY customer_id ORDER BY ts) AS running_total,
  row_number() OVER (PARTITION BY customer_id ORDER BY ts DESC) AS rn
FROM read_parquet('orders/*.parquet');
```

- Use `QUALIFY row_number() OVER (...) = 1` for top-N per group.
- `PIVOT`/`UNPIVOT` convert wide<->long without manual CASE columns.

## Sampling and profiling

```sql
SELECT * FROM read_parquet('big/*.parquet') USING SAMPLE 1000;
```

`USING SAMPLE` gives a representative subset for fast exploratory queries —
use it before expensive full scans.

## Joins and performance

- DuckDB picks the join strategy automatically; `EXPLAIN` to confirm
  hash joins.
- Filter early, project few columns (columnar means unselected columns are
  never read).
- For repeated analysis, load a file once into a temp table — the optimizer
  caches scans better than per-query glob rescans.