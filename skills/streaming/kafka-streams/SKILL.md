---
name: kafka-streams
metadata:
  category: Streaming
description: >-
  Builds stateful stream processing applications on Kafka Streams:
  topologies, KTables, state stores, and exactly-once processing. Use when
  processing should stay inside the Kafka ecosystem without a separate
  cluster. Don't use for SQL-only processing (use flink-sql) or for
  connector-driven integration (use kafka-connect).
allowed-tools:
  - java
  - gradle
  - docker
---

# Kafka Streams

Kafka Streams is a JVM library for stream processing on Kafka: your
application is a Kafka consumer/producer pair with stateful operators and
exactly-once semantics — no separate processing cluster.

## Prerequisites

- A Kafka cluster (see kafka-basics).
- JVM 11+; a Java build setup (Gradle/Maven) with the
  `kafka-streams` dependency.
- Topics designed per the topology (keying matters — see topic-design).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `kafka-streams-application-reset` with
  `--dry-run`, inspecting group/topic state, local runs against test topics.
- **Tier M (mutation)**: deploying the app to production, resetting
  application state, and writing to sink topics. Reset drops state stores —
  confirm with blast radius before running it.

## Workflow

### 1. Define the Topology

```java
StreamsBuilder builder = new StreamsBuilder();

KStream<String, Event> events = builder.stream(
    "events",
    Consumed.with(Serdes.String(), eventSerde));

events
    .filter((key, e) -> e.getStatus().equals("valid"))
    .groupByKey()
    .windowedBy(TimeWindows.of(Duration.ofHours(1)))
    .aggregate(
        () -> new Total(),
        (key, e, agg) -> agg.add(e.getAmount()),
        Materialized.with(Serdes.String(), totalSerde))
    .toStream()
    .map((wk, v) -> KeyValue.pair(wk.key(), v))
    .to("agg-events", Produced.with(Serdes.String(), totalSerde));
```

Rules:

- Keying drives grouping/state: rekey with `.selectKey()` only where
  necessary, and note the repartition topic it creates.
- Serdes MUST be registered for every custom type
  (JSON/Avro via the schema registry).

### 2. Configure the Application

```java
Properties props = new Properties();
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "events-aggregator");
props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "{broker}");
props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, jsonSerde.getClass());
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, "exactly_once_v2");
```

- `application.id` = the consumer group; must be unique per logical app.
- `exactly_once_v2` for end-to-end exactly-once (Kafka 3.3+).
- `state.dir` on durable local disk; state stores live here.

### 3. Run Locally

```bash
gradle run
```

Consume the sink topic and verify: input `events` (filtered) -> `agg-events`
counts per window are correct for a seeded test dataset.

### 4. Deploy

- Package a JAR; run with `java -jar` (one instance per partition-group, or
  let it auto-scale with `num.stream.threads`).
- Rebalance behavior: adding/removing instances redistributes partitions —
  test with 2 instances locally first.

### 5. Operate: Reset and Recovery

```bash
# dry-run first
kafka-streams-application-reset --application-id events-aggregator \
  --bootstrap-servers {broker} --dry-run

# real reset (CONFIRMED): clears offsets + state topics
kafka-streams-application-reset --application-id events-aggregator \
  --bootstrap-servers {broker} --input-topics events --to-earliest
```

Rules:

- Reset only after the app is stopped and the failure is fixed.
- Prefer replay (`--to-earliest`) over state reset when the input is
  re-available: reprocessing rebuilds state correctly.

## Validation

- Local run over seeded input produces correct aggregations.
- Two-instance run shares partitions without overlap (offsets balanced).
- Restart with replayed input yields identical state (exactly-once
  verified).
- `kafka-consumer-groups --describe` shows the app's group with bounded lag.

## Definition of Done

- Topology declared; serdes registered; keying intentional.
- Exactly-once guarantee configured and verified via replay test.
- Deployment confirmed; reset/recovery path documented and dry-run tested.
- Lag monitored and bounded.

## Reference Directory

- [State Stores & Windows](references/state.md): store types and
  windowed state.
- [Rebalancing & Recovery](references/rebalancing.md): what happens when
  instances join/leave, and safe recovery.

## Related Skills

- [Kafka Basics](../../ingestion/kafka-basics/SKILL.md): topics and
  partitioning this app depends on.
- [Flink SQL](../flink-sql/SKILL.md): SQL alternative when the topology is
  simple.
- [Streaming Architecture Patterns](../streaming-architecture-patterns/SKILL.md):
  architectural fit.
