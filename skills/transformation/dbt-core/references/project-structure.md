# Project Structure

## Folder conventions

```
dbt_project/
├── dbt_project.yml          # project config, model paths, materialization defaults
├── profiles.yml             # NOT committed; credentials via env vars
├── models/
│   ├── staging/             # stg_*: clean + type source data
│   ├── intermediate/        # int_*: joins, business logic
│   └── marts/               # fct_*, dim_*: consumer models
├── tests/                   # singular tests (SQL assertions)
├── macros/                  # reusable Jinja
├── seeds/                   # small CSV reference data
├── snapshots/               # SCD type-2
└── analyses/                # ad-hoc, not materialized
```

## Naming

- `stg_<source>_<entity>.sql` for staging.
- `fct_` for fact marts, `dim_` for dimensions, `int_` for intermediate.
- Model names are global in dbt: keep them unique and descriptive.
- Every model file has a matching YAML entry (description, tests) — docs
  degrade otherwise.

## dbt_project.yml essentials

```yaml
name: my_project
profile: my_profile
model-paths: ["models"]
models:
  my_project:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

Set materialization defaults per folder; override per model only when
justified.

## Sources vs seeds vs models

- `source()`: upstream tables owned by other teams — declare, never `ref`.
- `seed`: small static CSVs (< 1 MB-ish, warehouse-dependent).
- `model`: anything dbt builds.
