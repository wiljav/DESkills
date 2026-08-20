# Failure Signatures

Decision tree for Spark failures. Diagnosis commands are examples for a
Spark-on-YARN/GKE deployment; adapt the log source to your platform.

## 1. Executor OOM

Signal: executor logs contain `OutOfMemoryError`; tasks repeatedly fail with
`ExecutorLostFailure`.

Diagnosis:

```bash
yarn logs -applicationId {app_id} -log_files stderr | grep -i "outofmemory\|heap space"
```

Check the UI executor page for spill. Fix (in order): reduce partition size
(more partitions) -> increase `spark.executor.memory` -> add
`spark.executor.memoryOverhead`.

## 2. Driver OOM

Signal: driver log shows `Driver stack trace` with `OutOfMemoryError`.

Diagnosis: search the driver log for `collect`, `take`, `toPandas`.

Fix: replace `collect()` with storage-backed writes; for genuinely small
results, `take(N)` with a bound. Increase `spark.driver.memory` only when the
result is legitimately large.

## 3. Skew

Signal: one task's duration dwarfs all others; the stage "tail" is long.

Diagnosis:

```python
spark.read.parquet("s3a://bucket/input/").groupBy("key").count().orderBy(F.desc("count")).show(10)
```

Fix: salt hot keys or two-path join (see spark-optimization joins reference);
enable AQE skew join.

## 4. Missing input

Signal: `FileNotFoundError: Path does not exist` / `NoSuchObjectException`.

Diagnosis: verify the path:

```bash
aws s3 ls s3://bucket/prefix/ | tail
gsutil ls gs://bucket/prefix/ | tail
```

Fix: upstream producer issue — coordinate, then re-run after the data lands.
Never fabricate the input.

## 5. Task not serializable

Signal: `org.apache.spark.SparkException: Task not serializable` with a
reference to your class/lambda.

Diagnosis: inspect the exception's object chain (the offending object is
named in the traceback).

Fix: remove non-serializable captures (DB connections, clients, loggers)
from closures; initialize inside tasks; use DataFrame APIs instead of UDFs.

## 6. Container killed

Signal: `Container killed on request. Exit code is 143` / `137`.

Diagnosis: exit 137 = OOM-killed by the container runtime; 143 = SIGTERM
(preemption/scale-down).

Fix: 137 -> memory config per signature #1; 143 -> check cluster autoscaling
and queue priority.

## 7. Catalog / schema mismatch

Signal: `Table or view not found`, `AnalysisException: cannot resolve`.

Diagnosis: compare expected vs actual schema:

```python
spark.read.format("iceberg").load("catalog.db.table").schema
```

Fix: align code to the current schema or repair the table metadata; schema
drift prevention belongs to data contracts (governance skills).