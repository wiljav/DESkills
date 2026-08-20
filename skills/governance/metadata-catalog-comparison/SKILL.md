---
name: metadata-catalog-comparison
metadata:
  category: DataGovernance
description: >-
  Compares metadata platforms (DataHub, OpenMetadata, Atlan, Amundsen,
  Marquez) and selects one for the org: features, maturity, and migration
  paths. Use when choosing or evaluating a metadata catalog. Don't use for
  operating the chosen tool (use datahub-catalog or the tool's own skill).
allowed-tools:
  - python
---

# Metadata Catalog Comparison

Choosing a metadata platform is a long-lived decision. This skill frames
the evaluation so the choice is driven by requirements, not hype.

## Prerequisites

- A written list of the org's metadata needs (see Workflow step 1).
- Current inventory: what pipelines, warehouses, and tools exist today.
- Stakeholder list (producers, consumers, compliance, platform).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: reading docs, running POCs on isolated
  instances, comparing feature matrices.
- **Tier M (mutation)**: committing to a platform (pilots on shared
  infrastructure, production ingestion). Any production commitment MUST be
  confirmed with the platform team and stakeholders.

## Workflow

### 1. Define Requirements

Score each requirement as `must` / `should` / `nice`:

- Schema + column-level metadata
- Lineage (job and column level)
- Data quality integration (GE/Soda/dbt results)
- Data contracts
- Business glossary / tags / ownership
- Access control (RBAC/SSO)
- OpenLineage compatibility (openlineage-basics)
- Deployment model (self-host vs SaaS)
- Team size available to operate it

### 2. Compare Candidates

| Tool | Strengths | Watch out for |
| --- | --- | --- |
| DataHub | deep lineage, wide source coverage, active OSS | operator effort; feature churn |
| OpenMetadata | integrated quality + glossary, simpler UX | smaller lineage depth in places |
| Atlan | polished UX, strong governance UX | SaaS-centric; cost |
| Amundsen | simple search, low ops | limited lineage/quality, slowing OSS |
| Marquez | focused lineage store | metadata hub only, not full catalog |

### 3. Run a Two-Week POC

Rules:

- POC on ONE core domain (e.g. `analytics.orders` + its pipelines).
- Success criteria from step 1, each scored by the same rubric.
- Include the daily-driver use cases: search, lineage walk, ownership
  lookup, quality badges.
- Decision gate: score vs requirements; the winner must beat the
  incumbent or stay.

### 4. Decide and Migrate

- If an incumbent exists, weigh migration cost: extract lineage from the
  old tool, re-create ownership/tags, re-point ingest recipes.
- Phased: catalog core domains first; legacy metadata stays read-only.

### 5. Revisit

- Schedule a re-evaluation every 18-24 months (or on a must-have gap).

## Validation

- Requirements matrix documented with scores.
- POC ran against the rubric with stakeholder sign-off.
- Decision recorded with the rationale + migration plan.
- No tool adopted without a pilot on real pipelines.

## Definition of Done

- Requirements ranked; comparison matrix filled.
- POC completed on one core domain with scored results.
- Decision + migration plan approved and recorded.
- Re-evaluation date scheduled.

## Reference Directory

- [Evaluation Rubric](references/rubric.md): the scoring template.
- [Migration Notes](references/migration.md): leaving a legacy catalog.

## Related Skills

- [DataHub Catalog](../datahub-catalog/SKILL.md): the operational skill if
  DataHub wins.
- [OpenLineage Basics](../openlineage-basics/SKILL.md): the lineage event
  standard that feeds any catalog.
- [Data Contracts](../data-contracts/SKILL.md): catalog-housed contracts.