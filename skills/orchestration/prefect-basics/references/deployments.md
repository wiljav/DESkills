# Deployments & Work Pools

## Deployments

A deployment = flow code + metadata (parameters, schedule, work pool).
Created via:

```bash
prefect deployment build {module}:{flow_name} -n {name} -q {queue} -o {file}.yaml
prefect deployment apply {file}.yaml
```

The YAML file is the deployment artifact — commit it. Never put secrets in
deployment YAML; use Prefect blocks for credentials.

## Work pools & workers

- A **work pool** defines infrastructure (local process, Docker, Kubernetes).
- A **worker** polls the pool's queue and executes scheduled runs.
- Queues let you route runs: `-q production` vs `-q dev`.

Local worker:

```bash
prefect worker start -p {pool_name}
```

## Schedules

```bash
prefect deployment schedule create {flow}/{deployment} --interval 86400
prefect deployment schedule create {flow}/{deployment} --cron "0 8 * * *" --timezone "UTC"
```

Rules:

- Prefer cron with explicit timezone for business schedules.
- Pausing a schedule does not affect already-queued runs; cancel those
  explicitly if needed.

## Secrets (Prefect blocks)

```bash
prefect block register -m prefect_gcp
prefect block create "secret" --name my-secret   # prompts for value
```

Reference in flows with `Secret.load("my-secret").get()`. Blocks never
appear in flow code or logs.
