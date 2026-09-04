# Load Patterns

## Copy (lakehouse `COPY INTO`)

- BigQuery: `LOAD DATA ... FROM FILES` / external table + `CREATE OR
  REPLACE` partition.
- Snowflake: `COPY INTO table FROM @stage` with `FILE_FORMAT` and
  `PATTERN`.
- Redshift: `COPY` from the role-accessible bucket.

Rules: `COPY INTO` is atomic per statement; use `ON_ERROR` policies to
quarantine instead of aborting.

## External tables / zero-copy

- BigQuery external tables / Databricks `_symlink_format_manifest` for
  Iceberg over files.
- Good for exploratory reads; production serving should copy to managed
  tables (query cost + performance).

## Staged load (engine-agnostic)

1. Stage: load new files into a `_staging` table with `_source_file`.
2. Validate: row counts, schema, checks.
3. Merge/insert into the target partition.
4. Archive files + update control table.

Best when the engine's native load lacks idempotency primitives.

## Retry semantics

- At-least-once: re-run is safe (dedup by `_source_file`).
- Never "delete the partition then load" unless the files are immutable
  and the window is fully present.
