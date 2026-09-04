# Incident Log Template

## Incident

- **ID**: `{INC-YYYY-NNN}`
- **Date (UTC)**: `{date}`
- **Severity**: `{SEV-1..3}`
- **Asset(s)**: `{table(s)}`
- **Detected by**: `{alert | consumer report | manual}`

## Timeline

- `{t0} detection` — first violating metric/report
- `{t1} verification` — reproduced read-only; confirmed real / false alarm
- `{t2} blast radius` — affected tables + consumers identified
- `{t3} mitigation` — consumers blocked / pipeline paused
- `{t4} root cause` — `{upstream | ingestion | transformation | env}`
- `{t5} fix deployed` — `{change, PR link}`
- `{t6} repair` — `{re-run | SQL repair | snapshot}` with verification counts
- `{t7} closed` — monitoring green; consumers unblocked

## Root cause

- `{one paragraph}`

## Impact

- `{tables, consumers, duration, rows}`

## Prevention

- `{new/changed checks, thresholds, ownership changes, code guardrails}`

## Follow-ups

- [ ] `{item}` — owner, due date
