# Indexing & EXPLAIN

## Reading EXPLAIN

- `Seq Scan`: full table read — expensive on big tables; index likely
  missing.
- `Index Scan` / `Bitmap Index Scan`: good — filter hit an index.
- `Sort` after a scan: check if the sort column should be indexed
  (for ORDER BY / merge joins).
- Numbers to look at: `rows` (estimate vs actual), `buffers` (reads),
  `actual time`.

## Index rules

- Composite index `(a, b)` serves filters on `a` and `a+b`, NOT `b` alone.
- Low-cardinality columns (booleans, statuses) rarely deserve standalone
  indexes.
- Partial indexes for hot subsets:
  `CREATE INDEX idx_orders_active ON orders(id) WHERE status = 'active';`
- Every index taxes writes — budget indexes like any resource.

## Analyze vs vacuum

- `ANALYZE` refreshes planner statistics; auto-vacuum runs it, but big
  changes merit a manual run.
- `VACUUM` reclaims dead tuples; `VACUUM FULL` locks — maintenance window
  only.