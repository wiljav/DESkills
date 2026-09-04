# Ingestion Recipes

## Common sources

| Source | Recipe type | Notes |
| --- | --- | --- |
| Snowflake | `snowflake` | database-level scoping via `database` |
| BigQuery | `bigquery` | `project_id` + `database` |
| Redshift | `redshift` | IAM role or user auth |
| Kafka | `kafka` | schema registry topics |
| Airflow | `datahub-airflow` plugin | DAG-level lineage, enabled in airflow.cfg |
| dbt | `datahub` via `acryl-datahub[dbt]` | `dbt` source type |

## dbt recipe

```yaml
source:
  type: dbt
  config:
    manifest_path: target/manifest.json
    catalog_path: target/catalog.json
    run_results_path: target/run_results.json
    load_schema: true
sink:
  type: datahub-rest
  config:
    server: "http://datahub-gms:8080"
    token: ${DATAHUB_TOKEN}
```

## Scheduling rules

- Core sources: daily at minimum (post-pipeline completion).
- dbt: after each successful `dbt run` + `dbt test` (manifest+results).
- Airflow: via the plugin, per DAG run.
- Secrets: env vars, secret manager, or the CI secrets store.

## Failure handling

- Ingestion failure = ticket + alert; never let a week of failures pass.
- Idempotent by design: re-running a recipe updates, not duplicates.
