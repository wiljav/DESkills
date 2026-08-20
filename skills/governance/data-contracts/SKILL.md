---
name: data-contracts
metadata:
  category: DataGovernance
description: >-
  Designs, publishes, and enforces data contracts between producers and
  consumers: schema, semantics, quality SLAs, and breaking-change process.
  Use when introducing contracts or resolving producer/consumer disputes.
  Don't use for cataloging metadata (use datahub-catalog) or for schema
  validation inside pipelines (use great-expectations).
allowed-tools:
  - python
  - yaml
  - json
---

# Data Contracts

A data contract is the agreement between a producer and consumers: what a
dataset promises about its schema, semantics, quality, and availability.
Contracts turn implicit assumptions into explicit, testable promises.

## Prerequisites

- An identified dataset boundary (table, topic, file group).
- Named producer and consumer owners (can be same team).
- A contract repository (Git-based) and a registry/format to publish to
  (DataHub schema/contract support or a plain YAML file in the repo).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: reading contracts, comparing versions, auditing
  compliance.
- **Tier M (mutation)**: creating/editing contracts and publishing new
  versions. Contract version bumps affect consumers — every breaking
  change requires the confirmation process in the workflow.

## Workflow

### 1. Define the Contract Shape

```yaml
dataset: analytics.orders
version: "1.2.0"
owner:
  team: checkout-platform
  channel: "#data-producers"
consumers:
  - team: growth-analytics
    use: reporting
schema:
  fields:
    order_id:
      type: STRING
      required: true
      semantic: order identifier
    amount:
      type: DECIMAL(12,2)
      required: true
      semantic: gross order value in USD
    event_date:
      type: DATE
      required: true
  partition: event_date
quality:
  row_count_delta: within 5% day over day
  null_rate: amount < 1%
  freshness: loaded by 06:00 UTC
availability:
  sla: 99.9%
  disaster_recovery: 24h
semantics:
  dedup_key: order_id
  retention: 7 years
```

### 2. Publish and Version

Rules:

- Semver: `MAJOR` = breaking (rename/drop/type change of a field);
  `MINOR` = additive; `PATCH` = clarification.
- Every change is a commit in the contracts repo — the Git history IS the
  decision log.
- Publish to the registry the consumers actually read (DataHub or the
  repo itself).

### 3. Enforce with Tests

- Schema: validate with great-expectations expectations generated from the
  contract fields.
- Quality: the SLAs in the contract become the pipeline's test suite
  (dbt tests / GE suites).
- Availability: freshness monitoring per data-observability.

```python
# generate GE expectations from the contract (pseudo)
for f in contract.schema.fields:
    suite.add_expectation(expect_column_values_to_not_be_null, column=f.name)
```

### 4. Handle Breaking Changes

Process (Tier M — confirm with the producer AND affected consumers):

1. Propose `MAJOR` bump with a migration note.
2. Notify consumers in the agreed channel; minimum notice = contract
   term (e.g. 2 weeks).
3. Dual-write or add the new field alongside the old where possible
   (backward-compatible).
4. Only after consumers confirm migration: publish the new version.

### 5. Audit Compliance

- Quarterly: compare contract promises vs measured reality
  (quality metrics vs SLAs).
- Flag contracts older than 12 months with no version activity (stale).

## Validation

- Contract validates against the registry schema; version bumps follow
  semver rules.
- GE/dbt suites derived from the contract pass.
- Breaking-change flow followed: notice given, consumers confirmed.
- SLA audit shows the contract's promises met or a corrective ticket filed.

## Definition of Done

- Contract published for the dataset with schema/quality/availability
  sections.
- Enforcement tests exist and pass.
- Breaking-change process documented and exercised when needed.
- SLA audit scheduled (quarterly).

## Reference Directory

- [Contract Sections Explained](references/contract-sections.md): what each
  section must contain and why.
- [Change Management Playbook](references/change-management.md): the full
  breaking-change flow with templates.

## Related Skills

- [Great Expectations](../../quality/great-expectations/SKILL.md): turning
  contract schema/SLA into tests.
- [DataHub Catalog](../datahub-catalog/SKILL.md): where contracts live and
  are discovered.
- [Data Quality Incident Runbook](../../quality/data-quality-incident-runbook/SKILL.md):
  what happens when a contract promise breaks.