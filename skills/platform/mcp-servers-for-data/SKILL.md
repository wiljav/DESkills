---
name: mcp-servers-for-data
metadata:
  category: GettingStarted
description: >-
  Connects AI agents to data platforms through Model Context Protocol (MCP)
  servers: warehouses, catalogs, and orchestrators. Use when an agent needs
  direct query, metadata, or lineage access to a data platform instead of
  shell commands. Don't use for credential setup (use data-engineering-auth)
  or for choosing between catalog products (use metadata-catalog-comparison).
allowed-tools:
  - uv
  - python
---

# MCP Servers for Data

Model Context Protocol (MCP) servers expose data platforms to agents as typed
tools: run a warehouse query, look up a table in the catalog, fetch lineage,
or inspect a DAG run. This skill wires those servers into an agent session.

## Prerequisites

- Agent harness with MCP client support (opencode, Claude Code, Codex, or
  similar) and the ability to register external MCP servers.
- Credentials configured per the `data-engineering-auth` skill.
- Network access to the target platforms (no VPC-restricted endpoints for
  local sessions).
- `uv` installed for Python-based servers.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: listing available MCP tools, testing `read` /
  `query` tools against `SELECT`-only statements, verifying server health.
- **Tier M (mutation)**: registering servers that expose write tools
  (DDL, `CREATE`, `INSERT`), granting MCP servers scopes, and connecting to
  production endpoints. Require explicit user confirmation and record which
  tools are write-capable.

## Workflow

### 1. Identify the Data Platform Surfaces

Determine which platforms the session needs:

| Need | Suggested MCP server |
| --- | --- |
| Warehouse queries | BigQuery / Snowflake / Redshift MCP servers |
| Catalog + lineage | DataHub / Knowledge Catalog MCP |
| Orchestration | Airflow / Dagster MCP |
| Object storage | S3 / GCS MCP (file listing, reads) |

Check the repository marketplace manifests
(`.claude-plugin/marketplace.json`) for plugins this repo ships.

### 2. Install and Register the Server

Python servers are typically installed via `uvx` so the session does not
pollute the project environment:

```bash
uvx {mcp-server-package} --help
```

Register the server in the harness configuration with:

- `command`: `uvx` (or the server binary).
- `args`: server-specific flags (e.g. `--project {project}`).
- `env`: scoped credentials only (see auth skill; never hardcode).

Verify registration: the harness should now list the server's tools (e.g.
`bigquery_query`, `datahub_search`).

### 3. Scope and Test Permissions

For each exposed tool, determine its tier:

```bash
# Example: test a warehouse MCP server with a read-only probe
{server} probe --query "SELECT 1"
```

- Mark write tools explicitly; prefer server configurations that expose
  read-only modes (e.g. `--read-only` flags).
- Test one happy-path call and one error path (invalid table name) and
  record the expected error shape so the agent can recognize it later.

### 4. Document the Wiring

Record in the session/project docs: server name, install command, env vars
used (names only), tool prefixes, and any `--read-only` flag applied. This
enables the next session to reproduce the setup without rediscovery.

## Validation

- `tools/list` on the harness returns the expected tools.
- A read-only probe query returns correct data for both an existing and a
  nonexistent table (error handled gracefully).
- No write tool was invoked without explicit user confirmation.
- Credentials used are short-lived and were not written to the repository.

## Definition of Done

- Required MCP servers registered and listed by the harness.
- Read/write tool boundaries documented; write tools gated by confirmation.
- Probe queries succeed against the target platform.
- Wiring notes captured so the setup is reproducible.
- No secrets committed; credential names only, never values.

## Reference Directory

- [Common Server Catalogue](references/server-catalogue.md): popular MCP
  servers per data platform and their install commands.
- [Troubleshooting MCP](references/troubleshooting.md): registration failures,
  auth errors, and tool-not-found diagnosis.

## Related Skills

- [Data Engineering Authentication](../data-engineering-auth/SKILL.md):
  credentials for the servers wired here.
- [Metadata Catalog Comparison](../../governance/metadata-catalog-comparison/SKILL.md):
  decide which catalog MCP server to install.
- [Data Engineering Stack Setup](../de-stack-getting-started/SKILL.md):
  base toolchain that `uvx` depends on.
