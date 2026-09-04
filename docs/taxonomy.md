# Taxonomy

The catalog is organized into 13 categories. Every skill maps to exactly one
category; every category maps to one or more domain directories under
`skills/`.

| Category (`metadata.category`) | Domains | Scope |
| --- | --- | --- |
| `DataIngestion` | `ingestion/` | Getting data into the platform |
| `StorageAndLakehouse` | `storage/` | Where data lives and its file/table format |
| `Warehousing` | `warehousing/` | SQL warehouses and serving |
| `DataProcessing` | `processing/` | Compute engines for batch processing |
| `DataTransformation` | `transformation/` | Modeling and SQL transformation |
| `Orchestration` | `orchestration/` | Scheduling and DAG management |
| `Streaming` | `streaming/` | Real-time and event-driven processing |
| `DataQuality` | `quality/` | Testing, monitoring, and incident response |
| `DataGovernance` | `governance/` | Contracts, lineage, catalogs, PII |
| `Databases` | `databases/` | Transactional stores used by pipelines |
| `DataInfrastructure` | `infrastructure/` | IaC, containers, CI/CD |
| `Solutions` | `solutions/` | End-to-end architectures and migrations |
| `GettingStarted` | `platform/` | Setup, auth, and integrations |

## Rules

- A skill's `metadata.category` must match the category mapped to its domain
  directory (enforced by `make validate`).
- New categories require an entry in `catalog.yaml` and a section in this
  table; do not reuse a category across unrelated domains without updating the
  taxonomy.
- Skills that primarily *diagnose* failures (troubleshooting genre) stay in
  the domain of the system they operate on (e.g. `spark-troubleshooting` in
  `processing/`) and follow the failure-signature + runbook pattern.
