# Pipeline Patterns

## Side inputs

Small reference data applied per-element:

```python
dimensions = p | "ReadDim" >> beam.io.ReadFromParquet("gs://bucket/dims/")

main = p | "Read" >> beam.io.ReadFromParquet("gs://bucket/events/")
result = main | "Join" >> beam.ParDo(JoinWithDim(), beam.pvalue.AsSingleton(dimensions))
```

Rules:

- Side inputs are broadcast; keep them small (cache-friendly).
- For large reference data, prefer a `CoGroupByKey` join instead.

## Windowing (streaming)

```python
from apache_beam.transforms import window

events = p | beam.io.ReadFromPubSub(...) \
    | "Window" >> beam.WindowInto(
        window.FixedWindows(300),
        trigger=window.AfterWatermark(early=AfterProcessingTime(60)),
    )
```

- Default trigger is after-watermark with late data allowed until the
  window closes.
- Use allowed lateness (`with_allowed_lateness`) to handle stragglers;
  balance against watermark lag.

## Stateful processing

`StatefulDoFn` with `@state` (ValueState, BagState) enables per-key state in
streaming without external stores. Prefer SQL-like aggregations where
possible; use stateful DoFns for dedup, session logic, and enrichment that
needs per-key memory.

## Idempotency

- Writes: `WRITE_TRUNCATE` with partition overwrite semantics per run key, or
  `WRITE_APPEND` with dedup by event id.
- Streaming replays: Pub/Sub at-least-once means the pipeline MUST dedup or
  the sink MUST be idempotent (BigQuery streaming dedup via table insertId
  when enabled).