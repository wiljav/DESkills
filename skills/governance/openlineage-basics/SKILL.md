---
name: openlineage-basics
metadata:
  category: DataGovernance
description: >-
  Instruments pipelines with OpenLineage events and uses lineage graphs to
  find upstream dependencies, blast radius, and data provenance. Use when
  mapping data flows or debugging upstream/downstream impact. Don't use for
  cataloging schemas (use datahub-catalog) or storing lineage long-term (see
  the datahub integration).
allowed-tools:
  - python
  - curl
---

# OpenLineage Basics

OpenLineage is an open standard for lineage metadata: jobs emit events
(`START`/`RUNNING`/`COMPLETE`/`FAIL`) describing inputs, outputs, and job
runs; a collector/marquez-style backend stores the graph.

## Prerequisites

- A lineage collector endpoint (OpenLineage-compatible, e.g. Marquez or
  DataHub's OpenLineage API) reachable from the pipeline environment.
- Python `openlineage-python` package (or the platform's native
  integration: Airflow `OpenLineageProvider`, dbt `dbt-ol`).
- Read access to the lineage API for queries.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: querying lineage (API/UI), reading events, tracing
  a dataset's history.
- **Tier M (mutation)**: enabling/instrumenting emitters in pipelines,
  changing collector config, and replaying events. Enabling an emitter adds
  events to the lineage backend — confirm before wiring it into shared
  platforms.

## Workflow

### 1. Enable the Integration

Airflow:

```python
# airflow.cfg
[lineage]
backend = openlineage.lineage_backend.OpenLineageBackend
```

dbt:

```bash
pip install dbt-ol
# profiles.yml
vars:
  openlineage: true
```

Spark:

```bash
--packages io.openlineage:openlineage-spark:{version}
--conf spark.openlineage.url=http://{collector}:5000
--conf spark.openlineage.namespace=de_prod
```

### 2. Verify Events Flow

```bash
curl -s http://{collector}:5000/api/v1/lineage | jq .
```

Rules:

- Namespace + job names MUST be stable: `de_prod` + the Airflow DAG id.
- Each job run emits START/RUNNING/COMPLETE/FAIL — a missing COMPLETE
  event means a failed/aborted run.

### 3. Use Lineage for Impact Analysis

Queries against the backend (example: find downstream of a table):

```bash
curl -s "http://{collector}:5000/api/v1/lineage?nodeId=dataset:s3://bucket/warehouse/curated/orders" | jq .
```

Rules:

- Before touching a table (schema change, backfill, drop): enumerate
  downstream jobs from lineage — this is the blast radius.
- Before investigating an anomaly: walk UPSTREAM to the source of the
  data in question.

### 4. Keep It Alive

- Lineage events are emitted at run time; the collector stores them.
- Monitor collector health (events lag) — stale lineage = false confidence
  in the blast-radius analysis.
- Standardize `namespace`/`job` naming in the platform docs so graphs
  stay connected across engines.

## Validation

- Events visible for a test run (START..COMPLETE in the API/UI).
- A known table shows its upstream sources and downstream jobs.
- Naming conventions match the platform docs (no orphan jobs).

## Definition of Done

- Emitters enabled on the pipeline platforms (Airflow/dbt/Spark as
  applicable).
- Collector verified healthy; events flowing.
- Lineage query workflow documented (blast radius before changes).

## Reference Directory

- [Event Model](references/event-model.md): the OpenLineage event shape and
  facets.
- [Collector Setup](references/collector-setup.md): backend options and
  deployment notes.

## Related Skills

- [DataHub Catalog](../datahub-catalog/SKILL.md): where lineage graphs are
  stored/queried alongside metadata.
- [Airflow Basics](../../orchestration/airflow-basics/SKILL.md): the main
  emitter platform.
- [dbt Core](../../transformation/dbt-core/SKILL.md): dbt-ol integration.