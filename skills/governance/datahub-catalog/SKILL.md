---
name: datahub-catalog
metadata:
  category: DataGovernance
description: >-
  Operates DataHub as the metadata hub: ingesting schemas and lineage from
  platforms, managing the search index, and governing metadata quality.
  Use when setting up or maintaining the org's metadata catalog. Don't use
  for ad-hoc table lookups (the catalog UI is the tool) or for lineage
  event emission (use openlineage-basics).
allowed-tools:
  - python
  - curl
  - datahub
---

# DataHub Catalog

DataHub is the metadata hub: it collects schemas, lineage, ownership, and
contracts into one searchable catalog. This skill covers operating the
ingestion and keeping the catalog trustworthy.

## Prerequisites

- A running DataHub deployment (GMS + frontend) or a managed instance.
- `acryl-datahub` CLI installed (`pip install acryl-datahub`).
- A datahub GMS endpoint + credentials (token) per the auth skill.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `datahub get`, search/lineage API calls,
  inspecting ingestion runs.
- **Tier M (mutation)**: running ingest recipes (writes metadata),
  deleting/updating entities, and changing ingestion schedules. Metadata
  writes affect the whole org's catalog — confirm recipes on staging first.

## Workflow

### 1. Ingest from a Source

```yaml
# recipes/snowflake.yml
source:
  type: snowflake
  config:
    account_id: {account}
    username: {user}
    password: ${SNOWFLAKE_PASSWORD}
    database: analytics
sink:
  type: datahub-rest
  config:
    server: "http://datahub-gms:8080"
    token: ${DATAHUB_TOKEN}
```

```bash
datahub ingest -c recipes/snowflake.yml
```

Rules:

- Run ingestion from CI or a scheduler (cron), not ad-hoc — freshness of
  the catalog depends on it.
- Scope recipes to the databases the platform owns; do not ingest
  everything.
- Secret references via env vars only — never inline credentials.

### 2. Verify Ingestion

```bash
datahub get --urn urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.orders,PROD)
```

Rules:

- After a recipe run, spot-check: entities exist, schema fields correct,
  lineage edges present.
- Ingestion failures alert (watch the orchestrator task) — a silently
  stale catalog is worse than none.

### 3. Enrich with Ownership & Tags

Rules:

- Assign dataset owners (team + person) — this feeds the data-contracts
  escalation path.
- Use consistent tag vocabulary (`pii`, `gold`, `team:growth`); enforce
  via the platform docs.
- Glossary terms over freeform tags for business semantics.

### 4. Govern Metadata Quality

- Watch for: orphan datasets (no owner, no lineage), stale schemas
  (last-ingested > 30 days), duplicate entities.
- Quarterly audit: export the catalog, review orphans, clean up.

## Validation

- Recipe run completes; entities + lineage visible in the UI/API.
- Spot-check schema fields match the warehouse `DESCRIBE`.
- Ownership present on core datasets; tags follow the vocabulary.
- No orphaned/duplicate entities on core domains.

## Definition of Done

- Ingestion recipes run on schedule; freshness verified.
- Lineage graphs usable for blast-radius analysis.
- Ownership/tagging conventions applied to core datasets.
- Metadata quality audit scheduled.

## Reference Directory

- [Ingestion Recipes](references/ingestion-recipes.md): recipe patterns
  for the platform sources.
- [API & Search](references/api-search.md): querying the catalog
  programmatically.

## Related Skills

- [OpenLineage Basics](../openlineage-basics/SKILL.md): the event source
  feeding lineage.
- [Data Contracts](../data-contracts/SKILL.md): contracts live here.
- [Metadata Catalog Comparison](../metadata-catalog-comparison/SKILL.md):
  when DataHub is not the right choice.