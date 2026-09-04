---
name: flink-sql
metadata:
  category: Streaming
description: >-
  Authors streaming pipelines with Flink SQL and change-data-capture
  sources: catalogs, tables, windows, and exactly-once sinks. Use when
  stream processing is expressible in SQL. Don't use for complex stateful
  logic (use flink-basics DataStream API) or for batch SQL (use duckdb or
  warehouse SQL).
allowed-tools:
  - flink
  - sql-client
  - python
---

# Flink SQL

Flink SQL brings the table abstraction to streams: Kafka topics become
tables, windows become SQL clauses, and sinks are declarative.

## Prerequisites

- A Flink cluster with the SQL client (`sql-client`) or SQL gateway.
- Kafka cluster with the topics to process (see kafka-basics).
- Destination sink access (warehouse, object storage, Kafka).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `SHOW TABLES`, `DESCRIBE`, `EXPLAIN PLAN FOR`,
  running statements with `--mode read-only` where supported, previewing
  results.
- **Tier M (mutation)**: `CREATE TABLE`/`CREATE CATALOG`, `INSERT INTO`
  statements (executing queries writes to sinks), and checkpoint config.
  Confirm before any statement that writes.

## Workflow

### 1. Configure the Session

```sql
SET 'execution.checkpointing.interval' = '60s';
SET 'execution.checkpointing.mode' = 'EXACTLY_ONCE';
SET 'sql-client.execution.result-mode' = 'tableau';
```

### 2. Declare the Source

```sql
CREATE TABLE kafka_events (
    event_id   STRING,
    customer_id STRING,
    amount     DECIMAL(12,2),
    event_time TIMESTAMP(3),
    WATERMARK FOR event_time AS event_time - INTERVAL '5' SECONDS
) WITH (
    'connector' = 'kafka',
    'topic' = 'events',
    'properties.bootstrap.servers' = '{broker}',
    'properties.group.id' = 'flink-sql',
    'scan.startup.mode' = 'latest-offset',
    'format' = 'json'
);
```

Rules:

- Watermarks MUST be declared for event-time windows.
- `scan.startup.mode`: `earliest-offset` for replayable processing,
  `latest-offset` for fresh-only.
- Types MUST match the topic's schema registry (or the JSON schema).

### 3. Declare the Sink

```sql
CREATE TABLE sink_agg (
    customer_id STRING,
    window_end  TIMESTAMP(3),
    total       DECIMAL(14,2),
    PRIMARY KEY (customer_id, window_end) NOT ENFORCED
) WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:postgresql://{host}:5432/{db}',
    'table-name' = 'agg_orders'
);
```

- `PRIMARY KEY ... NOT ENFORCED` declares the upsert key for sink connectors
  that support it.
- For lakehouse sinks (Iceberg/Delta) use their connectors with
  `'sink.upsert-materialize'` as needed.

### 4. Write the Transformation

```sql
INSERT INTO sink_agg
SELECT
    customer_id,
    TUMBLE_END(event_time, INTERVAL '1' HOUR) AS window_end,
    SUM(amount) AS total
FROM kafka_events
GROUP BY TUMBLE(event_time, INTERVAL '1' HOUR), customer_id;
```

- Tumbling/sliding/session windows via the SQL clauses.
- `EXPLAIN PLAN FOR INSERT INTO ...` to review the plan BEFORE executing.

### 5. Run and Monitor

```bash
sql-client -f transform.sql
```

Monitor:

- Checkpoints completing (see flink-basics checkpointing).
- Backpressure in the UI.
- Sink counts vs source counts (exactly-once verification).

### 6. Handle CDC Sources

Debezium topics (from kafka-connect) with the `debezium-json` format:

```sql
CREATE TABLE cdc_orders (
    id INT, amount DECIMAL(12,2),
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'kafka',
    'topic' = 'db.orders.orders',
    'format' = 'debezium-json',
    'scan.startup.mode' = 'earliest-offset'
);
```

CDC tables are upsert streams: downstream processing MUST be idempotent and
aware of tombstone (delete) events.

## Validation

- `EXPLAIN` plan shows the expected windowing and join strategy.
- A bounded test (replay a small topic range) produces correct counts.
- Checkpoints complete; exactly-once sink verified (reprocessed input does
  not duplicate).
- Backpressure in normal range.

## Definition of Done

- Sources/sinks declared with correct formats, watermarks, and startup
  modes.
- Transformation written in SQL; plan reviewed.
- Statement executed with confirmation; counts verified.
- CDC handling explicit where Debezium sources are used.

## Reference Directory

- [Time & Window Functions](references/windows.md): TUMBLE/HOP/SESSION and
  watermark tuning.
- [Joins in Flink SQL](references/joins.md): interval joins, temporal
  joins, and lookup joins.

## Related Skills

- [Flink Basics](../../processing/flink-basics/SKILL.md): the runtime and
  checkpoint model underneath.
- [Kafka Connect](../../ingestion/kafka-connect/SKILL.md): producing the
  topics consumed here.
- [Streaming Architecture Patterns](../streaming-architecture-patterns/SKILL.md):
  where Flink SQL fits.
