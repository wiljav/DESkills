---
name: flink-basics
metadata:
  category: DataProcessing
description: >-
  Builds streaming and batch jobs with Apache Flink DataStream and Table
  APIs, including sources, sinks, state, and checkpointing. Use when
  building stateful stream processing or unified batch/streaming pipelines.
  Don't use for one-off batch SQL (use duckdb/spark) or for SQL-only
  streaming (use flink-sql).
allowed-tools:
  - flink
  - python
  - java
---

# Apache Flink Basics

Apache Flink is a stateful stream processor with exactly-once semantics and a
unified batch/streaming model. This skill covers the foundation: job
structure, sources/sinks, state, and checkpointing.

## Prerequisites

- Flink cluster (local `flink` CLI, Kubernetes, managed Flink) or a
  session/application mode environment.
- A running Kafka/event stream for streaming sources (or bounded sources for
  batch-mode jobs).
- Credentials per `data-engineering-auth` for cloud sinks.
- Java 11+ for the JVM runtime.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `flink list`, `flink info` on a JAR, inspecting
  checkpoints, reading job logs and metrics.
- **Tier M (mutation)**: submitting/cancelling jobs, creating or altering
  topics, and state-heavy operations (savepoints, rescaling). All MUST be
  confirmed; cancelling a job with uncheckpointed state can lose data.

## Workflow

### 1. Define the Job Structure

DataStream API (Python example):

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common import WatermarkStrategy

env = StreamExecutionEnvironment.get_execution_environment()
env.enable_checkpointing(60000)

source = KafkaSource.builder() \
    .set_bootstrap_servers("localhost:9092") \
    .set_topics("events") \
    .set_group_id("de-pipeline") \
    .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
    .build()

ds = env.from_source(source, WatermarkStrategy.no_watermarks(), "kafka-events")
```

### 2. Choose Sources and Sinks

| Source/Sink | When |
| --- | --- |
| Kafka | default streaming source/sink |
| Kinesis / Pub/Sub | cloud-native streams |
| File source/sink | batch-mode bounded jobs |
| JDBC / warehouse connectors | serving results to analytics |

Sinks MUST be transactional where the connector supports it (Kafka sink with
`exactly-once`, warehouse connectors with staged commits) so downstream never
sees partial results.

### 3. Manage State Correctly

State is the heart of Flink: window aggregations, keyed state, and
checkpointed operators.

```python
from pyflink.datastream.functions import KeyedProcessFunction

class WindowCounter(KeyedProcessFunction):
    def process_element(self, value, ctx):
        # keyed state kept per key, checkpointed
        ...
```

Rules:

- Keep state in Flink-managed keyed state (`ValueState`, `ListState`, etc.) —
  never in static variables.
- Prefer SQL/Table API windows for standard aggregations (tumbling, sliding,
  session) over hand-rolled timers.
- State size must be monitored; unbounded key growth is the top production
  killer.

### 4. Configure Checkpointing

```python
env.enable_checkpointing(60_000)  # interval in ms
env.get_checkpoint_config().set_min_pause_between_checkpoints(30_000)
env.get_checkpoint_config().set_max_concurrent_checkpoints(1)
```

Rules:

- Checkpoint interval << event-time window so restarts recover quickly.
- Exactly-once requires `set_externalized_checkpoints` + transactional sinks.
- Store checkpoints in durable storage (S3/GCS/HDFS), never local disk.

### 5. Submit and Monitor

```bash
flink run -d -p 4 -c {MainClass} target/job.jar
flink list
flink checkpoint list {job_id}          # verify checkpoints completing
flink cancel -s s3a://bucket/savepoints/ {job_id}   # graceful stop w/ savepoint
```

## Validation

- Job reaches RUNNING; checkpoints complete without failure.
- Test run over a bounded sample produces expected counts and window results.
- Sink output matches source volume after reprocessing (exactly-once
  verified by idempotent sink or count comparison).
- Backpressure metrics are in normal range (see reference).

## Definition of Done

- Job structured with proper sources/sinks and managed state.
- Checkpointing enabled, durable, and completing.
- Test on bounded data succeeded; counts verified.
- Job submitted to the cluster (confirmed) and monitored through the first
  checkpoint.
- No credentials in code; config via environment/cluster secrets.

## Reference Directory

- [Core Concepts](references/core-concepts.md): time semantics, watermarks,
  windows, and state.
- [Checkpointing & Recovery](references/checkpointing.md): exactly-once,
  savepoints, and rescaling.

## Related Skills

- [Flink SQL](../../streaming/flink-sql/SKILL.md): SQL-first streaming when
  the DataStream API is overkill.
- [Spark Basics](../spark-basics/SKILL.md): batch-oriented alternative.
- [Streaming Architecture Patterns](../../streaming/streaming-architecture-patterns/SKILL.md):
  where Flink fits in the platform.