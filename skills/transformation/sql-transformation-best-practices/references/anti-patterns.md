# Anti-Patterns

## 1. `SELECT *` everywhere

Carries unknown columns, breaks typing, and bloats scans. Only the initial
read of a table may be `*`; explicitly list columns afterwards.

## 2. `DISTINCT` to fix duplicates

Masks the actual problem (bad join, missing dedup key) and costs a sort.
Investigate the join first; dedupe with `row_number()` when duplicates are
legitimate.

## 3. `NOT IN` with NULLs

`x NOT IN (a, b, NULL)` returns no rows when any NULL exists. Use `NOT EXISTS`
for anti-joins.

## 4. Implicit casts

Comparing strings to dates or floats to decimals silently coerces. Cast
explicitly at the boundary.

## 5. Filtering after aggregation

`HAVING` on raw columns or filtering in the outer query instead of pushing
into the scan defeats partition pruning.

## 6. CTE naming soup

`cte1`, `data`, `t`, or one mega-CTE with five joins. One concept per named
CTE.

## 7. Repeating expressions

`case when` blocks pasted across models. Extract to a macro (dbt) or a
shared view.

## 8. Comments that restate the code

```sql
-- adds 1 to id
select id + 1 as id
```

Comment WHY: business rules, edge cases, decisions.

## 9. Non-deterministic outputs

`rand()`/`now()` in transformation logic make re-runs non-idempotent. Use
run-scoped timestamps injected by the orchestrator instead.

## 10. Cartesian joins (accidental)

Missing join key produces N*M rows. Always count expected rows after joins
(`select count(*)` on a sample) before trusting output.