# Prod Parity Notes

## What local CAN'T replicate

- Celery/K8s executor semantics (concurrency, queues) — test scheduling
  logic, not scale.
- Managed secrets — local dummies vs real vault integration.
- Multi-node/cloud networking (VPCs, IAM).

## What MUST match

- Airflow version + core config (`AIRFLOW__CORE__*`).
- DAG code itself (mount = the repo).
- Timezone (UTC) and DAG schedule intervals.
- Provider/package versions in the requirements.

## Gap mitigations

- Run CI DAG-parsing checks (airflow scheduler in check mode) on PRs —
  catches import errors that local setups might mask.
- Use the same image tag in CI test jobs as production deploys.
- Treat local success as necessary, not sufficient: staging runs remain
  the gate before prod.