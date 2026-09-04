# Worker & Task Tuning

## Worker sizing

- `tasks.max` in the connector config limits parallelism; sinks also cap at
  topic partition count.
- Worker heap: `KAFKA_HEAP_OPTS=-Xmx2g` typical per worker; more with many
  connectors.
- `offset.storage.topic`, `config.storage.topic`, `status.storage.topic`
  MUST be created with enough partitions (e.g. 25-50) and RF 3 for
  distributed mode.

## Exactly-once

- Source connectors: exactly-once only with the right Kafka version +
  `exactly.once.support=all` + transactional coordinator; otherwise
  at-least-once with idempotent sinks.
- Sink connectors: at-least-once by default; S3 sink can dedupe via
  `s3.partitioner` stable keys + idempotent writes.

## Common failures

| Symptom | Cause | Fix |
| --- | --- | --- |
| Task FAILED, trace = ConnectException | plugin missing on worker | install plugin JAR, restart worker |
| Task rebalancing loop | rebalance.timeout too low / slow worker | increase `session.timeout.ms`, check worker CPU |
| Offsets never commit | sink errors accumulate | check DLQ config, raise `errors.tolerance` |
| Lag growing | sink throughput < topic rate | more tasks (<= partitions), bigger flush |

## Restart discipline

- Fix the cause before restarting tasks — restarting a failing task without
  a fix repeats the failure.
- Prefer `PUT /connectors/{name}/pause` then fix, then `resume` for planned
  changes.
