# Checks Language Reference

## Metric checks

| Metric | Example | Meaning |
| --- | --- | --- |
| `freshness` | `freshness(loaded_at) < 6h` | max age of the freshness column |
| `row_count` | `row_count > 10000` | table volume |
| `duplicate_count` | `duplicate_count(order_id) = 0` | dup rows on a column |
| `missing_count` / `missing_percent` | `missing_count(customer_id) = 0` | NULLs |
| `invalid_count` | `invalid_count(status, valid values: [a, b])` | invalid values |
| `avg` / `min` / `max` | `avg(amount) between 50 and 500` | aggregates |
| `percentile` | `percentile(amount, 0.95) < 1000` | tail bounds |
| `schema` | `schema: ...` | required/forbidden columns, types |

## Threshold syntax

- Simple: `metric < value`, `between a and b`, `= value`.
- Warn + fail: `warn: when < x`, `fail: when > y` blocks.
- Percent-based: `missing_percent < 5` etc.

## Variables

```yaml
checks for orders:
  - variables:
      today: 2024-01-01
  - row_count > 1000
```

Use variables for date-windowed checks in scheduled scans.

## Discovery

`frequent_values`, `distribution` checks exist but are profiling-oriented;
keep them out of CI gates unless baselined from real history.
