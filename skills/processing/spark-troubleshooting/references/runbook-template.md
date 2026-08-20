# Runbook Template

Copy this skeleton per incident.

## Incident

- **Date/time (UTC)**: `{date}T{time}`
- **Application / job**: `{app_id}` / `{job_name}`
- **Cluster**: `{platform + cluster id}`
- **Severity**: `{SEV-1..SEV-3}`

## Failure signature

- `{executor OOM | driver OOM | skew | missing input | serialization | container killed | catalog mismatch}`

## Timeline

- `{time} detection` — `{who/what detected}`
- `{time} diagnosis` — `{root cause hypothesis}`
- `{time} fix applied` — `{code/config change, approver}`
- `{time} verification` — `{re-run result + metrics}`

## Root cause

- `{one paragraph}`

## Fix & prevention

- `{code/config/alert change}`
- `{follow-up}`

## Verification

- `{failed stage completes; spill/GC/skew metrics healthy; data verified}`