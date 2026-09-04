# Engines & Indexing

## InnoDB essentials

- Clustered by primary key: the PK physically orders rows; PK choice
  matters (auto-increment beats random UUIDs for write throughput).
- Secondary indexes point back to the PK — wide PKs bloat every index.
- Buffer pool is the hot cache: `SHOW ENGINE INNODB STATUS` shows hits.

## Reading EXPLAIN

- `type` column: `ALL` = full scan (bad), `range`/`ref`/`const` = good.
- `key` column: which index was actually used (null = none).
- `rows` estimate vs actual `rows_examined` in profiling — verify pruning.

## Index rules

- Leftmost-prefix: `(a, b)` serves `a` and `a+b`, not `b`.
- Prefix indexes on long text: `INDEX (email(10))` — smaller, often
  enough for lookups.
- Avoid functional-expression indexes (pre-8.0): denormalize the computed
  column instead.
