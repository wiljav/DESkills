---
name: lakehouse-migration
metadata:
  category: Solutions
description: >-
  Migrates a data warehouse to an open lakehouse with staged cutover:
  inventory, format conversion, validation, and parallel-run. Use when
  planning or executing a warehouse-to-lakehouse migration. Don't use for
  single-table conversions (do those in the domain skills) or greenfield
  builds (use batch-etl-pipeline).
allowed-tools:
  - python
  - sql
  - bash
---

# Lakehouse Migration

Moving from a warehouse to an open lakehouse (Iceberg/Delta on object
storage) trades managed convenience for openness and cost. This skill is
the staged migration playbook.

## Prerequisites

- The inventory (databases/tables) and the target lakehouse platform
  (iceberg-basics / delta-lake-basics + object-storage-basics).
- The warehouse's access controls and the target's equivalents.
- Downtime windows and stakeholders (consumers of each table).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: inventory queries, sampling, read-only
  comparisons.
- **Tier M (mutation)**: creating lakehouse tables, cutover switches,
  and warehouse decommissioning. Cutover affects all consumers — follow
  the staged approval gates below.

## Workflow

### 1. Inventory and Triage

```sql
-- warehouse inventory (example: BigQuery)
SELECT table_schema, table_name, row_count,
       ROUND(size_bytes/1e9, 1) AS size_gb
FROM `region-us`.INFORMATION_SCHEMA.TABLES
ORDER BY size_gb DESC;
```

Rules:

- Rank by: size, consumer count, complexity (joins, stored procedures).
- Triage: migrate as-is / redesign / leave behind (archival).

### 2. Set Up the Target

```bash
# Iceberg REST catalog + bucket per iceberg-basics
aws s3 mb s3://de-lakehouse/
# catalog registered; warehouse schema mapping defined
```

Rules:

- Map warehouse schemas -> lakehouse database/namespace 1:1 initially
  (less consumer churn).
- Define naming/lifecycle before the first table lands.

### 3. Migrate in Waves

Wave plan (confirm each wave):

1. **Wave 0**: dimensions/small tables — prove the pattern.
2. **Wave 1**: mid-size facts — load + validation scripts.
3. **Wave 2**: largest facts — parallel-run + cutover.

Per table:

```python
# pseudo: full load with validation
load(source="warehouse.table", target="iceberg.namespace.table",
     partition_by="event_date")
validate_counts(source, target)     # row count + checksum on key columns
```

Rules:

- One migration job per table (idempotent, resumable).
- Validate: row counts, null rates, checksums on key columns, and the
  warehouse's own tests (dbt suite) re-run on the lakehouse copy.

### 4. Parallel-Run Before Cutover

- Run both systems in parallel for one reporting cycle; compare daily
  outputs.
- Freeze warehouse writes only for the cutover window (dual-write or
  replay).

### 5. Cutover

```text
1. Freeze warehouse writes for the table (maintenance window).
2. Final incremental load into the lakehouse (catch-up).
3. Re-run validation (counts must match exactly).
4. Switch consumers (connection strings, dbt profiles, BI sources).
5. Verify consumer dashboards against the lakehouse.
6. Un-freeze; warehouse stays read-only for 2 weeks (rollback path).
```

### 6. Decommission

- After the rollback window: `DROP` warehouse tables with owner
  confirmation (blast radius = all remaining consumers).
- Keep warehouse access logs/audit trail per compliance.

## Validation

- Per table: counts + checksums match source at cutover.
- Wave gates: every table in a wave passes before the next starts.
- Consumer verification: dashboards/reports unchanged after switch.

## Definition of Done

- Inventory + triage documented; waves planned with owners.
- All tables migrated; validations pass; cutover complete.
- Rollback path closed (read-only period elapsed) and decommission done.

## Reference Directory

- [Validation Recipes](references/validation.md): the checks that prove
  parity.
- [Cutover Checklist](references/cutover-checklist.md): the day-of script.

## Related Skills

- [Iceberg Basics](../../storage/iceberg-basics/SKILL.md) /
  [Delta Lake Basics](../../storage/delta-lake-basics/SKILL.md): the
  targets.
- [Object Storage Basics](../../storage/object-storage-basics/SKILL.md):
  the foundation.
- [Data Platform Architecture](../data-platform-architecture/SKILL.md):
  the destination blueprint.