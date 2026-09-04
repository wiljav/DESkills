# Checkpointing & Recovery

## Checkpoints vs savepoints

| | Checkpoints | Savepoints |
| --- | --- | --- |
| Trigger | automatic, periodic | manual |
| Purpose | crash recovery | upgrades, rescaling, maintenance |
| Lifecycle | deleted with job | retained by operator |
| Format | optimized | portable |

## Exactly-once

Exactly-once = checkpointing + transactional sink:

1. Checkpoints snapshot operator state atomically.
2. Transactional sinks (Kafka `exactly-once`, Iceberg staged commits) commit
   only when the checkpoint completes.
3. On restart, Flink resumes from the last completed checkpoint; the sink
   replays the uncommitted window.

Verify with a reprocessing test: feed the same bounded input twice, sink
count must equal input count, not double.

## Common failure signatures

| Symptom | Cause | Fix |
| --- | --- | --- |
| Checkpoint timeout | state too large / sink slow | increase interval, check sink throughput, inspect backpressure |
| `Checkpoint was declined` | operators busy | reduce load, rescale parallelism |
| Savepoint restore mismatch | state schema changed | align `uid()`s and state structure |
| Unbounded state growth | key cardinality grows | key design, TTL (`StateTtlConfig`) |

## Rules

- Assign `uid()`/`uidHash` to operators so savepoints restore correctly after
  code changes.
- Checkpoint storage MUST be durable (S3/GCS/HDFS).
- Cancel with `-s` (savepoint) for maintenance; killing a job without a
  savepoint loses the ability to resume state exactly.
