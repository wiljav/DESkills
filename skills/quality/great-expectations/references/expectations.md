# Expectations Catalogue

## Column-level

| Expectation | Use |
| --- | --- |
| `expect_column_to_exist` | schema drift guard |
| `expect_column_values_to_not_be_null` | required fields |
| `expect_column_values_to_be_unique` | PK-like uniqueness |
| `expect_column_values_to_be_between` | ranges (amounts, ages) |
| `expect_column_values_to_be_in_set` | enum domains |
| `expect_column_values_to_match_regex` | formats (emails, SKUs) |
| `expect_column_mean/median_to_be_between` | distribution sanity |
| `expect_column_values_to_be_of_type` | type stability |

## Table-level

| Expectation | Use |
| --- | --- |
| `expect_table_row_count_to_be_between` | volume guard (slammed/empty) |
| `expect_table_columns_to_match_ordered_list` | exact schema pin |
| `expect_table_row_count_to_equal_other_table` | symmetric aggregates |

## Distribution & profiles

`expect_column_quantile_values_to_be_between`, `expect_column_kl_divergence_to_be_less_than`
— use for anomaly-style checks with thresholds from observed history. These
drift; review monthly and re-baseline deliberately.

## Selection rules

1. Invariants (not-null, unique, range, type) — always.
2. Business rules (regex, in-set) — always.
3. Distribution checks — only where upstream changes are slow.
4. Never threshold on data you do not understand; wrong baselines cause
   alert fatigue.