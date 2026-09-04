# Joins in Flink SQL

## Interval joins

Two streams joined on a time condition:

```sql
SELECT *
FROM clicks c
JOIN impressions i
  ON c.user_id = i.user_id
 AND c.ts BETWEEN i.ts AND i.ts + INTERVAL '5' MINUTE;
```

- Stateful: both sides' state is retained for the interval; bound it or
  state grows forever.
- `c.ts BETWEEN ...` IS required for streaming joins — unbounded joins do
  not exist.

## Temporal joins (versioned tables)

Join a stream to the latest version of a CDC table:

```sql
SELECT o.id, o.amount, d.name
FROM orders o
JOIN dim_customers FOR SYSTEM_TIME AS OF o.ts d
  ON o.customer_id = d.id;
```

- Requires the dimension to be declared with `PRIMARY KEY` + `debezium-json`
  format.
- Results are correct-as-of-event-time; late dimension changes do not
  retroactively update results.

## Lookup joins

Enrich with external tables (JDBC, Redis):

```sql
CREATE TEMPORARY TABLE rates (
  currency STRING, rate DECIMAL(10,6),
  PRIMARY KEY (currency) NOT ENFORCED
) WITH ('connector' = 'jdbc', ...);

SELECT t.*, r.rate
FROM trades t
JOIN rates FOR SYSTEM_TIME AS OF t.ts r ON t.currency = r.currency;
```

- Lookup joins add latency per event; cache-friendly connectors matter.
- They are not replay-safe: re-processing after a failure reads the lookup
  at the new time — document for exactly-once analyses.
