# Collector Setup

## Options

| Backend | Use when | Notes |
| --- | --- | --- |
| DataHub | org metadata hub exists | native OpenLineage API on the GMS endpoint |
| Marquez | standalone lineage store | reference implementation, Airflow integration |
| OpenLineage proxy | fleet already points elsewhere | forwards to Marquez/DataHub |

## Deployment notes

- Run the collector in the same VPC as pipelines (events are small HTTP
  POSTs).
- Persist events: default in-memory stores lose history on restart —
  configure the backend DB (Postgres for Marquez).
- Monitor: event count per hour vs pipeline run count (drops = emitter
  breakage).

## Fail-closed vs fail-open

- Pipelines should fail-open: lineage emitter errors must NOT fail the
  data job (wrap emitters in try/except or use the platform's built-in
  async emission).
- DataHub/Marquez downtime = missing lineage for that window; backfill by
  re-running the job (events re-emit) — document this expectation.
