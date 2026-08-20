# Replication & CDC

## Logical replication

```sql
SHOW wal_level;             -- must be 'logical'
CREATE PUBLICATION de_pub FOR TABLE orders, customers;
SELECT * FROM pg_replication_slots;  -- one slot per subscriber
```

- Publisher: writes the change stream. Subscriber: applies it (e.g.
  Debezium connector -> Kafka topic).
- Slots hold the WAL until consumed — orphaned slots grow disk
  unboundedly. Monitor + drop unused slots.

## Debezium wiring (Kafka)

- Debezium Postgres connector uses logical replication slots.
- One connector per table set; snapshot first, then stream changes.
- Heartbeat events help detect lag beyond the WAL retention window.

## Monitoring

| Metric | View | Alert when |
| --- | --- | --- |
| Slot lag (bytes/WAL) | `pg_replication_slots` | grows > retention window |
| Stream lag (ms) | Debezium/consumer offsets | > SLA |
| WAL disk | `pg_wal` size | disk pressure |

## Failures

- Consumer down long enough -> WAL wraps -> snapshot re-run needed:
  restore from snapshot + replay, or re-snapshot.
- Test the re-snapshot path quarterly; document the runbook entry.