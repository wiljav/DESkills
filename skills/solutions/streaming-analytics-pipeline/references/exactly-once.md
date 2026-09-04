# Exactly-Once in Practice

## The semantics stack

1. **Source**: Kafka consumer reads offsets; commits only after
   processing (Flink checkpoints manage this).
2. **State**: checkpointed (Flink) / store-backed (Kafka Streams).
3. **Sink**: transactional writes — two-phase commit for Kafka
   (flink kafka sink), IdempotentWriter for streams.

## Rules

- Enable checkpoints: `checkpointing.interval` (10-30s) + `EXACTLY_ONCE`
  mode (Flink) — the default in Kafka Streams.
- Idempotent sink writes (`enable.idempotence=true` in the producer) —
  never rely on at-least-once alone for money data.
- Compacted topics (`cleanup.policy=compact`) for keyed outputs: the
  last value per key wins — this makes duplicates converge.

## Verifying exactly-once

- Test: inject the same event twice; assert ONE row in the sink.
- Monitor: sink-side duplicates counter (Flink `numRecordsOut` vs sink
  row count).
- On restart: resume from checkpoint, not from scratch.

## Costs

- Exactly-once costs latency (transaction commit on each checkpoint).
- When the workload tolerates duplicates (telemetry aggregates), use
  at-least-once + dedup at aggregation — cheaper, same outcome.
