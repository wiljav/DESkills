---
name: streaming-analytics-pipeline
metadata:
  category: Solutions
description: >-
  Builds an end-to-end streaming pipeline with CDC, processing, and
  serving: Kafka, Flink/Kafka Streams, sinks, and freshness SLAs. Use when
  assembling a real-time pipeline. Don't use for batch pipelines (use
  batch-etl-pipeline) or single components (use the domain skills).
allowed-tools:
  - python
  - sql
  - bash
---

# Streaming Analytics Pipeline

The reference recipe for streaming: source events -> Kafka -> stream
processing -> serving layer, with exactly-once semantics and latency SLAs.
Assembly skill composing the streaming domain skills.

## Prerequisites

- Domain skills: kafka-basics, flink-sql or kafka-streams,
  streaming-architecture-patterns.
- A running Kafka cluster and a processing environment (Flink/K8s).
- The latency SLA and the serving target (warehouse, API, feature store).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: reading topics, job status, consumer lag.
- **Tier M (mutation)**: creating topics, deploying jobs, changing
  partitioning/keys, and backfilling. Deployments alter live processing —
  confirm with the streaming platform owner.

## Workflow

### 1. Design the Topology

```text
sources (CDC, events, telemetry)
  -> Kafka topics (raw)
  -> stream processing: Flink SQL / Kafka Streams (enrich, window, join)
  -> sinks: warehouse (Iceberg/Delta), feature store, API
  -> observability: lag, watermark age, failure rate
```

Rules:

- Kafka = the backbone: raw topics append-only; processed topics derived.
- Partition keys choose ordering semantics — decide per topic
  (kafka-basics).
- Latency budget: source-to-topic < SLA/3, processing < SLA/3, sink <
  SLA/3.

### 2. Create Topics with Purpose

```bash
kafka-topics --create --topic raw.orders \
  --partitions 12 --replication-factor 3 --config retention.ms=604800000
```

- Raw topics: partition by natural key (order_id) for order-scoped
  ordering.
- Derived topics (`processed.orders`): partition by serving key.
- Retention >= consumer lag headroom + reprocessing needs.

### 3. Process with Flink SQL

```sql
CREATE TABLE raw_orders (
  order_id STRING, customer_id STRING, amount DECIMAL(12,2),
  event_ts TIMESTAMP(3), WATERMARK FOR event_ts AS event_ts - INTERVAL '5' SECONDS
) WITH ('connector' = 'kafka', 'topic' = 'raw.orders', ...);

CREATE TABLE processed_orders (
  order_id STRING, customer_id STRING, amount DECIMAL(12,2),
  event_ts TIMESTAMP(3), PRIMARY KEY (order_id) NOT ENFORCED
) WITH ('connector' = 'upsert-kafka', ...);

INSERT INTO processed_orders
SELECT order_id, customer_id, amount, event_ts FROM raw_orders;
```

Rules:

- Watermarks define event-time completeness — the latency/accuracy knob.
- Upsert-Kafka sink = compacted, exactly-once-visible processed topic.
- Checkpointing ON with `EXACTLY_ONCE` (processing guarantees).

### 4. Sink to Serving

```sql
-- Iceberg sink
CREATE TABLE serving.orders_iceberg (
  order_id STRING, ...,
  event_ts TIMESTAMP(3), PRIMARY KEY (order_id) NOT ENFORCED
) WITH ('connector' = 'iceberg', 'catalog' = 'rest', 'table' = 'curated.orders');

INSERT INTO serving.orders_iceberg SELECT * FROM processed_orders;
```

Rules:

- Warehouse sinks: Iceberg/Delta with upsert semantics (see
  iceberg-basics).
- Feature/API sinks: compacted topics + consumers.
- Never let the sink lag unbounded: alert at 2x SLA.

### 5. Backfill and Recovery

- Backfill: replay from the topic (consumer offsets reset) or re-run the
  job from a Kafka snapshot.
- Recovery: Flink checkpoints + savepoints; redeploy from the last
  checkpoint.
- CDC pipelines: on topic reset, re-snapshot the source
  (kafka-connect).

### 6. Monitor the SLAs

| Metric | Tool | Alert |
| --- | --- | --- |
| Consumer lag | kafka lag exporters / Kafka UI | > SLA window |
| Watermark age | Flink metrics (`currentWatermark`) | > SLA/2 |
| Job restart rate | Flink JobManager metrics | > 0 in 24h |
| Sink freshness | warehouse table `max(event_ts)` | staleness > SLA |

## Validation

- End-to-end: event injected -> visible in serving within the SLA.
- Exactly-once: duplicate-source replay produces no duplicates in the
  sink (count check).
- Lag/watermark within budget under the expected load.

## Definition of Done

- Topology live: raw topics, processing job, sinks.
- Exactly-once semantics verified; SLA met in a load test.
- Observability dashboards live; backfill/recovery documented.

## Reference Directory

- [SLA Budgeting](references/sla-budgeting.md): splitting latency budgets.
- [Exactly-Once in Practice](references/exactly-once.md): the semantics
  stack.

## Related Skills

- [Kafka Basics](../../ingestion/kafka-basics/SKILL.md): the backbone.
- [Flink SQL](../../streaming/flink-sql/SKILL.md) and
  [Kafka Streams](../../streaming/kafka-streams/SKILL.md): the processing
  options.
- [Streaming Architecture Patterns](../../streaming/streaming-architecture-patterns/SKILL.md):
  which topology fits.
- [Iceberg Basics](../../storage/iceberg-basics/SKILL.md): the sink
  format.
