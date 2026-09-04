# Assets & Partitions

## Software-defined assets

- An asset is a unit of data with a producer (the `@asset` function) and a
  logical name. The asset graph is derived from function parameters.
- `@asset` returns or loads the produced value; use `@materialize` or IOManagers
  to persist to warehouses/object storage.
- Use `@multi_asset` when one function produces several assets atomically.

## Partitions

```python
from dagster import asset, DailyPartitionsDefinition

@asset(partitions_def=DailyPartitionsDefinition(start_date="2024-01-01"))
def daily_table(context):
    date = context.partition_key
    # load only this partition
```

- Partitioned assets enable per-partition backfills, retries, and
  freshness checks.
- `context.asset_partition_keys_for_output()` gives upstream partition keys
  for incremental dependencies.

## Backfills

Backfill a failed partition range:

```bash
dagster backfill create --partition-range {start}...{end} {asset_key}
```

Rules:

- Backfills MUST be confirmed (Tier M).
- After a backfill, verify partition counts: `dagster asset partitions`
  should show the expected set with no gaps.

## Asset checks

```python
from dagster import asset_check

@asset_check(asset=cleaned_events)
def count_positive(cleaned_events):
    return cleaned_events["count"] > 0
```

Asset checks are the Dagster-native home for quality gates; wire
great-expectations or dbt tests here instead of inside transformation logic.
