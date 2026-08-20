# Style Guide

## Formatting

- Uppercase SQL keywords: `SELECT`, `FROM`, `WHERE`, `JOIN`, `GROUP BY`.
- Lowercase identifiers; snake_case names.
- Indent CTE bodies 4 spaces; comma-first line breaks for column lists.
- One statement per line; keep lines under ~100 chars.
- `sqlfluff fix` with the target dialect enforces this automatically.

## Naming

| Concept | Convention |
| --- | --- |
| Raw input | `raw_<entity>` |
| Staging | `stg_<entity>` |
| Facts | `fct_<entity>` |
| Dimensions | `dim_<entity>` |
| Intermediate | `int_<purpose>` |
| Aggregates | `<metric>_<granularity>` (e.g. `total_amount_hourly`) |

- Names state content, not queries (`orders_total`, not `query_2`).
- No reserved-word collisions; suffix columns like `date` -> `_date`.

## Comments

- Comment business rules and non-obvious decisions at the line they apply to.
- Use `--` line comments; block comments for model-level intent.
- Never commit commented-out code; delete it.