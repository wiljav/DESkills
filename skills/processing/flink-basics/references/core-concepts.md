# Core Concepts

## Event time, processing time, ingestion time

- **Event time**: timestamp in the data. Correct for late/out-of-order data;
  requires watermarks.
- **Processing time**: when the operator executes. Cheap, but results depend
  on system speed.
- **Ingestion time**: assigned at the source. Middle ground.

Prefer event time for analytics; declare watermarks so Flink knows how long
to wait for stragglers.

## Watermarks

- Watermark W means "events with event time < W will not arrive".
- `WatermarkStrategy.for_bounded_out_of_orderness(Duration.ofSeconds(5))`
  is the typical start; tune with observed lateness.
- Watermark delay is a trade: too small = dropped/late data; too big = slow
  windows.

## Windows

| Type | Use |
| --- | --- |
| Tumbling | fixed non-overlapping intervals |
| Sliding | fixed intervals with overlap (every X within Y) |
| Session | gaps in activity end the window |

## State backends

- RocksDB: large state, disk-backed, recommended for production keyed state.
- Heap: in-memory, fast, limited by JVM heap.

Choose at environment setup; switching backends mid-life requires a restart
cycle.
