# Tool Versions

Reference matrix used by the stack-setup skill. Keep this file updated when
the minimum supported versions change; CI does not enforce these values but
the skill treats them as the floor.

| Tool | Minimum | Recommended | Notes |
| --- | --- | --- | --- |
| Python | 3.10 | 3.12 | 3.12 for Apple Silicon wheels |
| uv | 0.4 | latest | used for env + tool management |
| Docker Engine | 24 | latest | Airflow image needs a running daemon |
| Apache Airflow | 2.8 | latest 2.x | `airflow standalone` requires 2.4+ |
| dbt-core | 1.7 | latest 1.x | adapters installed per warehouse |
| DuckDB | 0.10 | latest | local OLAP over Parquet |
| PySpark | 3.5 | 3.5.x | matches current docs |

## Upgrade policy

- Never upgrade a pinned tool in a pipeline without running the repo
  validation pipeline afterwards.
- Record upgrade rationale in `CHANGELOG.md`.
- If a skill script pins a version (e.g. `requirements.txt`), prefer loose
  floors (`>=`) over exact pins unless reproducibility demands exact pins.
