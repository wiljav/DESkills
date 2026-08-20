---
name: dataflow-basics
metadata:
  category: DataProcessing
description: >-
  Builds and runs Apache Beam pipelines on Google Dataflow for batch and
  streaming workloads: pipeline structure, I/O transforms, and deployment
  options. Use when deploying Beam pipelines to Dataflow or porting batch
  logic to the Beam model. Don't use for general Spark tuning (use
  spark-optimization) or Flink-specific streaming (use flink-basics).
allowed-tools:
  - python
  - gcloud
  - java
---

# Google Dataflow Basics

Dataflow is Google Cloud's unified batch/streaming runner for Apache Beam.
This skill covers pipeline authoring, I/O, and safe deployment.

## Prerequisites

- A GCP project with Dataflow API enabled and a service account scoped for
  the pipeline's data access (see auth skill).
- Python 3.9+ with `apache-beam[gcp]` for Python pipelines.
- A staging GCS bucket for the pipeline's temp files.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `dataflow jobs list`, reading job graphs and
  metrics, `df-describe` style inspection of existing jobs.
- **Tier M (mutation)**: launching jobs, cancelling/draining jobs, writing to
  warehouse/storage, and enabling Dataflow Prime features. All MUST be
  confirmed; a Dataflow job with `overwrite` output semantics replaces data.

## Workflow

### 1. Author the Pipeline

```python
import apache_beam as beam

def run():
    with beam.Pipeline(options=options) as p:
        (
            p
            | "Read" >> beam.io.ReadFromParquet("gs://bucket/input/*.parquet")
            | "Filter" >> beam.Filter(lambda row: row["status"] == "active")
            | "Write" >> beam.io.WriteToParquet(
                "gs://bucket/output/", schema=SCHEMA
            )
        )
```

Rules:

- Pipeline = source transform -> processing -> sink transform; keep
  transforms as pure functions for testability.
- Use the runner-agnostic `DirectRunner` locally, `DataflowRunner` for GCP.
- Never hardcode project/credentials; read from the pipeline options.

### 2. Choose I/O

- `ReadFromParquet`/`WriteToParquet`, BigQuery IO
  (`beam.io.gcp.bigquery`), Pub/Sub IO (`ReadFromPubSub`/`WriteToPubSub`).
- Streaming pipelines MUST use Pub/Sub or Kafka IO as sources (bounded reads
  do not stream).
- For warehouse writes prefer the BigQuery IO `WRITE_TRUNCATE` (confirmed)
  or `WRITE_APPEND` with dedup keys for idempotency.

### 3. Configure the Pipeline Options

```python
options = PipelineOptions(
    runner="DataflowRunner",
    project="{project}",
    region="us-central1",
    temp_location="gs://bucket/tmp/",
    staging_location="gs://bucket/staging/",
    job_name="de-pipeline",
    num_workers=4,
    max_num_workers=40,
    autoscaling_algorithm="THROUGHPUT_BASED",
    worker_machine_type="n1-standard-4",
)
```

- Set `max_num_workers` to bound cost; autoscaling raises workers up to it.
- Use worker-appropriate machine types for memory-heavy transforms.
- Streaming: keep `job_name` stable across runs so Drain/Update can target
  the job.

### 4. Deploy (Confirmed)

```bash
python pipeline.py \
  --runner DataflowRunner \
  --project {project} \
  --region us-central1 \
  --temp_location gs://bucket/tmp/ \
  --staging_location gs://bucket/staging/
```

or with the job builder:

```bash
gcloud dataflow flex-template run {job_name} \
  --template-file-gcs-location gs://bucket/templates/pipeline.json \
  --parameters input=gs://bucket/input/
```

Prefer flex templates for repeatable production deployments: the template
pins the pipeline artifact, parameters are supplied per run.

### 5. Monitor and Validate

```bash
gcloud dataflow jobs list --region us-central1 --status active
gcloud dataflow jobs show {job_id} --format="value(currentState)"
gcloud dataflow jobs describe {job_id} --format="table(stages[].name, stages[].metrics[].metric, stages[].metrics[].scalar)"
```

- Watch for `cancelled`/`failed` states; check worker logs in Cloud Logging
  (`resource.type="dataflow_step"`).
- Validate output counts and freshness per the pipeline's data quality
  checks.

## Validation

- Job reaches `JOB_STATE_RUNNING`, then `JOB_STATE_DONE` (batch).
- Metrics: elements consumed == elements written (or within dedup bounds).
- Streaming: watermark lag within SLA; no sustained backlog.
- Output table/objects exist with expected counts.

## Definition of Done

- Pipeline authored with pure transforms and explicit I/O.
- Deployment used confirmed settings (workers bounded, temp/staging set).
- Job completed (batch) or healthy (streaming) with metrics reviewed.
- Cost exposure documented (worker-hours, data volume).

## Reference Directory

- [Pipeline Patterns](references/pipeline-patterns.md): side inputs,
  windows, and stateful transforms.
- [Deployment & Lifecycle](references/deployment.md): templates, update vs
  drain, and job lifecycle commands.

## Related Skills

- [Streaming Analytics Pipeline](../../solutions/streaming-analytics-pipeline/SKILL.md):
  full streaming architecture using Dataflow.
- [Data Engineering Authentication](../../platform/data-engineering-auth/SKILL.md):
  service account scoping for jobs.
- [Flink Basics](../flink-basics/SKILL.md): alternative streaming engine.