---
name: airflow-job-failure-troubleshooting
metadata:
  category: Orchestration
description: >-
  Diagnoses failed Airflow DAG runs and task instances from logs, metadata,
  and infrastructure signals: import errors, scheduler stalls, retry storms,
  and upstream data issues. Use when a DAG run is failing, stuck, or missing.
  Don't use for authoring DAGs (use airflow-dag-authoring) or for configuring
  the platform (use airflow-basics).
allowed-tools:
  - airflow
  - python
  - gcloud
---

# Airflow Job Failure Troubleshooting

This skill turns Airflow failures into a decision tree: classify the failure
signature, locate the authoritative log, identify root cause, remediate, and
prevent recurrence.

## Prerequisites

- Access to the Airflow UI or CLI for the affected environment.
- Permission to read task logs and metadata (read-only first).
- Knowledge of the pipeline's SLA and expected data volumes (from the team or
  documentation).
- `airflow` CLI available; managed environments use their platform CLI
  (`gcloud composer environments run`, MWAA CLI).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: querying DAG run/task states, reading logs, diffing
  DAG versions, querying metadata DB (read-only).
- **Tier M (mutation)**: clearing task instances, marking runs successful,
  re-running/backfilling, changing DAG code, and restarting components.
  Every mutation MUST be confirmed by the user; never silently re-run
  pipeline work that may have partially written data.

## Workflow

### 1. Classify the Failure Signature

Gather the facts first:

```bash
airflow dags list-runs --dag-id {dag_id} --state failed --limit 5
airflow tasks list-runs --dag-id {dag_id} --state failed --limit 20
airflow dags list-import-errors
```

Map to a signature using [Failure Signatures](references/failure-signatures.md):

| Signature | Quick signal |
| --- | --- |
| Import error | `dags list-import-errors` non-empty |
| Task failure (code) | task state `failed`, log shows exception |
| Task stuck | task state `running` beyond SLA; scheduler queue backlog |
| Retry storm | same task failed N times with identical stack trace |
| Missing run | DAG not scheduled; scheduler down or schedule missed |
| Upstream data issue | task fails reading a table/object that does not exist |

### 2. Locate and Read the Authoritative Log

```bash
airflow tasks logs --dag-id {dag_id} --task-id {task_id} --run-id {run_id} --map-index 0 2>/dev/null | tail -100
```

For managed environments, logs land in the platform logging (Cloud Logging /
CloudWatch): search `resource.type="cloud_composer_environment"` with the
DAG file name and `severity>=ERROR` (see the source repo's pattern in
`managed-airflow-dag-authoring`).

Extract: exception class, failing line, provider error code, and any
resource identifiers (buckets, tables, connection IDs).

### 3. Determine Root Cause

Follow the decision tree in [Failure Signatures](references/failure-signatures.md).
Common roots in order of frequency:

1. **Data dependencies**: upstream table missing/empty; the task is
   technically fine. Verify with a read-only query for the expected data.
2. **Credentials**: connection broken or expired — confirm with the auth
   skill's validation commands (never print secrets).
3. **Resource limits**: quota exceeded, out of memory, disk full, connector
   limits.
4. **Code defect**: only reproducible with certain inputs; check for
   non-idempotent logic.
5. **Platform issue**: scheduler/worker restarts, metadata DB problems.

### 4. Remediate (Mutation, Requires Confirmation)

Depending on the root cause:

```bash
# clear a failed task for re-run after the underlying issue is fixed
airflow tasks clear {dag_id} --task-regex {task_id} --start-date {start} --end-date {end}

# backfill a missed interval after verification
airflow dags backfill {dag_id} -s {start} -e {end} --reset-dagruns
```

Rules:

- Fix the root cause BEFORE re-running; clearing without a fix repeats the
  failure and risks double writes.
- Prefer re-running the failed task over `--mark-success` (never fabricate
  success unless explicitly instructed and the data is verifiably complete).
- If the failure is data-dependent and the interval is irrecoverable, agree
  with the user on the SLA outcome rather than silently skipping.

### 5. Prevent Recurrence

- If the root cause is code: update the DAG per `airflow-dag-authoring`
  (retries, idempotency, sensors on upstream data).
- If the root cause is platform: adjust alerts/quotas; document in the team
  runbook.
- Record the incident: signature, root cause, fix, and verification in one
  paragraph in the issue tracker.

## Validation

- After remediation, the failed task/run reaches `success` for the affected
  interval(s).
- Re-running the same interval produces identical results (idempotency
  proven).
- `dags list-import-errors` stays empty.
- The root cause is stated explicitly in the final summary — never conclude
  with "cleared and reran" alone.

## Definition of Done

- Failure signature classified and root cause identified from logs.
- Fix applied with user confirmation; verification run succeeded.
- No fabricated success marks; no silent skips.
- Recurrence prevention documented (code change, alert, or runbook entry).
- Final summary states: signature, root cause, fix, verification.

## Reference Directory

- [Failure Signatures](references/failure-signatures.md): decision tree for
  each failure class with diagnosis commands.
- [Log Query Templates](references/log-queries.md): ready-made log searches
  for self-managed and managed Airflow.
- [Runbook Template](references/runbook-template.md): skeleton for the
  post-incident entry.

## Related Skills

- [Airflow DAG Authoring](../airflow-dag-authoring/SKILL.md): fixes that
  touch DAG code.
- [Airflow Basics](../airflow-basics/SKILL.md): environment-level causes
  (executor, connections, secrets backend).
- [Data Quality Incident Runbook](../../quality/data-quality-incident-runbook/SKILL.md):
  when the failure indicates bad data, not bad code.