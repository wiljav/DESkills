---
name: data-quality-incident-runbook
metadata:
  category: DataQuality
description: >-
  Triage, remediates, and post-mortems data quality incidents: alert
  verification, blast-radius analysis via lineage, mitigation, and
  prevention. Use when a quality check fails or consumers report bad data.
  Don't use for writing checks (use dbt tests/soda/great-expectations) or
  for diagnosing pipeline crashes (use the orchestrator troubleshooting
  skills).
allowed-tools:
  - python
  - dbt
  - airflow
---

# Data Quality Incident Runbook

When a quality gate fails or a consumer reports bad data, this runbook
drives a disciplined response: verify, scope, mitigate, fix, verify, learn.

## Prerequisites

- Alert or consumer report with the affected asset and time window.
- Access to metric history (data-observability) and lineage
  (openlineage-basics).
- Ownership map: who produces the asset, who consumes it.
- A communication channel for the incident (Slack channel + on-call).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: verifying the alert, reading metrics/lineage,
  inspecting data, reproducing with read-only queries.
- **Tier M (mutation)**: repairing/replaying data, changing pipelines,
  blocking consumers, and silencing alerts. All MUST be confirmed; a bad
  repair can silently corrupt data for longer than the original incident.

## Workflow

### 1. Verify the Alert (10 min)

- Confirm the metric truly regressed: compare `measured_at` values against
  history; rule out monitor misconfiguration (bad query, new baseline).
- Reproduce with a read-only query (e.g. count rows where the invariant
  fails).
- Decide: real incident vs false alarm. False alarm -> fix the monitor,
  log, close.

### 2. Scope the Blast Radius

Use lineage (upstream/downstream) to answer:

- Which tables are affected (same pipeline, same partition range)?
- Which consumers depend on the broken asset?
- When did it start? (first violating metric timestamp)

Classify severity:

| Severity | Criteria |
| --- | --- |
| SEV-1 | Tier-1 marts wrong; consumers actively blocked |
| SEV-2 | wrong data in non-critical assets; SLA at risk |
| SEV-3 | quality gates failing; no consumer impact yet |

### 3. Mitigate (Confirmed)

- **Block consumers**: pause downstream jobs reading the bad asset; reroute
  BI reports to a known-good snapshot if one exists.
- **Prevent further damage**: pause the producing pipeline if it keeps
  writing bad data; do NOT let it overwrite history.
- Communicate: current status, ETA, who is affected.

### 4. Fix the Root Cause

Determine source of the bad data:

1. **Upstream source** changed schema/semantics (check the contract).
2. **Ingestion bug** (parsing, typing, dedup).
3. **Transformation bug** (logic regression — `git log` the model).
4. **Environment** (wrong branch/target wrote to prod).

Apply the fix per the relevant skill (dbt-core, spark-basics, ingestion
skills). NEVER patch data with ad-hoc SQL before the code fix is in.

### 5. Repair Data (Confirmed, Highest Care)

Repair options in order of preference:

1. Re-run the producing pipeline for the affected window (idempotent
   re-run, verifies code fix + produces clean data).
2. Targeted SQL repair on the affected rows — only if re-run is impossible;
   requires a reviewed, tested script and a full count diff before/after.
3. Snapshot restore — only with a verified good snapshot and consumer
   notification.

Verify: row counts, sample values, and the violated invariant all match
expectations. Prove the repair with the same checks that caught the incident.

### 6. Post-Mortem & Prevention

- Record in the runbook log: timeline, root cause, fix, verification.
- Add/re-tune checks that would have caught it earlier (see
  data-observability anomaly rules).
- Update ownership map if the alert routed to the wrong team.
- Share the post-mortem with the data platform channel.

## Validation

- The violating invariant passes on the repaired asset.
- Consumers' downstream jobs re-run clean.
- Alert history shows the incident window closed with the monitor back to
  green.
- Post-mortem documented with prevention items tracked.

## Definition of Done

- Alert verified as real (or false alarm handled).
- Blast radius scoped; severity declared; consumers notified.
- Mitigation applied and confirmed.
- Root cause fixed in code; repair done via re-run or reviewed SQL.
- Post-mortem recorded; prevention items assigned.

## Reference Directory

- [Severity Matrix](references/severity-matrix.md): decision table for
  classification and escalation.
- [Repair Playbooks](references/repair-playbooks.md): re-run vs SQL repair
  vs snapshot restore guidance.
- [Incident Log Template](references/incident-log.md): the record format.

## Related Skills

- [Data Observability](../data-observability/SKILL.md): the monitors that
  raise these incidents.
- [OpenLineage](../../governance/openlineage-basics/SKILL.md): blast-radius
  analysis.
- [Airflow Job Failure Troubleshooting](../../orchestration/airflow-job-failure-troubleshooting/SKILL.md):
  when the incident is a pipeline crash, not a data problem.