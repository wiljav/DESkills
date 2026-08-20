---
name: kafka-basics
metadata:
  category: DataIngestion
description: >-
  Creates topics, produces and consumes messages, and sizes Apache Kafka
  clusters for data pipelines: topic design, partitioning, retention, and
  consumer groups. Use when standing up or operating a Kafka cluster for
  ingestion. Don't use for building connectors (use kafka-connect) or
  stream processing (use kafka-streams or flink).
allowed-tools:
  - kafka-topics
  - kafka-console-producer
  - kafka-console-consumer
  - docker
---

# Apache Kafka Basics

Kafka is the backbone of event-driven data platforms. This skill covers the
foundations: brokers, topics, partitions, producers, consumers, and the
cluster settings that keep pipelines healthy.

## Prerequisites

- A running Kafka cluster (local `docker-compose` Kafka, managed Kafka like
  Confluent/MSK/Aiven, or Kraft-mode single broker).
- `kafka-topics`, `kafka-console-producer`, `kafka-console-consumer` CLIs
  available.
- Understanding of what events flow through this cluster (topics and
  consumers to be designed).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `kafka-topics --describe`, `kafka-consumer-groups
  --describe`, listing topics/brokers, `kafka-console-consumer --from-beginning
  --max-messages N`.
- **Tier M (mutation)**: creating/altering topics (partitions, retention),
  deleting topics, changing broker configs, and producing test data. Deleting
  a topic destroys data irrecoverably — MUST be confirmed with the blast
  radius stated.

## Workflow

### 1. Inventory the Cluster

```bash
kafka-topics --bootstrap-server {broker} --list
kafka-topics --bootstrap-server {broker} --describe
kafka-broker-api-versions --bootstrap-server {broker} | head
```

Record: broker count, topics, partitions, replication factor, and retention.

### 2. Design and Create Topics

Topic design rules:

- **Partitions**: parallelism + ordering unit. Rule of thumb: `max(3,
  consumers-in-group)`; scale for throughput: target ~10 MB/s per partition
  on modern hardware.
- **Replication factor**: 3 for production, 2 for dev; never 1 for
  irreplaceable data.
- **Retention**: `retention.ms` per data value; compacted topics
  (`cleanup.policy=compact`) for keyed state.

```bash
kafka-topics --bootstrap-server {broker} \
  --create --topic events \
  --partitions 12 --replication-factor 3 \
  --config retention.ms=604800000 \
  --config min.insync.replicas=2
```

### 3. Produce and Consume for Verification

```bash
kafka-console-producer --bootstrap-server {broker} --topic events \
  --property parse.key=true --property key.separator=:

kafka-console-consumer --bootstrap-server {broker} --topic events \
  --group probe-group --from-beginning --max-messages 10
```

Verify: messages round-trip, keys partition consistently
(`--property print.partition=true`).

### 4. Configure Consumer Groups

```bash
kafka-consumer-groups --bootstrap-server {broker} --group {group} --describe
```

Rules:

- One consumer group per logical consumer (pipeline/team), not per
  instance.
- Partition count >= group size, else idle consumers.
- Set explicit `auto.offset.reset` per consumer intent: `earliest` for
  replayable pipelines, `latest` for fire-and-forget. Never leave it
  implicit for new groups.

### 5. Monitor Health

```bash
kafka-consumer-groups --bootstrap-server {broker} --group {group} --describe
kafka-log-dirs --bootstrap-server {broker} --topic-list events
```

Watch: consumer lag (persistent growth = consumer falling behind), under-
replicated partitions (`kafka-topics --describe` shows `Isr` < `ReplicationFactor`),
and leader imbalance.

## Validation

- Topic describes correctly: expected partitions, RF, retention.
- Round-trip produce/consume verified with keys and partitions.
- Consumer group lag is zero (or bounded and declining) after the test.
- Under-replicated partitions = 0.

## Definition of Done

- Topics created per the design rules (partitions, RF, retention).
- Producer/consumer round-trip verified.
- Consumer groups configured with explicit reset policy.
- Health metrics recorded (lag, ISR); no under-replicated partitions.
- No test data left behind unless explicitly requested.

## Reference Directory

- [Topic Design](references/topic-design.md): partitioning math, keying,
  and compaction.
- [Cluster Health Signals](references/health-signals.md): lag, ISR, and
  broker metrics with diagnosis.

## Related Skills

- [Kafka Connect](../kafka-connect/SKILL.md): moving data in/out of this
  cluster.
- [Kafka Streams](../../streaming/kafka-streams/SKILL.md): processing the
  topics.
- [Streaming Architecture Patterns](../../streaming/streaming-architecture-patterns/SKILL.md):
  where Kafka sits in the platform.