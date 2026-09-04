# Design Checklist

Use to audit any streaming design (new or existing).

## Requirements

- [ ] Latency target stated and justified.
- [ ] Throughput estimate (peak, sustained) with margin.
- [ ] Retention/replay window defined.
- [ ] Consumers and their semantics identified.

## Architecture

- [ ] Pattern chosen with documented trade-offs.
- [ ] Broker platform single and managed (or justified otherwise).
- [ ] Processing engine matches the team's skills and workload.
- [ ] Delivery semantics stated per pipeline.
- [ ] Idempotent sinks or dedup in place.

## Failure handling

- [ ] Broker outage recovery documented (reconnect + replay).
- [ ] Processing resume path (checkpoints/savepoints/state replay).
- [ ] Dead-letter policy for every sink.
- [ ] Schema registry + drift gate in place.

## Operations

- [ ] Producer/consumer lag metrics defined and alarmed.
- [ ] Watermark/latency metrics for event-time engines.
- [ ] Cost model (broker throughput, processing units) estimated.
- [ ] Runbook entry exists for the streaming platform.
