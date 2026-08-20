# Event Model

## Core event

```json
{
  "eventType": "COMPLETE",
  "job": {
    "namespace": "de_prod",
    "name": "airflow.orders_daily"
  },
  "run": {
    "runId": "uuid",
    "facets": { "parent": { "run": { "runId": "dag_run_uuid" } } }
  },
  "inputs": [
    { "namespace": "kafka", "name": "orders_topic", "facets": {} }
  ],
  "outputs": [
    { "namespace": "s3", "name": "warehouse/curated/orders", "facets": {} }
  ]
}
```

## Facets

- Job facets: ownership, source code link.
- Run facets: parent runs (DAG -> task), SQL, arguments.
- Dataset facets: schema, data quality, column-level lineage.

## Lifecycle

| Event | Meaning |
| --- | --- |
| START | run began |
| RUNNING | heartbeat (spark/long jobs) |
| COMPLETE | finished successfully |
| FAIL | failed; consumers of its outputs were not updated |

## Rules

- Stable job identity is everything: the same DAG must always emit the
  same `job.name`.
- Column-level lineage requires integration support (dbt-ol emits it);
  file/table-level works everywhere.