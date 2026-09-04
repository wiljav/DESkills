# Time & Window Functions

## Windows

| Window | Syntax | Use |
| --- | --- | --- |
| Tumbling | `TUMBLE(ts, INTERVAL '1' HOUR)` | fixed non-overlapping buckets |
| Hopping (sliding) | `HOP(ts, INTERVAL '15' MINUTE, INTERVAL '1' HOUR)` | overlapping windows |
| Session | `SESSION(ts, INTERVAL '30' MINUTE)` | activity gaps end the window |

## Watermark tuning

- `WATERMARK FOR event_time AS event_time - INTERVAL '5' SECONDS` — the
  delay trades completeness vs latency.
- Too small: late rows land in `null`-window / dropped.
- Too large: window results arrive late.
- Observe the UI's watermark vs event-time spread; set delay >= the p95
  lateness.

## Late data

- Late events after the watermark: dropped for non-update windows.
- `WITH LATE EVENT DELAY` / update modes on sinks: use `upsert` sinks for
  window results if correctness under late data matters more than latency.

## Grouping helpers

- `TUMBLE_START/TUMBLE_END` for window boundaries.
- `GROUP BY window_start, window_end` when the window needs to be re-joined.
