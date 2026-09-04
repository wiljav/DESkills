---
name: snowflake-basics
metadata:
  category: Warehousing
description: >-
  Configures warehouses, databases, stages, and query patterns in
  Snowflake: virtual warehouses, roles, and loading data. Use when setting
  up or operating Snowflake for pipelines. Don't use for cross-engine
  tuning (use warehouse-optimization) or alternative warehouses (use
  bigquery-basics or redshift-basics).
allowed-tools:
  - snowsql
  - python
---

# Snowflake Basics

Snowflake separates compute (virtual warehouses) from storage, bills per
warehouse second, and provides a rich SQL surface for analytics.

## Prerequisites

- A Snowflake account with a role scoped to the work (per auth skill).
- `snowsql` installed and configured
  (`~/.snowsql/config` with account/user/role; password via env or keypair).
- The target database/schema created or the right to create it.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `SHOW WAREHOUSES/DATABASES`, `DESCRIBE TABLE`,
  `SELECT`, `EXPLAIN` (Snowflake uses `EXPLAIN USING TEXT`).
- **Tier M (mutation)**: DDL/DML writes, warehouse create/alter
  (billing implications), stage creation, and `COPY INTO`. Creating or
  resizing warehouses changes spend — confirm sizes with the user.

## Workflow

### 1. Inspect the Environment

```sql
SHOW WAREHOUSES;
SHOW DATABASES;
SHOW ROLES;
SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE();
```

### 2. Set Up Databases and Warehouses

```sql
CREATE DATABASE IF NOT EXISTS analytics;
CREATE WAREHOUSE IF NOT EXISTS de_wh
  WITH WAREHOUSE_SIZE = 'X-SMALL'
       AUTO_SUSPEND = 60
       AUTO_RESUME = TRUE;
```

Rules:

- Separate warehouses by workload class (ingest vs analytics vs BI) so
  heavy queries don't starve each other.
- `AUTO_SUSPEND` (60s typical) + `AUTO_RESUME` control idle cost — the
  default cost lever.
- Start small (X-SMALL); scale only with measured need (see
  warehouse-optimization).

### 3. Manage Roles and Access

```sql
CREATE ROLE IF NOT EXISTS de_engineer;
GRANT USAGE ON WAREHOUSE de_wh TO ROLE de_engineer;
GRANT USAGE ON DATABASE analytics TO ROLE de_engineer;
GRANT ALL ON SCHEMA analytics.public TO ROLE de_engineer;
GRANT ROLE de_engineer TO USER {user};
```

Rules:

- Grant at the schema level for pipelines; database level only for admins.
- Never use `ACCOUNTADMIN` in pipeline code — scoped roles only.

### 4. Load Data via Stages

```sql
CREATE STAGE IF NOT EXISTS analytics.public.s3_stage
  URL = 's3://{bucket}/orders/'
  STORAGE_INTEGRATION = {integration};   -- or credentials via integration

COPY INTO analytics.public.orders
FROM @s3_stage
FILE_FORMAT = (TYPE = PARQUET)
ON_ERROR = 'CONTINUE';
```

Rules:

- Prefer `STORAGE INTEGRATION` (or keypair auth) over inline credentials.
- `COPY INTO` is atomic per statement and idempotent by default (loaded
  files tracked) — the natural load primitive.
- `ON_ERROR` policy: `SKIP_FILE` to quarantine, never silent `CONTINUE`
  without a file-count reconciliation.

### 5. Query with Warehouse Awareness

```sql
ALTER WAREHOUSE de_wh SET WAREHOUSE_SIZE = 'SMALL';  -- confirmed, measured need

SELECT customer_id, SUM(amount) AS total
FROM analytics.public.orders
WHERE event_date >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY customer_id;
```

- Use `warehouse = de_wh` in sessions; monitor `QUERY_HISTORY` for
  warehouse contention and scanned bytes.

## Validation

- `SHOW` commands return the intended objects; role has only the granted
  privileges.
- `COPY INTO` loaded the expected row count (query the table + compare to
  stage manifest).
- `QUERY_HISTORY` shows no failed jobs; warehouse auto-suspends when idle.
- Dry-run/EXPLAIN used before expensive ad-hoc queries.

## Definition of Done

- Databases/warehouses/roles created with documented sizing and access.
- Loads via stages + COPY INTO with error policy; counts verified.
- Queries scoped; warehouse cost levers (auto-suspend/resume) confirmed.
- No credentials in SQL/config; integrations or keypairs used.

## Reference Directory

- [Warehouse Sizing](references/warehouse-sizing.md): credits, scaling
  mechanics, and multi-clustering.
- [Data Loading](references/loading.md): stages, COPY variants, and
  semi-structured handling.

## Related Skills

- [Warehouse Optimization](../warehouse-optimization/SKILL.md): tuning
  queries and warehouses.
- [BigQuery Basics](../bigquery-basics/SKILL.md): the alternative warehouse.
- [dbt Core](../../transformation/dbt-core/SKILL.md): transformations on
  Snowflake.
