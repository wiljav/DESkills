# Common Server Catalogue

Reference list of popular MCP servers for data platforms. Verify the package
name and version before installing; `uvx` runs the latest release unless a
version is pinned.

| Platform | Package (example) | Typical tools |
| --- | --- | --- |
| BigQuery | `bigquery-mcp-server` | `query`, `list_datasets`, `list_tables` |
| Snowflake | `snowflake-mcp-server` | `run_sql`, `list_warehouses`, `describe_table` |
| Redshift | `redshift-mcp-server` | `query`, `show_tables`, `describe` |
| DataHub | `datahub-mcp-server` | `search_entities`, `get_lineage`, `get_dataset_profile` |
| Airflow | `airflow-mcp-server` | `get_dag`, `list_dag_runs`, `trigger_dag` (write) |
| Dagster | `dagster-mcp-server` | `list_assets`, `get_run_status`, `launch_run` (write) |
| S3 | `s3-mcp-server` | `list_objects`, `read_object`, `put_object` (write) |
| GCS | `gcs-mcp-server` | `list_buckets`, `read_object` |

## Notes

- Prefer read-only flags or scoped IAM when the session only needs reads.
- Write tools (trigger DAG runs, `put_object`) MUST be registered as Tier M
  and require user confirmation before use.
- If a server exposes more tools than needed, use the harness's tool filtering
  if available to reduce the agent's attack surface.
