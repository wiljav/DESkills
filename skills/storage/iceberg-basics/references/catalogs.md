# Catalog Options

| Catalog | Best for | Notes |
| --- | --- | --- |
| REST catalog | default for new platforms | engine-agnostic, ACLs, works with Spark/Flink/Trino/DuckDB |
| Hive Metastore | legacy Hive/Spark fleets | shared metadata; upgrade path to REST |
| AWS Glue | AWS-native | tight S3/Athena integration; per-region |
| Nessie | git-style branching/CI on data | when data versioning workflows are needed |
| file-based (`hadoop`) | single-engine dev | no concurrent engines — dev only |

## Rules

- One catalog per environment, shared across engines (avoid per-engine
  catalogs that diverge).
- Catalog backups: export table metadata periodically; the catalog is the
  metadata of record (storage is just files).
- REST catalog is the recommended default; choose Glue only when the whole
  platform is AWS-native and existing.