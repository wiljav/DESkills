---
name: ci-cd-for-dbt
metadata:
  category: DataInfrastructure
description: >-
  Tests, lints, and deploys dbt projects through pull-request pipelines:
  profile handling, schema diffs, state comparison, and promotion to
  production. Use when wiring dbt into CI/CD or debugging deployments.
  Don't use for dbt modeling itself (use dbt-core) or for
  infrastructure-as-code (use terraform-for-data).
allowed-tools:
  - dbt
  - bash
  - python
---

# CI/CD for dbt

dbt changes must be reviewed, tested, and promoted safely: every PR runs
lint + tests, and merges deploy models with documented state.

## Prerequisites

- A dbt project in Git (structure per dbt-core).
- A CI runner (GitHub Actions per this repo's ci.yml pattern) with a
  service account per environment.
- A `profiles.yml` resolution strategy (env vars or CI secrets).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `dbt parse`, `dbt compile`, `dbt ls`, test runs
  against dev schema.
- **Tier M (mutation)**: `dbt run`/`dbt build` against shared
  environments and prod deployment. Prod runs change warehouse data —
  require the promotion gate in the workflow.

## Workflow

### 1. Set Up Profiles for CI

```yaml
# profiles.yml (injected via env, never committed)
target: ci
outputs:
  dev: &dev
    type: bigquery
    method: oauth
    project: {dev-project}
    dataset: dbt_dev_{git_branch}
  ci:
    <<: *dev
    dataset: dbt_ci
  prod:
    type: bigquery
    method: oauth
    project: {prod-project}
    dataset: analytics
```

Rules:

- One `outputs` entry per environment; the dataset name encodes
  isolation (per-branch schemas for dev).
- Credentials via CI secrets/service accounts — never in the repo.

### 2. Lint and Parse on Every PR

```bash
dbt deps
dbt parse                      # catches jinja/model errors fast
sqlfluff lint --dialect bigquery models/   # or dbt-lint / pre-commit
dbt compile
```

Rules:

- `dbt parse` + compile on every PR; lint enforced (fail on error).
- Add `pre-commit` hooks (`dbt parse`, sqlfluff) for local parity.

### 3. Test Against CI Schema

```bash
dbt seed --target ci
dbt build --target ci --select state:modified+ --state ./manifest  # incremental CI
```

Rules:

- `dbt build` = run + test in one command — the CI gate.
- Use `--state` + `state:modified+` with the merged `manifest.json`
  artifact for cheap incremental CI.
- Freshness/volume tests run here too (dbt-data-quality-tests).

### 4. Promote to Production

```bash
dbt build --target prod --select state:modified+ --state ./manifest --full-refresh-off
dbt docs generate && dbt docs serve   # or publish docs artifact
```

Rules:

- Promotion on merge to main, gated: CI passed + owner approval.
- `--state` against the prod manifest — deploys only what changed.
- `--full-refresh-off` prevents accidental full rebuilds; explicit
  `--full-refresh` only with confirmation (destructive on big tables).

### 5. Handle Rollbacks

- Fix-forward: revert the PR, re-deploy (idempotent models).
- If a model broke data: rerun the prior version via git revert, or
  restore the table (warehouse snapshot), then re-apply tests.

## Validation

- PR pipeline: parse/compile/lint/build pass; tests green in the CI
  schema.
- Prod deploy: only modified models ran; test suite green post-deploy.
- Docs artifact updated and served.

## Definition of Done

- CI/CD pipeline live (PR + promotion gates).
- Profiles isolated per environment; credentials in CI secrets.
- Incremental state-based runs working (modified-only deploys).
- Rollback path documented.

## Reference Directory

- [GitHub Actions Setup](references/github-actions.md): the workflow file
  pattern.
- [State & Incremental Deploys](references/state-incremental.md): the
  manifest/state mechanics.

## Related Skills

- [dbt Core](../../transformation/dbt-core/SKILL.md): the project being
  deployed.
- [dbt Tests & Macros](../../transformation/dbt-tests-macros/SKILL.md):
  what runs in the gate.
- [Terraform for Data](../terraform-for-data/SKILL.md): infra split.
