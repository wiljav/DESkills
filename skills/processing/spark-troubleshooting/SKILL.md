---
name: spark-troubleshooting
metadata:
  category: DataProcessing
description: >-
  Diagnoses failed and stuck Spark jobs from driver/executor logs, UI
  metrics, and failure signatures: OOM, skew, missing files, and resource
  exhaustion. Use when a Spark job fails, hangs, or regresses after a change.
  Don't use for tuning slow-but-working jobs (use spark-optimization) or
  writing Spark code (use spark-basics).
allowed-tools:
  - spark-submit
  - pyspark
  - python
---

# Spark Troubleshooting

This skill classifies Spark failures by signature, extracts the authoritative
log, finds the root cause, remediates, and records the prevention.

## Prerequisites

- Access to driver logs (stdout/stderr) and the Spark UI or event logs.
- Knowledge of the job's expected input size and SLA.
- Read-only access to the cluster's monitoring (Cloud Logging, CloudWatch,
  Ganglia/Prometheus) for the affected period.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: reading logs, UI metrics, event log files, and
  driver/executor JVM settings.
- **Tier M (mutation)**: changing cluster configuration, re-running jobs,
  modifying code, and increasing resources. All MUST be confirmed by the
  user; re-running a failing job before fixing the cause wastes resources
  and may double-write.

## Workflow

### 1. Capture the Failure Facts

```bash
# driver log tail (example: YARN/Dataproc/EMR differ by platform)
yarn logs -applicationId {app_id} -log_files stdout | tail -200
```

Record: application ID, failed stage ID, task failure count, exception text,
and the job's input size. If the run "hung", note the last completed stage
and current running tasks.

### 2. Classify the Failure Signature

Map to [Failure Signatures](references/failure-signatures.md):

| Signature | Primary evidence |
| --- | --- |
| OOM (executor) | `OutOfMemoryError`, `Java heap space`, GC time >10% |
| OOM (driver) | `Driver stack trace`, `collect()` on large data |
| Disk/memory spill storm | massive "Spill (Disk)" in UI, slow stage |
| Skew | one task >> others in runtime, uneven task times |
| Missing input | `FileNotFoundError`, `Path does not exist`, zero input files |
| Serialization | `Task not serializable`, Kryo/Java errors |
| Resource exhaustion | `Container killed`, `YarnApplicationAttemptFinished` |
| Metadata/catalog | `Table not found`, schema mismatch on read |

### 3. Find the Root Cause

- **OOM**: check the UI executor page for per-executor spill; confirm the
  failing stage's shuffle size vs executor memory. Fix per
  spark-optimization memory guidance (partition count first, then memory).
- **Skew**: verify with a key-count query (see joins reference) — hot keys
  produce the classic "one task runs for hours".
- **Missing input**: confirm the path exists and the expected partitions
  were produced upstream; this is usually an upstream orchestration failure,
  not a Spark bug.
- **Serialization**: replace the UDF/lambda capturing non-serializable
  objects; prefer DataFrame/SQL functions.
- **Resource exhaustion**: check cluster capacity during the run window;
  queue contention or executor preemption is a platform issue.

### 4. Remediate (Confirmed Mutations)

- Code fix: apply per spark-basics/spark-optimization guidance; validate
  locally on a sample BEFORE cluster re-run.
- Config fix: apply the single config that addresses the signature (e.g.
  `spark.sql.adaptive.skewJoin.enabled=true` for skew), re-run, and keep it
  only if it helps.
- Data/upstream fix: coordinate with the producer; never patch downstream
  around missing data without agreement.

### 5. Verify and Prevent

- Re-run succeeds; failed stage completes; metrics improved.
- Add an alert/check that would have caught the signature earlier
  (e.g. input-size drop alert for missing-input class).
- Record: signature, root cause, fix, verification (see
  [Runbook Template](references/runbook-template.md)).

## Validation

- The exact failure is reproduced in a sample or the re-run completes clean.
- Failed stage now completes; no new failure signature introduced.
- Metrics (spill, task time variance, GC) are within healthy bounds.
- The final summary states root cause explicitly — never just "reran".

## Definition of Done

- Failure signature classified; root cause identified from logs/UI.
- Fix applied with confirmation; verification run succeeded.
- Prevention (alert/config/check) documented or added.
- No silent retries without diagnosis; no fabricated success.

## Reference Directory

- [Failure Signatures](references/failure-signatures.md): decision tree with
  diagnosis commands for each class.
- [Log & UI Field Guide](references/log-field-guide.md): where each signal
  lives in the Spark UI and driver logs.
- [Runbook Template](references/runbook-template.md): post-incident entry
  skeleton.

## Related Skills

- [Spark Optimization](../spark-optimization/SKILL.md): the tuning fixes this
  skill points at.
- [Spark Basics](../spark-basics/SKILL.md): rewrite guidance when the root
  cause is code structure.
- [Airflow Job Failure Troubleshooting](../../orchestration/airflow-job-failure-troubleshooting/SKILL.md):
  when the Spark failure surfaces through the orchestrator.
