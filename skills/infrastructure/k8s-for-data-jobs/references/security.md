# Security & Secrets

## Service accounts & RBAC

- Every workload runs under a service account (never the default SA).
- Spark: `spark.kubernetes.authenticate.serviceAccountName` with a role
  granting pod get/create/delete within the namespace.
- Airflow: the K8s executor uses a SA with pod-permission; the webserver
  SA stays read-only.

## Secrets

- `kubectl create secret generic de-secrets --from-env-file=secrets.env`
  (secrets.env from the secret manager, never Git).
- Referenced via `secretRef` env entries; `stringData` for literal values.
- Rotate on the platform's schedule; a secret change = pod restart.

## Image security

- Pin image digests in production manifests
  (`image: registry.local/de/etl:1.4.2@sha256:...`).
- Scan images in CI (trivy-style gate); no `latest` tags in prod.

## Network

- Default deny: egress via policy only for the ports the jobs need
  (warehouse, storage, orchestrator).
- Never expose data-job pods via services to the internet.