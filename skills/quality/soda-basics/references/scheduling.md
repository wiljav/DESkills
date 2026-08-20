# Scheduling & Alerting

## Scheduled scans

Run scans on a schedule via the orchestrator (preferred) or cron:

```bash
# cron: hourly freshness + daily full checks
0 * * * * soda scan -d orders_db -c config.yml checks/freshness.yml
15 6 * * * soda scan -d orders_db -c config.yml checks/ && echo ok
```

Rules:

- Separate freshness (frequent, cheap) from full suites (daily, expensive).
- The orchestrator owns scheduling in production so failures surface in the
  same place as pipeline failures.

## Notifications

Soda can send scan results to Slack (webhook) and email via config; keep the
distribution list per-check (ownership matters — the runbook skill depends
on clear ownership).

## Result stores

- Soda Cloud (SaaS) aggregates history, or:
- Export scan JSON (`soda scan ... --output-path results.json`) and ship to
  the observability backend for trend tracking.

## Alert hygiene

- Every check must have an owner and an SLA for response.
- Thresholds changed only with justification; a changelog in the checks file
  comment header keeps history.