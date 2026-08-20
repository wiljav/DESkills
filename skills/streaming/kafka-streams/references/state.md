# State Stores & Windows

## Store types

| Store | API | Use |
| --- | --- | --- |
| Key-value | `KeyValueStore` | lookup state, dedup, latest-value |
| Windowed | `WindowStore` | window aggregations, session state |
| Timestamped | `TimestampedKeyValueStore` | time-aware lookups (temporal joins) |

State is local (RocksDB default) and replicated via changelog topics
(`{app}-{store}-changelog`).

## RocksDB tuning

- Default config works for most; set `state.rocksdb.memory.monitoring` when
  memory is tight.
- Large state: watch changelog topic growth — it is the durability cost of
  state.

## Windowed state

- `TimeWindows.of(duration)` — tumbling; `SessionWindows` — activity gaps.
- Window retention (`grace`) MUST exceed late-data tolerance; windowed
  results are emitted once and do not update for late events beyond grace.

## Idempotency of state

- Replays rebuild state deterministically (given same input + serdes).
- State is NOT replayable across serde/schema changes — coordinate via
  versioned serdes and reset policy.