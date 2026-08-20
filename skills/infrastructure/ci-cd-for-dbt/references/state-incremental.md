# State & Incremental Deploys

## How dbt state works

- `dbt build --state ./manifest` compares the run against a previously
  produced `manifest.json`.
- `state:modified+` selects: the model itself + its downstream dependents.
- Stale state = full runs: always refresh the state artifact after a
  successful deploy.

## State artifact flow

1. Deploy job runs; saves `target/manifest.json` as an artifact.
2. Next deploy downloads it as `./manifest`.
3. `--select state:modified+` picks only changed models and their
   dependents.

## Rules

- Never `--full-refresh` without explicit confirmation (it drops/recreates
  tables; huge on big models).
- Test the `state:modified+` select on a PR first
  (`dbt ls --select state:modified+ --state ./manifest`).
- Freshness: keep the state artifact current — stale state silently
  converts incremental deploys into full builds.