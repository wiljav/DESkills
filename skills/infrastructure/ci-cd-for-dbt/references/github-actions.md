# GitHub Actions Setup

## Workflow skeleton

```yaml
name: dbt CI
on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install dbt-bigquery sqlfluff
      - run: sqlfluff lint models/ --dialect bigquery
      - run: dbt deps && dbt parse

  ci-build:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install dbt-bigquery
      - env:
          DBT_PROFILES_DIR: .ci
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.DEV_SA_JSON }}
        run: dbt deps && dbt seed --target ci && dbt build --target ci

  deploy:
    if: github.ref == 'refs/heads/main'
    needs: ci-build
    environment: prod   # approval gate
    steps:
      - uses: actions/checkout@v4
      - run: pip install dbt-bigquery
      - env:
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.PROD_SA_JSON }}
        run: |
          dbt deps
          dbt build --target prod --select state:modified+ --state ./manifest
          dbt docs generate
      - uses: actions/upload-artifact@v4
        with: { name: docs, path: target/ }
```

## Gate rules

- `environment: prod` with required reviewers = the human approval gate.
- Separate service accounts per environment; per-environment secrets.
- Cache `~/.dbt` + `target/` artifacts between jobs for state-based
  selects.
