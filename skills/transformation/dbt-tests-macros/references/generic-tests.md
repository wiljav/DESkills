# Generic Test Library

## Built-in tests

| Test | Signature | Use |
| --- | --- | --- |
| `unique` | column | PK uniqueness |
| `not_null` | column | required fields |
| `accepted_values` | column, values | enum/domain checks |
| `relationships` | column, to, field | FK integrity |
| `dbt_expectations.expect_column_values_to_be_between` | column, min, max | ranges |
| `dbt_utils.expression_is_true` | expression | arbitrary row-level rule |

## dbt_utils highlights

- `recency` — freshness of a column per group.
- `cardinality_equality` — counts match between two models (good for
  symmetric aggregates).
- `unique_combination_of_columns` — multi-column uniqueness.
- `at_least_one` / `not_empty_string`.

## dbt_expectations highlights

- Distribution tests (`expect_column_distribution_to_be_within`)
- Column pair tests (`expect_column_pair_values_to_be_equal`)
- Regex/format tests (`expect_column_values_to_match_regex`)
- Quantile/percentile tests for anomaly-style checks

## Selection

```bash
dbt test --select fct_orders          # tests on the model
dbt test --select tag:critical        # tests tagged critical
dbt test --select test_type:singular  # only singular tests
```

Tag critical tests (`config(tags=['critical'])`) so CI can fail fast on the
smallest meaningful subset.