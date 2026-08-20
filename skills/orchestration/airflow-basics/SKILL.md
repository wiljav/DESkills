---
name: airflow-basics
metadata:
  category: Orchestration
description: >-
  Installs, configures, and operates Apache Airflow as a pipeline
  orchestrator: scheduler, webserver, connections, variables, and secrets
  backends. Use when standing up or maintaining an Airflow environment, or
  when a DAG fails for environment-level reasons. Don't use for writing DAG
  code (use airflow-dag-authoring) or for diagnosing task-level failures
  (use airflow-job-failure-troubleshooting).
allowed-tools:
  - airflow
  - docker
  - python
---

# Apache Airflow Basics

Airflow is a platform to programmatically author, schedule, and monitor
workflows as DAGs. This skill covers the environment: components, settings,
connections, variables, and the secrets backend.

## Prerequisites

- A running Airflow environment (see `docker-airflow-dev` for local setup or
  use managed Airflow / Cloud Composer / MWAA).
- `airflow` CLI available on the target environment.
- Credentials per the `data-engineering-auth` skill for cloud-backed
  connections.
- Understanding of what a DAG is; authoring itself is covered by
  `airflow-dag-authoring`.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `airflow config list`, `airflow dags list`,
  `airflow connections list`, `airflow variables list`, inspecting logs.
- **Tier M (mutation)**: creating connections, setting variables, changing
  config, DB migrations (`airflow db migrate`), and restarting components.
  Each mutation MUST be confirmed by the user; connection strings contain
  secrets and must never be echoed fully.

## Workflow

### 1. Identify the Environment

Confirm which deployment you are operating:

```bash
airflow version
airflow config get-value core executor
airflow config get-value database sql_alchemy_conn | sed 's/:.*@/:***@/'
```

Record executor (Sequential/Local/Celery/Kubernetes) and metadata DB type;
they determine what configuration is relevant below.

### 2. Inspect Core Configuration

Show non-secret settings the platform depends on:

```bash
airflow config list | grep -E "parallelism|max_active_tasks_per_dag|max_active_runs_per_dag|dag_dir_list_interval|load_examples"
```

- Confirm `dag_dir_list_interval` matches the expected DAG refresh cadence.
- Confirm `load_examples = False` on production environments.

### 3. Manage Connections

List connections without revealing secrets:

```bash
airflow connections list
```

Create a connection from a URI while keeping the password masked in output:

```bash
airflow connections add {conn_id} \
  --conn-uri 'postgresql+psycopg2://{user}:***@{host}:5432/{db}'
```

MUST follow the rules:

- Use the provider's `{conn_type}+{driver}` URI scheme for the target tool
  (e.g. `google-cloud-platform://` for GCP, `aws://` for AWS).
- Prefer the secrets backend (step 4) over inline connection strings where
  the platform supports it.

### 4. Configure the Secrets Backend

For any credential-bearing connection, store values in a secrets backend
(Vault, AWS Secrets Manager, GCP Secret Manager) and point Airflow at it.
Example for GCP Secret Manager (must be confirmed before applying):

```bash
airflow config set secrets backend \
  airflow.providers.google.secrets.cloud_secret_manager.CloudSecretManagerBackend
airflow config set secrets backend_kwargs '{"project_id": "{project}"}'
```

Verify resolution by fetching a connection stored only in the backend:

```bash
airflow connections get {conn_id} --json | python3 -c "import sys,json; print(json.load(sys.stdin)['conn_type'])"
```

### 5. Validate Environment Health

Run the platform self-checks:

```bash
airflow db check
airflow dags list-import-errors
airflow scheduler --help >/dev/null && echo "scheduler CLI: ok"
```

- `airflow db check` must exit 0.
- `dags list-import-errors` must return no rows; import errors are the top
  cause of "missing DAG" complaints.

## Validation

- Executor and metadata DB are identified and match the deployment type.
- All connections resolve against the secrets backend without printing
  secrets.
- `airflow db check` passes; `dags list-import-errors` is empty.
- Config changes were reverted or explicitly approved, and a restart was
  performed if the setting requires it.

## Definition of Done

- Environment components and executor are documented.
- Connections are stored via the secrets backend; none rely on inline
  plaintext in DAG code.
- Import errors are zero; scheduler is parsing DAGs.
- No secret value was printed or committed at any point.

## Reference Directory

- [Core Concepts](references/core-concepts.md): components, executor
  comparison, and scheduling model.
- [Connections & Variables](references/connections-variables.md): URI
  formats per provider and variable best practices.

## Related Skills

- [Airflow DAG Authoring](../airflow-dag-authoring/SKILL.md): the code this
  environment runs.
- [Dockerized Airflow Development](../../infrastructure/docker-airflow-dev/SKILL.md):
  local environment setup.
- [Airflow Job Failure Troubleshooting](../airflow-job-failure-troubleshooting/SKILL.md):
  what to do when tasks fail.