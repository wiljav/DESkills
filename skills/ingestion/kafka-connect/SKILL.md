---
name: kafka-connect
metadata:
  category: DataIngestion
description: >-
  Stands up and operates Kafka Connect connectors to move data between
  Kafka and storage, databases, and cloud services: connector configs,
  worker tuning, and failure recovery. Use when moving data in or out of
  Kafka with connectors. Don't use for building custom stream processing
  (use kafka-streams) or one-off file loads (use file-ingestion-gcs-s3).
allowed-tools:
  - connect-distributed
  - curl
  - docker
---

# Kafka Connect

Kafka Connect is the integration layer for Kafka: distributed workers run
source/sink connectors (JDBC, S3/GCS, BigQuery, Elasticsearch, etc.) with
exactly-once semantics for supported connectors.

## Prerequisites

- A Kafka cluster (see kafka-basics).
- Connect worker(s) configured — locally via Docker Compose or managed
  (Confluent Cloud connectors, MSK Connect).
- Connector plugin JARs installed on the workers (e.g. JDBC, S3 sink).
- REST API reachable (`http://localhost:8083` typical).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `GET /connectors`, `GET /connectors/{name}/status`,
  `GET /connectors/{name}/config`, reading worker logs.
- **Tier M (mutation)**: creating/pausing/deleting connectors, altering
  connector configs, and restarting tasks. Deleting a connector does not
  delete data but may orphan state; scaling tasks changes resource usage —
  confirm all.

## Workflow

### 1. Verify the Cluster and Plugins

```bash
curl -s localhost:8083/connectors | jq .
curl -s localhost:8083/connector-plugins | jq '.[].class'
```

Confirm the needed plugin classes are present before designing connectors.

### 2. Design the Connector Config

Source connector example (JDBC -> topic):

```json
{
  "name": "jdbc-orders-source",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "connection.url": "jdbc:postgresql://{host}:5432/{db}",
    "connection.user": "${file:/etc/connect/secrets:user}",
    "topic.prefix": "db.orders.",
    "mode": "incrementing",
    "incrementing.column.name": "id",
    "tasks.max": "4"
  }
}
```

Sink connector example (topic -> S3):

```json
{
  "name": "s3-events-sink",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "topics": "events",
    "s3.bucket.name": "{bucket}",
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "flush.size": "100000",
    "rotate.interval.ms": "600000"
  }
}
```

Rules:

- Secrets via externalized config providers (`${file:...}`), never inline.
- `tasks.max` sized by topic partitions for sinks, by source table
  cardinality for sources.
- Source modes: `incrementing` (append-only), `timestamp+incrementing`
  (updates + appends), `bulk` (small tables).

### 3. Deploy and Validate

```bash
curl -s -X POST localhost:8083/connectors -H "Content-Type: application/json" -d @connector.json
curl -s localhost:8083/connectors/jdbc-orders-source/status | jq
```

Check: connector state `RUNNING`, tasks assigned, no task failures.

### 4. Verify Data Flow

- Source: `kafka-console-consumer --topic db.orders.orders --from-beginning
  --max-messages 5` (see kafka-basics) — rows appear with the expected keys.
- Sink: check the sink location for objects, and compare object counts to
  topic offsets (lag = 0 via `kafka-consumer-groups`).

### 5. Handle Failures

Symptom: task state `FAILED`.

Diagnosis:

```bash
curl -s localhost:8083/connectors/{name}/tasks | jq .
curl -s localhost:8083/connectors/{name}/tasks/0/status | jq '.trace'
```

Common causes: schema drift in the source table, permissions, dead
brokers. Fix the cause, then restart the task:

```bash
curl -s -X POST localhost:8083/connectors/{name}/tasks/0/restart
```

## Validation

- Connector state RUNNING with all tasks assigned.
- Data flows end to end (probe consume + sink object check).
- Consumer lag for sink connectors = 0.
- No secrets in connector configs (grep the config endpoint output).

## Definition of Done

- Connector designed with correct mode/format/flush settings.
- Deployed and RUNNING; tasks healthy.
- End-to-end data flow verified.
- Failure handling understood; task restart path documented.
- Secrets externalized via config providers.

## Reference Directory

- [Connector Catalogue](references/connector-catalogue.md): common source/
  sink connectors and their config essentials.
- [Worker & Task Tuning](references/worker-tuning.md): offsets, memory,
  and exactly-once settings.

## Related Skills

- [Kafka Basics](../kafka-basics/SKILL.md): the cluster underneath.
- [File Ingestion (GCS/S3)](../file-ingestion-gcs-s3/SKILL.md): batch
  alternative to streaming sinks.
- [Streaming Architecture Patterns](../../streaming/streaming-architecture-patterns/SKILL.md):
  pipeline design with Connect.
