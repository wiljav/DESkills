# Extensions

## Loading pattern

```sql
INSTALL {ext};  -- one time
LOAD {ext};     -- per session
```

## httpfs

Adds `s3://`, `gs://`, `azure://`, and HTTP(S) reads/writes.

```sql
INSTALL httpfs; LOAD httpfs;
SET s3_region='us-east-1';
SET s3_access_key_id=current_setting('env_s3_key');
```

Rules: prefer environment-variable indirection; never embed keys in SQL.

## postgres / mysql

Attach a live server database:

```sql
INSTALL postgres; LOAD postgres;
ATTACH 'host=... user=... dbname=...' AS pg (TYPE postgres, READ_ONLY);
SELECT * FROM pg.public.events;
```

READ_ONLY attachment prevents accidental mutation — the default for ad-hoc
analysis.

## iceberg

Query Iceberg tables via REST or file catalogs:

```sql
INSTALL iceberg; LOAD iceberg;
SELECT * FROM iceberg_scan('s3://bucket/warehouse/db/table', allow_moved_paths=true);
```

## spatial, json, parquet

- `json`: `read_json_auto()` for schema-inferred JSON.
- `spatial`: `ST_*` functions and GeoParquet.
- `parquet`: auto-loaded core; no INSTALL needed.