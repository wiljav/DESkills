---
name: k8s-for-data-jobs
metadata:
  category: DataInfrastructure
description: >-
  Runs batch and streaming workloads on Kubernetes: pod specs, resource
  requests, KubernetesExecutor for Airflow, and Spark-on-K8s. Use when
  deploying data jobs to a cluster. Don't use for cluster administration
  (platform team scope) or cloud-specific managed compute (vendor docs).
allowed-tools:
  - kubectl
  - helm
  - bash
---

# Kubernetes for Data Jobs

Kubernetes gives data workloads elasticity: jobs scale per run, and the
orchestrator (Airflow K8sExecutor, Spark-on-K8s, or plain Jobs) drives the
lifecycle.

## Prerequisites

- A cluster with kubectl access (RBAC-scoped) or the platform's CI/CD
  path.
- Helm (or kubectl) to apply manifests.
- Resource conventions from the platform team (namespaces, quotas).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `kubectl get/describe/logs`, `top`, `explain`.
- **Tier M (mutation)**: creating/deleting workloads, changing resource
  requests/limits, and scaling. Deletions and resource changes affect
  running pipelines — confirm with the workload owner.

## Workflow

### 1. Inspect the Namespace

```bash
kubectl get ns
kubectl get pods -n de
kubectl describe pod {pod} -n de
kubectl logs {pod} -n de --tail=200
```

### 2. Define a Job Manifest

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: orders-daily-{run_id}
  namespace: de
spec:
  backoffLimit: 2
  ttlSecondsAfterFinished: 86400
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: etl
          image: registry.local/de/etl:1.4.2
          resources:
            requests: { cpu: "1", memory: 4Gi }
            limits:   { cpu: "2", memory: 8Gi }
          envFrom:
            - secretRef: { name: de-secrets }
```

Rules:

- `resources.requests` = what the scheduler reserves; `limits` = the cap.
  Set both; mismatched ratios cause evictions.
- `ttlSecondsAfterFinished` cleans up finished jobs (no pod leakage).
- Secrets via `secretRef` — never inline.

### 3. Airflow KubernetesExecutor

```python
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

run_job = KubernetesPodOperator(
    task_id="orders_etl",
    namespace="de",
    image="registry.local/de/etl:1.4.2",
    resources={"request_cpu": "1", "request_memory": "4Gi",
               "limit_cpu": "2", "limit_memory": "8Gi"},
    secrets=[k8s.Secret("de-secrets", None, "DB_PASSWORD")],
    is_delete_operator_pod=True,
    dag=dag,
)
```

Rules:

- One pod per task = clean isolation + per-run resource sizing.
- `is_delete_operator_pod=True` avoids pod accumulation.
- Pin images; tag-float (`latest`) is a deployment anti-pattern.

### 4. Spark on Kubernetes

```bash
spark-submit \
  --master k8s://https://{api-server} \
  --deploy-mode cluster \
  --conf spark.kubernetes.namespace=de \
  --conf spark.kubernetes.container.image=registry.local/de/spark:3.5 \
  --conf spark.executor.instances=4 \
  --conf spark.executor.memory=4g \
  --conf spark.kubernetes.authenticate.serviceAccountName=spark-sa \
  jobs/orders_etl.py
```

Rules:

- Spark's K8s scheduler creates executors per run; driver + executors
  need a service account with pod-create RBAC.
- Set `spark.kubernetes.allocation.driver.node.selector`/tolerations per
  platform convention.

### 5. Monitor and Triage

```bash
kubectl get pods -n de -w
kubectl top pods -n de
kubectl describe pod {pod} -n de   # events show OOMKilled / Evicted
```

Rules:

- `OOMKilled`: bump memory limit OR fix the job's memory use
  (spark-troubleshooting first).
- `Evicted`: node pressure — re-check requests vs cluster capacity.
- CrashLoopBackOff: application bug — logs first, manifests second.

## Validation

- Job completes with `Succeeded` status; pod cleaned by TTL.
- Resources honored (`kubectl top` within requests/limits).
- Orchestrator integration (Airflow/Spark) reports success.

## Definition of Done

- Job manifests follow the conventions (namespace, resources, TTL,
  secretRef).
- Orchestrator integration working; images pinned.
- Monitoring path documented (describe/logs/top for triage).

## Reference Directory

- [Resource Management](references/resources.md): requests/limits,
  eviction, and quotas.
- [Security & Secrets](references/security.md): RBAC, service accounts,
  and secret handling.

## Related Skills

- [Spark Basics](../../processing/spark-basics/SKILL.md): the workload
  being scheduled.
- [Terraform for Data](../terraform-for-data/SKILL.md): cluster
  provisioning above this layer.
- [Airflow Job Failure Troubleshooting](../../orchestration/airflow-job-failure-troubleshooting/SKILL.md):
  pod-level failures in DAG context.
