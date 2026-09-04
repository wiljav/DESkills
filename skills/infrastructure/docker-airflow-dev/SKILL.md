---
name: docker-airflow-dev
metadata:
  category: DataInfrastructure
description: >-
  Stands up a reproducible local Airflow development environment with
  Docker Compose: scheduler, webserver, workers, and connections to local
  engines. Use when developing DAGs locally or onboarding new engineers.
  Don't use for production Airflow deployment (production patterns differ)
  or non-Docker environments.
allowed-tools:
  - docker
  - bash
---

# Dockerized Airflow Development

A local Airflow environment must match production closely enough to trust
local DAG testing. This skill builds that environment with Docker Compose.

## Prerequisites

- Docker Desktop (macOS/Windows) or a Linux Docker daemon.
- The Airflow image matching your production version
  (`apache/airflow:{version}`).
- Git + the DAG repo you develop in.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `docker compose ps`, logs, `airflow dags list`,
  `airflow tasks list`.
- **Tier M (mutation)**: creating/removing containers, volumes, and
  connections; running DAG backfills locally. Volume resets (below) erase
  local state — confirm before wiping.

## Workflow

### 1. Scaffold the Compose Environment

```yaml
# docker-compose.yml (skeleton)
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: airflow
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
    volumes: [airflow_db:/var/lib/postgresql/data]

  airflow-init:
    image: apache/airflow:2.10.0
    depends_on: [postgres]
    environment: &airflow_env
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    entrypoint: ["airflow", "db", "init"]

  scheduler:
    image: apache/airflow:2.10.0
    depends_on: [airflow-init]
    environment: *airflow_env
    volumes:
      - ./dags:/opt/airflow/dags
      - ./plugins:/opt/airflow/plugins
    command: ["airflow", "scheduler"]

  webserver:
    image: apache/airflow:2.10.0
    depends_on: [airflow-init]
    environment: *airflow_env
    ports: ["8080:8080"]
    volumes:
      - ./dags:/opt/airflow/dags
      - ./plugins:/opt/airflow/plugins
    command: ["airflow", "webserver"]
```

Rules:

- Mount `./dags` (and `./plugins`) as bind mounts — the point is hot
  reload.
- Use LocalExecutor for local dev (Celery adds containers with no value
  locally).
- Pin the Airflow image version to production's.

### 2. Start and Verify

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f scheduler
open http://localhost:8080   # airflow/airflow by default
```

Verification checklist:

- Webserver up; DAGs list in the UI.
- Scheduler parses DAGs with no import errors (check scheduler logs).
- One test DAG runs to completion on `trigger_dag`.

### 3. Add Local Engine Services

```yaml
  spark:
    image: bitnami/spark:3.5
    ports: ["4040:4040"]
  duckdb-postgres:  # or a local Postgres target
    image: postgres:16
    environment:
      POSTGRES_DB: analytics
```

- Add the engines your DAGs touch; create Airflow connections to them
  (see below).

### 4. Configure Connections

```bash
docker compose exec webserver \
  airflow connections add local_postgres \
  --conn-type postgres --conn-host postgres \
  --conn-login airflow --conn-password airflow --conn-port 5432
```

Rules:

- Connections via CLI or env vars
  (`AIRFLOW_CONN_LOCAL_POSTGRES=postgres://...`), NOT the UI (not
  reproducible).
- Keep local credentials dummy; production secrets live in the secret
  manager (auth skill).

### 5. Test DAGs Locally

```bash
docker compose exec scheduler airflow dags test {dag_id} 2024-01-01
docker compose exec scheduler airflow tasks test {dag} {task} 2024-01-01
```

Rules:

- `airflow dags test` runs the DAG in-process — perfect for logic checks.
- Task isolation: `airflow tasks test` runs a single task with its own
  context.

### 6. Reset When Needed

```bash
docker compose down -v     # destroys local DB + volumes (confirmed!)
docker compose up -d --build
```

- `-v` wipes volumes — used for a clean slate; confirm before running.

## Validation

- Webserver + scheduler healthy; DAGs parse clean.
- Test DAG completes locally; tasks hit the local engines as expected.
- Connections reproducible via CLI/env (no UI-only config).

## Definition of Done

- Compose file committed to the DAG repo; image pinned.
- Local engines + connections working; DAG tests pass locally.
- Reset procedure documented in the repo README.

## Reference Directory

- [Debugging Locally](references/debugging.md): log inspection, task
  reruns, and scheduler issues.
- [Prod Parity Notes](references/prod-parity.md): what differs from
  production and why it matters.

## Related Skills

- [Airflow Basics](../../orchestration/airflow-basics/SKILL.md): the
  platform this containerizes.
- [Airflow DAG Authoring](../../orchestration/airflow-dag-authoring/SKILL.md):
  what to write inside the DAGs.
- [Data Engineering Auth](../../platform/data-engineering-auth/SKILL.md):
  real credentials vs local dummies.
