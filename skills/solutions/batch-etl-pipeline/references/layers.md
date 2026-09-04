# Layer Design

## Medallion rules

| Layer | Content | Consumers | Ownership |
| --- | --- | --- | --- |
| bronze | raw, as-received, append/replace per partition | data engineers only | ingestion team |
| silver | cleaned, typed, deduped, conformed | analysts, data scientists, gold builders | transformation team |
| gold | semantic, aggregated, business-named | dashboards, apps, ML features | product/data team |

## Boundaries

- Contract at silver: consumers rely on its stability (data-contracts).
- Bronze stays append-friendly: reprocessing never rewrites history.
- Gold is presentation: name models by the question, not the source.

## When NOT to medallion

- Small/one-off datasets: single silver table is fine.
- Strict append streaming: bronze + serving, skip gold
  (streaming-analytics-pipeline).
- The pattern pays off at scale; don't gold-plate a 5-row reference
  table.
