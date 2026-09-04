# Anomaly Detection Rules

## Volume (z-score)

```
z = (current - mean_last_30d) / std_last_30d
alert if |z| > 3, or if count == 0 when count_expected > 0
```

- Require >= 14 days of history before trusting z-scores.
- Reset baseline on deliberate schema/scope changes (document the change in
  the metric table via a `baseline_changed_at` marker).

## Freshness

```
age = now - max(loaded_at)
alert if age > warn_after (per cadence table) or > error_after
```

- Per-table cadence map lives in the monitoring config, not inline.

## Schema drift

- Pin schemas from the data contract (governance skills).
- Compare `DESCRIBE` columns/order/types; alert on added/removed/renamed.
- Treat type changes as critical; null-ability changes as warn.

## Null-rate and distribution

- `null_rate = count(col IS NULL) / count(*)` — alert if > baseline * 2.
- Quantile drift: compare p50/p95 of key columns vs trailing 30d; alert on
  > 20% relative shift (tune per column).

## Baselines & review

- Re-baseline monthly and after any deliberate upstream change.
- Every rule has: threshold, owner, escalation path, and a "why" comment.
- Alert noise target: < 30% of fired alerts are false positives.
