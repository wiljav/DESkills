---
name: prefect-basics
metadata:
  category: Orchestration
description: >-
  Orchestrates Python data workflows with Prefect flows, tasks, deployments,
  and schedules. Use when wrapping Python-based pipelines with retries,
  caching, and observability without a heavyweight scheduler. Don't use for
  SQL-centric transformation pipelines (use dbt + airflow) or for
  choosing an orchestrator (see data-platform-architecture).
allowed-tools:
  - prefect
  - python
---

# Prefect Basics

Prefect orchestrates Python workflows through the `@flow`/`@task` decorators,
with a local or hosted API server managing deployments, schedules, and run
history.

## Prerequisites

- Python 3.9+; `pip install prefect` (or `uv tool install prefect`).
- A Prefect API server reachable (`prefect server start` for local, or a
  hosted workspace).
- Credentials for cloud-backed tasks per `data-engineering-auth`.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `prefect flow ls`, `prefect deployment ls`,
  `prefect work-queue ls`, inspecting run history and logs.
- **Tier M (mutation)**: deploying flows, creating schedules, running flows,
  and updating the API server config. MUST be confirmed by the user.

## Workflow

### 1. Start the Server

Local development:

```bash
prefect server start
```

In another terminal:

```bash
prefect profile ls   # confirm the default profile points at the server
```

### 2. Author the Flow

```python
from prefect import flow, task

@task(retries=2, retry_delay_seconds=60)
def transform(url: str) -> int:
    # idempotent transformation; returns a row count
    return 42

@flow(log_prints=True)
def etl_pipeline(url: str):
    count = transform(url)
    print(f"transformed {count} rows")
```

Rules:

- Flows are the entry point; tasks are the retry/caching unit.
- Tasks MUST be idempotent (same inputs, same result).
- Use `retries` + `retry_delay_seconds` instead of bespoke retry loops.
- Use `cached=False` on tasks intentionally; default caching keys off inputs
  and result storage.

### 3. Validate Locally

```bash
prefect flow-run inspect   # after running
python - <<'PY'
from {module} import etl_pipeline
etl_pipeline("s3://bucket/path")   # runs locally with task retries
PY
```

Verify the run appears in the UI with task-level logs.

### 4. Create a Deployment

```bash
prefect deployment build {module}:{flow_name} -n {deployment_name} -q {queue} -o {file}.yaml
prefect deployment apply {file}.yaml
prefect deployment ls
```

Deployments bind the flow code to schedules and work pools. For a schedule:

```bash
prefect deployment schedule create {flow_name}/{deployment_name} \
  --interval 86400 --anchor-date {date}
```

### 5. Run and Monitor

```bash
prefect deployment run {flow_name}/{deployment_name}
prefect flow-run ls --limit 5
```

Confirm the run executes with expected task counts and no retries firing
unexpectedly (a retry storm indicates a deterministic failure).

## Validation

- Flow runs succeed end to end with task logs visible.
- Deployment listed; schedule active if requested.
- Re-running with the same parameters yields identical results.
- No credentials embedded in flow code or deployment YAML.

## Definition of Done

- Flow + tasks authored with retries and idempotency.
- Local validation run succeeded.
- Deployment applied and scheduled (if requested) with user confirmation.
- Run history shows a clean success; retry behavior understood.

## Reference Directory

- [Deployments & Work Pools](references/deployments.md): scheduling,
  work queues, and running flows in production.
- [Caching & Retries](references/caching.md): idempotency primitives and
  cache key semantics.

## Related Skills

- [Data Engineering Stack Setup](../../platform/de-stack-getting-started/SKILL.md):
  environment bootstrap with `uv tool install prefect`.
- [Data Platform Architecture](../../solutions/data-platform-architecture/SKILL.md):
  orchestrator selection context.