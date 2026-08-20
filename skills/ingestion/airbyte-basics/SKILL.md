---
name: airbyte-basics
metadata:
  category: DataIngestion
description: >-
  Builds and operates ELT connectors with Airbyte: sources, destinations,
  sync modes, and normalization. Use when setting up sync-based ingestion
  with a wide connector catalogue. Don't use for streaming event ingestion
  (use kafka-connect) or code-first Python pipelines (use dlt-python-
  ingestion).
allowed-tools:
  - docker
  - curl
  - python
---

# Airbyte Basics

Airbyte syncs data from sources (SaaS APIs, databases, files) to
destinations (warehouses, lakehouses) with a managed connector catalogue,
schema handling, and scheduling.

## Prerequisites

- A running Airbyte instance (local Docker Compose: `abctl local install`,
  or Cloud/Enterprise).
- Destination configured (warehouse/lakehouse credentials per auth skill).
- Source access credentials (read-only preferred).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: listing sources/destinations, viewing connection
  status and sync history, test-connection probes.
- **Tier M (mutation)**: creating sources/destinations, enabling syncs,
  running sync jobs, and resetting streams. Resets truncate destination
  data and MUST be confirmed with the affected streams stated.

## Workflow

### 1. Create the Source

API or UI:

```bash
curl -s -X POST {airbyte}/api/v1/source_definitions/list | jq '.sourceDefinitions[] | {name, sourceDefinitionId}'
curl -s -X POST {airbyte}/api/v1/sources/create \
  -d '{"sourceDefinitionId":"{id}","connectionConfiguration":{...},"name":"my-source","workspaceId":"{ws}"}'
```

Test the source (`/api/v1/sources/check_connection`) BEFORE wiring a
connection.

### 2. Create the Destination

Repeat for the destination (BigQuery/Snowflake/S3/GCS...). Configure:
schema/namespace, credentials, and staging mode.

### 3. Define the Connection

```bash
curl -s -X POST {airbyte}/api/v1/connections/create \
  -d '{"sourceId":"{sid}","destinationId":"{did}","syncCatalog":{...},"schedule":{"units":1440,"timeUnit":"minutes"},"namespaceDefinition":"destination"}'
```

Sync mode decisions:

| Sync mode | Use |
| --- | --- |
| full refresh | small, stateless tables |
| incremental | large append-only tables with cursor |
| incremental + dedup | upsert-capable destinations |

### 4. Run and Validate

```bash
curl -s -X POST {airbyte}/api/v1/connections/sync -d '{"connectionId":"{cid}"}'
curl -s -X POST {airbyte}/api/v1/jobs/get -d '{"id":"{job_id}"}'
```

Verify: job status `succeeded`, records emitted match expectations, and the
destination table row counts line up. Check `records.synced` vs
`bytes.synced` per stream.

### 5. Handle Schema Changes

- Airbyte detects schema changes between syncs; per-stream policy:
  `propagate`, `propagate_columns`, or `block`.
- `propagate_columns` (additive) is the safe default; `block` for
  contract-pinned tables.
- Never silently `discard` columns a consumer needs — coordinate via data
  contracts.

### 6. Operationalize

- Schedule via Airbyte (minutes/hours/cron) or trigger from the
  orchestrator.
- Monitor: sync failures, per-stream records, and freshness of the
  destination `_airbyte_*` metadata columns.

## Validation

- `check_connection` passes for source and destination.
- A test sync emits the expected records with the expected schema.
- Destination table matches the sync count (probe `count(*)`).
- Incremental connections resume from the cursor (second sync adds only new
  rows).

## Definition of Done

- Source + destination created and tested.
- Connection defined with explicit sync modes and namespace policy.
- Test sync verified; counts match.
- Schedule operational; failure alerts wired.
- No credentials in connection configs (use Airbyte secret fields/env).

## Reference Directory

- [Sync Modes & Cursors](references/sync-modes.md): incremental mechanics
  and cursor pitfalls.
- [Schema Change Policy](references/schema-changes.md): handling drift
  safely.

## Related Skills

- [dlt (Python) Ingestion](../dlt-python-ingestion/SKILL.md): code-first
  alternative.
- [Kafka Connect](../kafka-connect/SKILL.md): event-stream ingestion.
- [File Ingestion (GCS/S3)](../file-ingestion-gcs-s3/SKILL.md): file-based
  batch loads.