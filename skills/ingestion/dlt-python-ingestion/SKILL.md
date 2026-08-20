---
name: dlt-python-ingestion
metadata:
  category: DataIngestion
description: >-
  Builds declarative Python data pipelines with dlt (data load tool):
  resources, sources, destinations, incremental loading, and schema
  evolution. Use when ingestion logic lives in code and needs type
  handling, retries, and incremental state without a SaaS platform.
  Don't use for UI-managed syncs (use airbyte-basics) or file-based bulk
  loads (use file-ingestion-gcs-s3).
allowed-tools:
  - python
  - dlt
---

# dlt (Python) Ingestion

`dlt` is an open-source Python library for data ingestion: you write plain
Python generators, `dlt` handles extraction, typing, normalization, and
loading into destinations with stateful incremental syncs.

## Prerequisites

- Python 3.9+; `pip install "dlt[bigquery]"` (or the destination extras:
  `[snowflake]`, `[postgres]`, `[duckdb]`, `[filesystem]`).
- Destination credentials per the auth skill via env vars
  (`DESTINATION__CREDENTIALS__*` or `dlt` secret config).
- Source access (API keys, DB read access) kept out of the pipeline code.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `dlt debug`, `dlt pipeline show`, running
  pipelines in dev/dry-run mode, inspecting state.
- **Tier M (mutation)**: running pipelines against shared destinations,
  `dlt pipeline run` with production credentials, and `--drop-pending` /
  state resets. Confirm before production runs; resets truncate state and
  destination data.

## Workflow

### 1. Define the Source

```python
import dlt

@dlt.resource(name="events", write_disposition="append")
def events():
    # any generator: API pagination, DB rows, file lines
    yield from fetch_api_pages("https://api.example.com/events")

@dlt.source
def example_api():
    return events()
```

Rules:

- One resource per logical dataset; generators stream — never load
  everything into memory.
- Declare `write_disposition`: `append`, `replace`, or `merge` (upsert).
- Keep sources in `sources/` modules, pipelines in `pipelines/`.

### 2. Configure the Destination

```python
pipeline = dlt.pipeline(
    pipeline_name="events_ingest",
    destination="bigquery",
    dataset_name="raw",
)
```

Credentials from env vars:

```bash
export DESTINATION__BIGQUERY__CREDENTIALS__PROJECT_ID="{project}"
export DESTINATION__BIGQUERY__CREDENTIALS__CLIENT_EMAIL="{sa}"
```

`dlt` auto-detects types (`T.` hints) — annotate where inference is
ambiguous:

```python
from dlt.common import T

@dlt.resource
def orders():
    yield {"id": "1", "amount": T.DecimalType(), "ts": T.TimestampType()}
```

### 3. Enable Incremental Loading

```python
import dlt

@dlt.resource(
    name="orders",
    write_disposition="merge",
    primary_key="id",
    incremental=dlt.sources.incremental("updated_at", initial_value="2024-01-01"),
)
def orders():
    yield from fetch_orders(since=orders.incremental.last_value)
```

Rules:

- Cursor column MUST be monotonic; `last_value` drives the next query.
- `merge` + `primary_key` = idempotent upserts (re-runs converge).
- State lives in the destination's `_dlt_pipeline_state` table — never
  delete it without a plan.

### 4. Run and Verify

```bash
dlt pipeline events_ingest run --full-refresh   # dev only
dlt pipeline events_ingest run                  # incremental
dlt pipeline events_ingest show                 # load info + schema
```

Verify: load status `COMPLETED`, rows loaded match source, and a second run
loads 0 new rows when nothing changed.

### 5. Handle Schema Evolution

- `dlt` normalizes schemas per run; new columns appear automatically.
- Breaking changes (type/name): review `pipeline show` schema diff; use
  `dlt`'s schema hints to control typing instead of patching SQL.
- Coordinate breaking changes via data contracts.

## Validation

- Full-refresh dev run completes; row counts match the source.
- Incremental re-run loads only new rows (cursor verified).
- Merge re-run is idempotent (row count stable after N runs).
- No credentials in code; env vars / secret config used.

## Definition of Done

- Source/resource defined with explicit disposition and typing.
- Pipeline runs end to end against the destination.
- Incremental state proven (second run delta verified).
- Schema evolution policy documented for the pipeline's tables.
- Production run confirmed by the user.

## Reference Directory

- [Resource & Disposition Patterns](references/resources.md): append/merge/
  replace decisions and API pagination helpers.
- [Incremental State Deep Dive](references/incremental.md): state storage,
  reset, and multi-resource coordination.

## Related Skills

- [Airbyte](../airbyte-basics/SKILL.md): UI-managed alternative.
- [dbt Core](../../transformation/dbt-core/SKILL.md): consuming `raw`
  datasets as sources.
- [Data Contracts](../../governance/data-contracts/SKILL.md): governing the
  schemas dlt produces.