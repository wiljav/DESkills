# Data Engineering Agent Skills

[![CI](https://github.com/your-org/DE_skills/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/DE_skills/actions/workflows/ci.yml)

A production-grade, machine-validated collection of [Agent Skills](https://agentskills.io/home)
for data engineering, focused on **multi-cloud and open-source** tooling.

Skills are self-contained directories that teach an AI agent how to complete a
specific data-engineering task: prerequisites, safe execution tiers, step-by-step
workflow phases, validation steps, and a definition of done. Every skill is
validated against a JSON Schema, linted, unit-tested, and link-checked in CI.

## Installation

```bash
git clone git@github.com:your-org/DE_skills.git
make ci          # run the full local validation pipeline
```

To use a skill with an agent harness, point the harness at the skill directory
(or install via the marketplace manifests — see [Agent integrations](docs/agent-integrations.md)).

## Available Skills

<!-- BEGIN SKILLS -->
- **Data Governance**
  - [**Data Contracts**](./skills/governance/data-contracts): Design and enforce producer-consumer data contracts across the platform.
  - [**DataHub Catalog**](./skills/governance/datahub-catalog): Register, document, and discover data assets in DataHub.
  - [**Metadata Catalog Comparison**](./skills/governance/metadata-catalog-comparison): Choose between DataHub, Unity Catalog, Glue, and knowledge-catalog tools.
  - [**OpenLineage**](./skills/governance/openlineage-basics): Emit and query lineage events from orchestrators and compute engines.
  - [**PII Classification & Masking**](./skills/governance/pii-classification-and-masking): Detect, classify, and mask personally identifiable information in datasets.

- **Data Infrastructure**
  - [**CI/CD for dbt**](./skills/infrastructure/ci-cd-for-dbt): Test, lint, and deploy dbt projects through pull-request pipelines.
  - [**Dockerized Airflow Development**](./skills/infrastructure/docker-airflow-dev): Stand up a reproducible local Airflow development environment with Docker.
  - [**Kubernetes for Data Jobs**](./skills/infrastructure/k8s-for-data-jobs): Run batch and streaming workloads on Kubernetes with best practices.
  - [**Terraform for Data Platforms**](./skills/infrastructure/terraform-for-data): Provision warehouse, storage, and orchestrator infrastructure as code.

- **Data Ingestion**
  - [**Airbyte**](./skills/ingestion/airbyte-basics): Build and operate ELT connectors for batch and sync-based ingestion.
  - [**dlt (Python) Ingestion**](./skills/ingestion/dlt-python-ingestion): Declarative Python data pipelines that load from any source into warehouses.
  - [**File Ingestion (GCS/S3)**](./skills/ingestion/file-ingestion-gcs-s3): Ingest files from object storage into lakehouse tables with schema inference.
  - [**Apache Kafka Basics**](./skills/ingestion/kafka-basics): Create topics, produce and consume messages, and size clusters for data pipelines.
  - [**Kafka Connect**](./skills/ingestion/kafka-connect): Stand up connectors to move data between Kafka and storage/databases.

- **Data Processing**
  - [**Google Dataflow Basics**](./skills/processing/dataflow-basics): Build and run Apache Beam pipelines on Dataflow with streaming and batch support.
  - [**DuckDB Basics**](./skills/processing/duckdb-basics): Use DuckDB for local analytics, in-process OLAP, and zero-copy queries over Parquet.
  - [**Apache Flink Basics**](./skills/processing/flink-basics): Build streaming and batch jobs with Flink DataStream and Table APIs.
  - [**Apache Spark Basics**](./skills/processing/spark-basics): Write, run, and debug PySpark batch jobs against lakehouse tables.
  - [**Spark Optimization**](./skills/processing/spark-optimization): Tune partitions, joins, memory, and shuffles for faster Spark jobs.
  - [**Spark Troubleshooting**](./skills/processing/spark-troubleshooting): Diagnose OOM, skew, stragglers, and job failures using driver/executor logs.

- **Data Quality**
  - [**Data Observability**](./skills/quality/data-observability): Instrument pipelines with metrics, freshness, volume, and anomaly detection.
  - [**Data Quality Incident Runbook**](./skills/quality/data-quality-incident-runbook): Triage, remediate, and post-mortem data quality incidents end to end.
  - [**dbt Data Quality Tests**](./skills/quality/dbt-data-quality-tests): Enforce uniqueness, not-null, referential, and freshness guarantees in dbt.
  - [**Great Expectations**](./skills/quality/great-expectations): Define, run, and monitor data expectations against batch data.
  - [**Soda**](./skills/quality/soda-basics): Write and run data quality checks with Soda Core and Soda Checks Language.

- **Data Transformation**
  - [**dbt Core**](./skills/transformation/dbt-core): Model, test, and document warehouse data with dbt projects.
  - [**dbt Tests & Macros**](./skills/transformation/dbt-tests-macros): Write singular/generic tests, macros, and packages for reliable dbt projects.
  - [**SQL Transformation Best Practices**](./skills/transformation/sql-transformation-best-practices): Write performant, maintainable, and reviewable transformation SQL.

- **Databases**
  - [**MongoDB Basics**](./skills/databases/mongodb-basics): Model, query, and integrate MongoDB document collections into pipelines.
  - [**MySQL Basics**](./skills/databases/mysql-basics): Configure, tune, and integrate MySQL into data platforms.
  - [**PostgreSQL Basics**](./skills/databases/postgres-basics): Configure, tune, and integrate PostgreSQL into data platforms.

- **Getting Started**
  - [**Data Engineering Authentication**](./skills/platform/data-engineering-auth): Configure cloud and toolchain credentials using short-lived, scoped access.
  - [**Data Engineering Stack Setup**](./skills/platform/de-stack-getting-started): Bootstrap the local DE toolchain: Python, Spark, dbt, Airflow, and Docker.
  - [**MCP Servers for Data**](./skills/platform/mcp-servers-for-data): Connect agents to data platforms through Model Context Protocol servers.

- **Orchestration**
  - [**Apache Airflow Basics**](./skills/orchestration/airflow-basics): Install, configure, and operate Airflow as the pipeline orchestrator.
  - [**Airflow DAG Authoring**](./skills/orchestration/airflow-dag-authoring): Author production DAGs with idempotency, retries, and correct task design.
  - [**Airflow Job Failure Troubleshooting**](./skills/orchestration/airflow-job-failure-troubleshooting): Diagnose scheduler, task, and infrastructure failures from Airflow logs.
  - [**Dagster Basics**](./skills/orchestration/dagster-basics): Build typed, testable data pipelines with assets, ops, and jobs in Dagster.
  - [**Prefect Basics**](./skills/orchestration/prefect-basics): Orchestrate Python data workflows with Prefect flows and deployments.

- **Solutions**
  - [**Batch ETL Pipeline**](./skills/solutions/batch-etl-pipeline): Build an end-to-end batch ETL pipeline with ingestion, transformation, and quality gates.
  - [**Data Platform Architecture**](./skills/solutions/data-platform-architecture): Design a production data platform: zones, tools, and governance blueprint.
  - [**Lakehouse Migration**](./skills/solutions/lakehouse-migration): Migrate from data warehouse to open lakehouse with staged cutover.
  - [**Streaming Analytics Pipeline**](./skills/solutions/streaming-analytics-pipeline): Build an end-to-end streaming pipeline with CDC, processing, and serving.

- **Storage & Lakehouse**
  - [**Delta Lake Basics**](./skills/storage/delta-lake-basics): Use Delta tables, ACID transactions, and versioning in lakehouse pipelines.
  - [**Apache Hudi Basics**](./skills/storage/hudi-basics): Manage incremental upserts and table services on Hudi tables.
  - [**Apache Iceberg Basics**](./skills/storage/iceberg-basics): Create tables, manage snapshots, and use time travel with Iceberg catalogs.
  - [**Object Storage Basics**](./skills/storage/object-storage-basics): Design buckets, prefixes, lifecycle, and security for S3 and GCS.
  - [**Parquet & File Formats**](./skills/storage/parquet-file-formats): Choose and optimize Parquet, ORC, Avro, and compression for analytic workloads.

- **Streaming**
  - [**Flink SQL**](./skills/streaming/flink-sql): Author streaming pipelines with Flink SQL and change-data-capture sources.
  - [**Kafka Streams**](./skills/streaming/kafka-streams): Build stateful stream processing applications on Kafka Streams.
  - [**Streaming Architecture Patterns**](./skills/streaming/streaming-architecture-patterns): Choose event-driven, CDC, and lambda/kappa patterns for real-time platforms.

- **Warehousing**
  - [**BigQuery Basics**](./skills/warehousing/bigquery-basics): Manage datasets, tables, and jobs; query and load data in BigQuery.
  - [**Amazon Redshift Basics**](./skills/warehousing/redshift-basics): Provision clusters, design distribution styles, and run analytics on Redshift.
  - [**Snowflake Basics**](./skills/warehousing/snowflake-basics): Configure warehouses, databases, stages, and query patterns in Snowflake.
  - [**Warehouse Optimization**](./skills/warehousing/warehouse-optimization): Reduce cost and improve query performance with partitioning, clustering, and materialization.
<!-- END SKILLS -->

## Repository layout

```
skills/<domain>/<skill-name>/     one directory per skill
  SKILL.md                        entry point: frontmatter + workflow + definition of done
  references/                     per-topic deep-dive docs
  scripts/                        executable helpers + requirements.txt + tests
  assets/                         templates (DAGs, dbt projects, terraform, configs)
catalog.yaml                      canonical skill registry (source of truth for the index)
schema/skill.schema.json          JSON Schema for SKILL.md frontmatter
tools/                            repository tooling (validate, generate, check)
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the authoring checklist and quality
gates every skill must pass.

## Support

Open an issue in the repository tracker for bugs, outdated patterns, or skill
requests.

## License

Apache 2.0. See [LICENSE](LICENSE).
