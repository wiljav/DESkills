# Zone Design Details

## Zone policies matrix

| Zone | Owner | Access | Retention | Reprocessing |
| --- | --- | --- | --- | --- |
| landing | ingestion team | ingestion service + security | source-defined | n/a (immutable) |
| raw/bronze | ingestion team | data engineers | SLA + compliance | append/replace per partition |
| curated/silver | transformation team | analysts + data scientists | business retention | contract-backed overwrite |
| marts/gold | product teams | BI + apps | as contracted | derived, idempotent |

## Rules

- Data flows ONE direction (no writes from marts back into raw).
- Landing is the only zone that may delete by source policy; everything
  else is governed by the zone's retention contract.
- Cross-zone copies are jobs with owners — every hop appears in lineage
  (openlineage-basics).

## Security boundaries

- PII stays classified (pii-classification-and-masking): masking applied
  at the serving surface, raw PII restricted to named roles.
- Zones map to cloud IAM scopes (bucket prefixes / dataset ACLs) via
  terraform-for-data.

## Observability per zone

- Freshness: max event time per zone dataset vs wall clock.
- Volume: row counts day-over-day; anomalies alert
  (data-observability).
- Quality: gates at curated + marts boundaries.