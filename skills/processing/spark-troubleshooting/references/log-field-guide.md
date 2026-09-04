# Log & UI Field Guide

## Where the signals live

| Signal | Location |
| --- | --- |
| Exception + stack trace | driver stdout/stderr (application log) |
| Task failures | UI: Stage page -> "Failed Tasks" |
| Spill | UI: Stage page -> "Spill (Memory/Disk)"; Executors page |
| GC time | UI: Executors page -> "GC Time" column |
| Shuffle read/write | UI: Stage page -> "Shuffle Read/Write (Shuffle Bytes)" |
| Skew (task time spread) | UI: Stage page -> task timeline / task durations |
| Container kill reasons | YARN ResourceManager logs / cluster scheduler events |
| AQE decisions | UI: SQL tab -> "Adaptive Execution" events |

## Driver log capture (examples)

```bash
# YARN
yarn logs -applicationId {app_id} -log_files stdout,stderr

# Dataproc
gcloud dataproc jobs wait {job_id} --project {project} --region {region}

# EMR
aws emr get-steps / emr logs via s3://{log-bucket}/elasticmapreduce/{cluster-id}/

# GKE (Spark on K8s)
kubectl logs {driver-pod} --tail=200 -n {namespace}
```

## Event logs

Enable event logging (`spark.eventLog.enabled=true`) on production so
historical runs can be re-analyzed without re-running:

```bash
spark-submit --conf spark.eventLog.enabled=true \
  --conf spark.eventLog.dir=s3a://bucket/spark-events/ \
  job.py
```

Load event logs in the Spark History Server to compare the failing run with
the last good run — the diff (config, input size, executor count) usually
names the cause.
