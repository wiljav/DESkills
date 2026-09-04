# Runbook Template

Copy this skeleton for each post-incident entry.

## Incident

- **Date/time (UTC)**: `{date}T{time}`
- **DAG / task**: `{dag_id}` / `{task_id}`
- **Run id**: `{run_id}`
- **Severity**: `{SEV-1..SEV-3}`

## Failure signature

- `{import error | task exception | stuck | retry storm | missing run | upstream data}`

## Timeline

- `{time} detection` — `{how it was detected}`
- `{time} diagnosis` — `{root cause hypothesis}`
- `{time} fix applied` — `{mutation performed, who approved}`
- `{time} verification` — `{run result}`

## Root cause

- `{one paragraph: what actually broke and why}`

## Fix & prevention

- `{code change / config change / alert change}`
- `{follow-up item to prevent recurrence}`

## Verification

- `{affected interval(s) re-ran successfully; idempotency confirmed | skipped with explicit agreement}`
