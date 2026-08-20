---
name: de-stack-getting-started
metadata:
  category: GettingStarted
description: >-
  Bootstraps a local data engineering toolchain: Python environment, Apache
  Spark, dbt, Airflow, DuckDB, and Docker. Use when setting up a development
  machine for the first time or when a pipeline skill reports missing tools.
  Don't use when the user already has a working environment, or for
  provisioning shared/cloud infrastructure (use terraform-for-data instead).
allowed-tools:
  - python
  - uv
  - docker
  - git
---

# Data Engineering Stack Setup

This skill sets up a reproducible local data engineering environment with the
core open-source tools used across this repository: Python, DuckDB, Apache
Spark, dbt, Apache Airflow (via Docker), and the repo tooling dependencies.

## Prerequisites

- A 64-bit OS with at least 8 GB RAM and 10 GB free disk.
- `git` installed and authenticated.
- Docker Desktop (or Docker Engine) running for the Airflow section.
- No conflicting global Python packages; this skill prefers isolated tooling.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: checking installed versions (`python --version`,
  `docker info`, `uv --version`), listing tool availability.
- **Tier M (mutation)**: installing system packages, creating virtual
  environments, pulling Docker images, editing shell profiles. Each install
  step MUST be shown to the user for approval before execution.

## Workflow

### 1. Inventory the Environment

Run all checks and record results before installing anything:

```bash
python3 --version
git --version
docker info >/dev/null 2>&1 && echo "docker: ok" || echo "docker: missing"
command -v uv && uv --version || echo "uv: missing"
```

If `uv` is missing, install it with the official installer (approval required):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create the Project Virtual Environment

Use `uv` to create an isolated environment with pinned core dependencies:

```bash
uv init --no-workspace --bare
uv add --dev ruff pytest
uv add duckdb pyarrow
```

Record the exact versions installed (`uv lock` writes `uv.lock`). The lockfile
MUST be committed so environments are reproducible.

### 3. Install the Data Toolchain

Install tools that provide CLI entry points:

```bash
uv tool install apache-airflow
uv tool install dbt-core
```

Verify each tool's version:

```bash
airflow version
dbt --version
duckdb --version
```

> If the user needs Spark locally, prefer `uv tool install pyspark`; the
> standalone Spark distribution is only needed for cluster-role experiments.

### 4. Stand Up the Local Airflow Environment

Prefer the Dockerized path (documented in `docker-airflow-dev`) because it
matches production images. At minimum:

```bash
mkdir -p ~/airflow/dags ~/airflow/logs ~/airflow/plugins
airflow standalone
```

`airflow standalone` boots a SQLite-backed scheduler + webserver on
`http://localhost:8080` with a printed initial password. It MUST NOT be used
for anything beyond local experimentation.

### 5. Smoke-Test the Toolchain

Execute a trivial pipeline across all three engines to prove the stack works:

```bash
duckdb -c "SELECT 'ok' AS engine;"
dbt debug --project-dir /tmp/dbt-probe
airflow dags list
```

## Validation

- Every tool in the inventory section reports a version (no "missing").
- `uv lock` exists and `uv sync` completes without errors.
- `docker info` succeeds and `airflow standalone` reaches the login page.
- `make ci` in the repository root passes (tooling deps installed).

## Definition of Done

- Python, uv, Docker, and git are installed with recorded versions.
- Project virtual environment exists with `uv.lock` committed.
- `airflow`, `dbt`, and `duckdb` CLIs are on PATH and report versions.
- Local Airflow boots and serves the UI on port 8080.
- No credentials were stored; any secrets belong to the auth skill workflow.

## Reference Directory

- [Tool Versions](references/tool-versions.md): tested version matrix and
  upgrade policy.
- [Troubleshooting Setup](references/troubleshooting.md): common setup
  failures (Docker not running, port conflicts, pip conflicts) and fixes.

## Related Skills

- [Data Engineering Authentication](../data-engineering-auth/SKILL.md):
  required before any cloud-backed tool works.
- [Dockerized Airflow Development](../../infrastructure/docker-airflow-dev/SKILL.md):
  the reproducible Airflow setup this skill points to.
- [MCP Servers for Data](../mcp-servers-for-data/SKILL.md): wiring agents to
  the data platform after the stack is up.