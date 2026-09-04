# Resource Management

## Requests vs limits

| | requests | limits |
| --- | --- | --- |
| CPU | scheduling guarantee | cap (throttled above) |
| Memory | scheduling guarantee | cap (OOMKilled above) |

- Set both; memory requests MUST equal limits for stable jobs (limits
  above requests risk eviction under node pressure).
- CPU limits can throttle batch jobs — for data workloads prefer generous
  CPU requests and limits aligned with measured use.

## Eviction and OOM triage

- `OOMKilled` in pod status: memory limit too low or a leak — check the
  job first, raise the limit only with evidence.
- `Evicted` + `DiskPressure`/`MemoryPressure`: cluster capacity problem —
  report to the platform team; don't just shrink requests.

## Namespace quotas

- Namespaces carry `ResourceQuota` + `LimitRange` — the platform team
  sets these; jobs must fit within them (check `kubectl describe quota
  -n de`).
- Over-quota applies fail with `Forbidden` — read the quota before
  scaling up.
