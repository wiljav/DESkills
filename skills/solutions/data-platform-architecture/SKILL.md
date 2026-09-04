---
name: data-platform-architecture
metadata:
  category: Solutions
description: >-
  Designs a production data platform: zones, tool selection, governance
  blueprint, and team boundaries. Use when architecting or reviewing the
  overall platform. Don't use for building single pipelines (use
  batch-etl-pipeline or streaming-analytics-pipeline) or tool
  configuration (use the domain skills).
allowed-tools:
  - python
  - bash
---

# Data Platform Architecture

The blueprint skill: how the zones, tools, governance, and teams fit into
one production platform. Every domain skill implements a corner of this
design.

## Prerequisites

- Stakeholder list (producers, consumers, compliance, platform).
- Current-state inventory (sources, warehouses, pipelines, licenses).
- The requirements this platform must serve (latency, volume, SLA,
  compliance).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: reading architecture docs, evaluating options,
  producing design documents.
- **Tier M (mutation)**: committing architecture decisions (tool
  selection, zone design, governance structure). Decisions are
  long-lived — confirm with stakeholders before codifying.

## Workflow

### 1. Define Zones

```text
landing      raw source data, immutable, access-controlled
  -> raw       same data, organized/registered (bronze)
  -> curated   conformed, typed, documented (silver)
  -> marts     semantic, business-ready (gold)
  -> serving   BI/API/ML surfaces
```

Rules:

- Landing/raw: append-only, reprocessible — the reprocessing guarantee.
- Curated: contract-backed, owned by the transformation team.
- Marts: business-owned semantics.
- Every zone has: owner, access policy, retention, and observability.

### 2. Select Tools by Requirement

| Capability | Options (multi-cloud) |
| --- | --- |
| Orchestration | Airflow / Dagster / Prefect |
| Ingestion | dlt / Airbyte / Kafka Connect |
| Processing | Spark / Flink / DuckDB |
| Transformation | dbt |
| Storage | S3 / GCS + Iceberg or Delta |
| Warehouse | BigQuery / Snowflake / Redshift / lakehouse SQL |
| Catalog | DataHub / OpenMetadata |
| Quality | GE / Soda / dbt tests |

Rules:

- Choose by: team skills, existing contracts, latency needs, cost
  model — documented via metadata-catalog-comparison-style scoring.
- Prefer open standards (OpenLineage, Iceberg) for lock-in protection.
- Minimal set: every extra tool is an ops burden (the catalog comparison
  rubric applies to ALL selections).

### 3. Design Governance

- Ownership: every dataset has a team + contract (data-contracts).
- Lineage: OpenLineage events from all orchestrators (openlineage-basics).
- Catalog: schemas, lineage, quality results in one hub
  (datahub-catalog).
- PII: classification + masking per sensitivity (pii-classification-and-masking).
- Access: least-privilege roles; short-lived credentials
  (data-engineering-auth).

### 4. Define Platform Operating Model

| Concern | Owner |
| --- | --- |
| Cluster/warehouse capacity | platform team |
| Pipeline development | domain teams |
| Data quality SLAs | domain teams + data owners |
| Security/compliance | security team |
| Metadata hygiene | platform + data owners |

- SLAs: freshness per zone (raw < 12h, marts < 6h after raw, etc.).
- Environments: dev/ci/prod with promotion gates (ci-cd-for-dbt
  pattern).

### 5. Document and Review

- Architecture Decision Records (ADRs) for every committed decision:
  context, decision, consequences.
- Quarterly review: new requirements vs current design; tool renewal
  schedule per metadata-catalog-comparison.

## Validation

- Every zone has owner/access/retention/observability defined.
- Tool selections documented with the requirement rationale.
- Governance blueprint covers ownership, lineage, catalog, PII, access.
- ADRs exist for all major decisions.

## Definition of Done

- Architecture document: zones, tools, governance, operating model.
- ADRs for decisions; review cadence scheduled.
- The design maps to concrete domain skills for implementation.

## Reference Directory

- [Zone Design Details](references/zones.md): deep dive on boundaries and
  policies.
- [ADR Template](references/adr.md): the decision record format.

## Related Skills

- [Batch ETL Pipeline](../batch-etl-pipeline/SKILL.md): the batch
  implementation of this design.
- [Streaming Analytics Pipeline](../streaming-analytics-pipeline/SKILL.md):
  the streaming implementation.
- [Metadata Catalog Comparison](../../governance/metadata-catalog-comparison/SKILL.md):
  the selection method.
- [Data Contracts](../../governance/data-contracts/SKILL.md): the
  governance backbone.
