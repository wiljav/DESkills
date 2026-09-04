---
name: mysql-basics
metadata:
  category: Databases
description: >-
  Configures and tunes MySQL for data-platform use: engines, indexing,
  partitioning, binary-log replication, and CDC integration. Use when
  running MySQL as a source or operational store. Don't use for Postgres
  specifics (use postgres-basics) or warehouse design (warehousing skills).
allowed-tools:
  - mysql
  - python
---

# MySQL Basics

MySQL powers much of the web's transactional data. For data platforms it
is usually a CDC source or a small operational store — this skill covers
running it reliably and extracting from it.

## Prerequisites

- A running MySQL instance (local, RDS/Aurora, or GCP Cloud SQL).
- `mysql` client; `mysqldump` for backups.
- Credentials with scoped grants per the auth skill.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `SELECT`, `EXPLAIN`, `SHOW ENGINE`, information
  schema queries.
- **Tier M (mutation)**: DDL/DML writes, index creation, partition
  changes, and binary-log (`binlog`) configuration changes. Binlog
  settings need a restart — confirm with the instance owner.

## Workflow

### 1. Inspect the Instance

```bash
mysql -h {host} -u {user} -p -e "SHOW DATABASES; SHOW TABLE STATUS FROM {db};"
mysql -h {host} -u {user} -p -e "SHOW VARIABLES LIKE 'binlog%';"
```

### 2. Create Users and Grants

```sql
CREATE USER 'de_readonly'@'%' IDENTIFIED BY '{pwd}';
GRANT SELECT ON analytics.* TO 'de_readonly'@'%';
GRANT REPLICATION CLIENT, REPLICATION SLAVE ON *.* TO 'de_readonly'@'%';
FLUSH PRIVILEGES;
```

Rules:

- Extraction users: `SELECT` + replication privileges only.
- Host-scope users (`@'%'` vs `@'10.0.0.0/8'`) — prefer the narrowest.

### 3. Choose Engines and Indexes

```sql
CREATE TABLE orders (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id VARCHAR(64),
  amount DECIMAL(12,2),
  created_at DATETIME,
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB;
```

Rules:

- InnoDB is the default; only use MyISAM with explicit justification
  (legacy).
- Composite indexes follow leftmost-prefix like Postgres; `EXPLAIN` to
  verify (`key` column shows the used index).

### 4. Partition or Shard Large Tables

```sql
ALTER TABLE events PARTITION BY RANGE (TO_DAYS(created_at)) (
  PARTITION p_2024_01 VALUES LESS THAN (TO_DAYS('2024-02-01')),
  PARTITION p_2024_02 VALUES LESS THAN (TO_DAYS('2024-03-01'))
);
```

- Partition for retention-friendly archiving (DROP PARTITION is instant).
- Beyond single-node scale: shard by key or move analytics to the
  warehouse (this skill is about correctness, not infinite scaling).

### 5. Enable CDC via Binlog

```bash
# server config (restart required)
binlog_format=ROW
server_id=1
gtid_mode=ON
enforce_gtid_consistency=ON
```

Rules:

- `binlog_format=ROW` is REQUIRED for Debezium CDC (statement format
  misses before-images).
- GTID mode makes consumer offsets robust across restarts.
- Debezium MySQL connector reads the binlog position; keep the binlog
  retention long enough for consumer lag.

### 6. Back Up

```bash
mysqldump -h {host} -u {user} -p analytics --single-transaction > analytics.sql
```

- `--single-transaction` for consistent InnoDB dumps; test restores
  quarterly.

## Validation

- `EXPLAIN` shows index use on hot queries.
- Binlog in ROW+GTID mode (verified with `SHOW VARIABLES`).
- CDC events flowing with lag within SLA.
- Restore test passes from the latest dump.

## Definition of Done

- Scoped users created; no root in pipeline code.
- Indexes/partitions applied and verified with EXPLAIN.
- Binlog ROW+GTID enabled for CDC; lag monitored.
- Backup + quarterly restore test in place.

## Reference Directory

- [Engines & Indexing](references/engines-indexing.md): InnoDB notes and
  EXPLAIN reading.
- [Binlog CDC](references/binlog-cdc.md): ROW format details and Debezium
  wiring.

## Related Skills

- [Kafka Connect](../../ingestion/kafka-connect/SKILL.md): Debezium
  connector consumption.
- [PostgreSQL Basics](../postgres-basics/SKILL.md): the sibling engine.
- [dbt Core](../../transformation/dbt-core/SKILL.md): analytics on
  MySQL/analytics warehouses.
