# Freshness & Volatility Gates

## Designing freshness thresholds

Freshness = max age of `loaded_at_field` in the table.

| Source cadence | warn_after | error_after |
| --- | --- | --- |
| hourly | 2h | 4h |
| daily | 12h | 24h |
| weekly | 2d | 3d |

Rules:

- Thresholds MUST exceed the source's own scheduled cadence (a daily source
  with 1h warn will never be green).
- Account for known downtime windows (overnight maintenance) in
  `filter`/`dbt meta` when the platform supports it.

## Volatility gates

Volume guards on models:

```yaml
    tests:
      - dbt_utils.expression_is_true:
          expression: >
            (select count(*) from {{ this }}) >
            0.5 * (select count(*) from {{ ref('fct_orders_previous') }})
```

Use for "row count didn't collapse" invariants. For percentage thresholds on
fresh data, prefer `dbt_expectations.expect_table_row_count_to_be_between`
with bounds from history.

## Operational notes

- `dbt source freshness` only checks configured sources; every source dbt
  reads should declare freshness.
- Freshness failures should block downstream builds of stale-dependent
  models (config `freshness: {warn_after..., error_after...}` on sources
  does this via `dbt build` ordering).