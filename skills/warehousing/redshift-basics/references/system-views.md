# System Views for Diagnostics

| View | Answers |
| --- | --- |
| `SVV_TABLE_INFO` | table size, distribution health, skew |
| `STL_QUERY` | query history, timing per query |
| `STL_EXPLAIN` | actual plan execution details |
| `STL_LOAD_ERRORS` | COPY load failures with line/field info |
| `STL_WLM_QUERY` | workload manager queueing/waiting |
| `SVL_QUERY_SUMMARY` | per-step runtime breakdown |

## Typical diagnosis queries

```sql
-- skew: are slices balanced?
SELECT slice, COUNT(*) FROM orders GROUP BY slice ORDER BY 2 DESC;

-- slowest queries today
SELECT query, starttime, datediff(ms, starttime, endtime) AS ms
FROM stl_query
WHERE starttime > now() - interval '1 day'
ORDER BY ms DESC LIMIT 10;

-- load errors
SELECT * FROM stl_load_errors ORDER BY starttime DESC LIMIT 5;
```

## WLM / queuing

- `STL_WLM_QUERY` `state='queued'` rows indicate concurrency pressure —
  scale the cluster or add work queues.
- Redshift Serverless avoids most queueing; provisioned clusters need queue
  design.
