# Connector Catalogue

| Connector | Type | Essentials |
| --- | --- | --- |
| JDBC source | source | `mode`, `incrementing.column.name`, `poll.interval.ms` |
| Debezium (CDC) | source | `database.history.kafka.topic`, `transforms` for schema cleanup |
| S3 / GCS sink | sink | `format.class`, `flush.size`, `rotate.interval.ms`, `partitioner.class` |
| BigQuery sink | sink | `project`, `dataset`, `topic` mapping, `upsert` mode |
| Elasticsearch sink | sink | `topics`, `key.ignore` |
| HTTP source | source | `http.url`, `poll.interval.ms` |

## Debezium CDC notes

- One connector per table (or one per schema with table includes).
- `transforms=unwrap` flattens the envelope; prefer topic-per-table routing
  for warehouse loading.
- Tombstone events (deletes) MUST be handled downstream: BigQuery sinks map
  deletes via `delete.enabled=true`; S3 sinks drop tombstones by default.

## Config essentials checklist

- `errors.tolerance`: `all` for resilient pipelines (dead-letter instead of
  fail) — but `none` when ordering/accuracy matters.
- `errors.deadletterqueue.topic.name`: DLQ topic + `errors.deadletterqueue
  .context.headers.enable=true` for troubleshooting.
- `key.converter`/`value.converter`: `avro` with Schema Registry, or
  `json` for simple pipelines.
