# Connections & Variables

## Connection URI formats

| Provider | URI scheme |
| --- | --- |
| PostgreSQL | `postgresql+psycopg2://user:pass@host:5432/db` |
| MySQL | `mysql+mysqlconnector://user:pass@host:3306/db` |
| AWS | `aws://` (credentials resolved via AWS provider chain) |
| GCP | `google-cloud-platform://` (credentials via ADC) |
| Azure | `azure://` (via `azure-common` provider chain) |
| Snowflake | `snowflake://user:pass@account/db/schema?warehouse=WH` |
| dbt | `dbt://` (via dbt Cloud provider) |

Rules:

- Never include passwords inline when a secrets backend is available.
- Use extra `json` fields for provider-specific options
  (`--conn-extra '{...}'`), validated against provider docs.
- Default connections (`airflow_db`, `aws_default`, `google_cloud_default`)
  should be overridden only through the secrets backend on production.

## Variables

- Store non-secret config in Airflow Variables; store secrets in the secrets
  backend, NOT as variables.
- Reference variables via Jinja in DAG code
  (`{{ var.value.my_var }}`, `{{ var.json.my_dict }}`) so the scheduler does
  not query the DB during parsing.
- When reading variables in Python code use
  `Variable.get("x", deserialize_json=True)` inside task context only —
  never at module import time.

## Secrets backend resolution order

1. Secrets backend (Vault/Secret Manager).
2. Airflow metadata DB (connections/variables tables).
3. Default values / env vars (`AIRFLOW_CONN_{ID}`, `AIRFLOW_VAR_{NAME}`).

Backend-secured values win; this is what allows DAG code to omit credentials
entirely.
