# Topic Design

## Partitioning math

- Throughput target per partition: ~5-10 MB/s sustained (single-threaded
  producer/consumer limits).
- Ordering is per-partition: keyed producers place all events of a key in
  one partition.
- Partition count is largely fixed for the topic's life: changing it
  rebalances keys and breaks compacted ordering. Size for peak, not today.

## Keying

- Key = the grouping dimension downstream consumers need (customer_id,
  device_id, order_id).
- `null` key = round-robin distribution; fine for firehose topics.
- A badly keyed topic (e.g. timestamp keys) makes every partition hot —
  keys MUST have high cardinality.

## Compaction

```bash
kafka-topics --bootstrap-server {broker} \
  --alter --topic user_state \
  --config cleanup.policy=compact \
  --config segment.ms=600000
```

- Compacted topics keep the latest value per key; consumers see a
  full-state snapshot.
- `segment.ms` bounds compaction latency; `min.cleanable.dirty.ratio`
  controls when compaction runs.

## Retention policy

| Policy | When |
| --- | --- |
| time-based (`retention.ms`) | replayable events (audit, analytics) |
| size-based (`retention.bytes`) | bounded disk cost |
| compact | keyed state |

Set time-based retention generously for pipelines whose consumers may lag
(48h-7d typical); lag beyond retention = data loss by design.