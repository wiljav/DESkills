# SLA Budgeting

## The budget split

| Hop | Share | Example (SLA 60s) |
| --- | --- | --- |
| source -> topic | 1/3 | 20s |
| processing | 1/3 | 20s |
| sink + serving visibility | 1/3 | 20s |

## Measuring each hop

- source->topic: `kafka producer metrics` (record-send latency).
- processing: watermark age (`currentWatermark` vs event clock).
- sink: warehouse table `max(event_ts)` vs wall clock.

## Rules

- The budget is per-percentile: aim p95 within budget, p99 at 1.5x.
- Overruns: find the hop, not the job — measure before changing
  anything.
- Load test at 2x expected peak; SLAs must hold there.