# Binlog CDC

## Why ROW format

- Statement format logs SQL text — `UPDATE ... WHERE` can't be replayed
  exactly; ROW logs before/after images per row.
- Debezium requires ROW for correct change capture.
- Cost: more binlog volume — accept it, it is the price of correct CDC.

## GTID mode

- `gtid_mode=ON` + `enforce_gtid_consistency=ON`: every transaction gets
  a global ID.
- Consumer offsets (Debezium `gtid`) resume exactly where they stopped —
  no file/position guessing.

## Debezium connector basics

- One connector per schema/table set; snapshot phase first (consistent
  dump), then streaming.
- Store offsets in Kafka connect offsets topic; never reset casually
  (snapshot re-run follows).
- Monitor `source.ts_ms` vs now for stream lag.

## Retention

- Binlog retention (`expire_logs_days` or `binlog_expire_logs_seconds`)
  MUST exceed the worst-case consumer lag — otherwise a lagging consumer
  silently loses changes and needs a re-snapshot.
- Re-snapshot = full re-read of the table; test the process quarterly.
