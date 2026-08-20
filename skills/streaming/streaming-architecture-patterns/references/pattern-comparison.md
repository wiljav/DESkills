# Pattern Comparison

| Criterion | Event-driven | CDC | Kappa | Lambda |
| --- | --- | --- | --- | --- |
| Latency | ms-s | s | s-min | s-min (stream) |
| Complexity | low | medium | medium | high (two paths) |
| Replay | retention-bound | log replay | full replay | partial |
| Consistency | eventual | event-time | event-time | dual-write risk |
| Ops cost | low | medium | medium | high |

## Guidance

- **Event-driven**: default for service-to-service; pair with CDC when the
  source of truth is a database.
- **CDC**: the standard way to sync operational stores into the lakehouse;
  needs tombstone + schema handling (see kafka-connect Debezium notes).
- **Kappa**: choose when one engine (Flink/Dataflow) can serve both — the
  lakehouse tables are just the batch view of the replayed stream.
- **Lambda**: only when the batch path is already production-grade and the
  stream path is additive; actively plan the decommission of the batch path
  (that is the "kappa migration").

## Anti-patterns

- Streaming to serve ad-hoc BI (use batch).
- Exactly-once everywhere (cost without benefit).
- No retention planning (replay impossible when consumers fall behind).
- Per-service bespoke brokers (one managed broker platform).