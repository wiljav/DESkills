---
name: dagster-basics
metadata:
  category: Orchestration
description: >-
  Builds typed, testable data pipelines with Dagster assets, jobs, schedules,
  and sensors. Use when orchestrating data pipelines with software-defined
  assets or when migrating from imperative schedulers. Don't use for plain
  Airflow authoring (use airflow-dag-authoring) or for choosing an
  orchestrator (see data-platform-architecture).
allowed-tools:
  - dagster
  - python
  - dagster-daemon
---

# Dagster Basics

Dagster is an orchestration platform built around software-defined assets
(SDAs): pipelines are declared as assets with explicit upstream/downstream
dependencies, and Dagster derives the execution graph from them.

## Prerequisites

- A Python environment with `dagster` and `dagster-webserver` installed
  (`pip install dagster dagster-webserver`).
- A working directory with a `Definitions` object (see Workflow step 2).
- For cloud-backed assets, credentials per `data-engineering-auth`.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `dagster asset list`, `dagster job list`,
  `dagster schedule list`, launching `--preview`/dry-run style materializations
  where supported, inspecting run history.
- **Tier M (mutation)**: materializing assets, launching runs, starting
  schedules/sensors, and deploying code locations. All MUST be confirmed by
  the user before execution.

## Workflow

### 1. Scaffold the Project

```bash
dagster project scaffold --name {project_name}
cd {project_name}
```

The scaffold produces `{project_name}/definitions.py`, `assets/`, and
`jobs/` skeletons plus `pyproject.toml`.

### 2. Declare Assets

Model data as assets with explicit dependencies:

```python
from dagster import asset

@asset
def raw_events():
    # ingest step; returns/loads data
    return {"count": 42}

@asset
def cleaned_events(raw_events):
    # transformation step depends on raw_events
    return raw_events["count"] * 2
```

Asset rules:

- Each asset declares its upstream dependencies as parameters.
- Keep assets idempotent: re-materializing the same partition must produce
  the same result.
- Use `partitions_def` for partitioned assets so backfills and retries work
  per-partition.

### 3. Define Jobs, Schedules, and Sensors

```python
from dagster import Definitions, define_asset_job, ScheduleDefinition

materialize_all = define_asset_job("materialize_all")
daily_schedule = ScheduleDefinition(job=materialize_all, cron_schedule="0 8 * * *")

defs = Definitions(
    assets=[raw_events, cleaned_events],
    schedules=[daily_schedule],
)
```

- Prefer schedules for time-based pipelines and sensors for event-driven
  triggers (e.g. new file landed).
- Give every schedule a documented cron and timezone.

### 4. Run Locally and Inspect

```bash
dagster dev
```

Open the webserver (default `http://localhost:3000`), verify the asset graph
renders with correct dependencies, and materialize assets via the UI or:

```bash
dagster job execute --job-name materialize_all
```

Inspect run history for success/failure; use the asset lineage view to
confirm the DAG matches intent.

### 5. Deploy the Code Location

Deploy via the platform's code location mechanism (workspace file, Docker
image, or managed Dagster). Verify:

```bash
dagster asset list
dagster schedule list
```

Confirm schedules are active and the code location is healthy before
declaring the job production-ready.

## Validation

- Asset graph renders with correct upstream/downstream edges.
- A local materialization run succeeds end to end.
- Schedules/sensors listed as active in the deployment.
- Re-running a partition produces identical results (idempotency).

## Definition of Done

- Assets, jobs, schedules defined in `definitions.py`.
- Local run succeeded; graph verified in the webserver.
- Deployment confirmed by the user and verified (assets + schedules listed).
- No secrets in code; credentials via environment/config per auth skill.

## Reference Directory

- [Assets & Partitions](references/assets-partitions.md): partitioning,
  backfills, and asset checks.
- [Schedules, Sensors & Automation](references/automation.md): triggers and
  failure handling.

## Related Skills

- [Data Quality Tests](../../quality/dbt-data-quality-tests/SKILL.md):
  asset checks can call dbt tests.
- [Data Platform Architecture](../../solutions/data-platform-architecture/SKILL.md):
  where Dagster fits in the stack.
- [Airflow Job Failure Troubleshooting](../airflow-job-failure-troubleshooting/SKILL.md):
  analogous failure diagnosis for runs.