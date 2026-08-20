# Caching & Retries

## Retries

```python
@task(retries=2, retry_delay_seconds=60, retry_jitter_factor=0.5)
def flaky_call():
    ...
```

- Retries apply per task, not per flow.
- A deterministic failure will retry until exhausted — that is correct
  behavior; fix the root cause rather than inflating retries.
- `retry_jitter_factor` spreads retries to avoid thundering herds.

## Caching

Prefect caches task results by default when result storage is configured
(`result_persist=True`). Cache keys derive from task inputs + cache key fn.

```python
@task(cache_key_fn=task_input_hash, cache_policy=None)
def expensive_load(url: str):
    ...
```

Rules:

- Only cache idempotent, immutable-input tasks. Never cache tasks that read
  live data (the cache would serve stale results).
- Invalidate intentionally by changing the cache key function or bumping a
  version parameter.

## Idempotency in flows

- A flow run that fails mid-way must be safely re-runnable: downstream tasks
  should either overwrite their output or be guarded by a check.
- Prefer `INSERT OVERWRITE`-style semantics or delete-then-insert inside
  tasks so partial writes never corrupt final data.