# Cost & Performance

## Cost drivers

- Storage bytes (tier-dependent).
- Requests: GET/PUT/list operations (small files = request-heavy and
  expensive).
- Retrieval fees from lower tiers.
- Egress between regions/clouds.

## Small-file problem

- A Parquet dataset of 1M tiny files costs more in requests than in bytes.
- Fix at the writer: target 128 MB-1 GB files (spark-optimization and
  parquet-file-formats skills cover this).
- For legacy small-file data: compaction jobs or DuckDB rewrite.

## Prefix design

- Prefixes are flat keys, not directories; `ls`/`list` with prefixes is
  efficient, deep scans are not.
- Partition layout `date=YYYY-MM-DD/` enables engine predicate pruning.
- Avoid thousands of unique prefixes per minute (lifecycle/list overhead).

## Transfers

- Large transfers: use transfer services (GCS Transfer, S3 Transfer
  Acceleration, Storage Transfer Service) — parallel, resumable, cheaper
  than ad-hoc `gsutil cp -m`.
- Cross-cloud: budget egress costs BEFORE designing the pipeline.
