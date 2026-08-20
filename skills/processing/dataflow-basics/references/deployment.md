# Deployment & Lifecycle

## Job lifecycle states

| State | Meaning | Action |
| --- | --- | --- |
| `JOB_STATE_PENDING` | queued | wait |
| `JOB_STATE_RUNNING` | executing | monitor metrics |
| `JOB_STATE_DRAINING` | stopping gracefully, finishing in-flight | verify drains complete |
| `JOB_STATE_CANCELLED` | stopped (possibly mid-stream) | check partial writes |
| `JOB_STATE_FAILED` | error | worker logs: `resource.type="dataflow_step"` |
| `JOB_STATE_DONE` | completed (batch) | validate output |

## Update vs drain

- `drain`: stops ingestion, lets in-flight data finish. Use for streaming
  jobs you are retiring; verify the sink is quiescent before cancelling.
- `update`: hot-swaps a running job with new pipeline code when
  `job_name` matches and the graph is update-compatible. Use for upgrades
  without data loss.

```bash
gcloud dataflow jobs drain {job_id} --region us-central1
gcloud dataflow jobs update {job_id} --region us-central1 --pipeline ... 
```

## Templates

- Classic templates: template stored in GCS, parameters at run time.
- Flex templates: containerized pipeline artifact; best for custom
  dependencies.

Rules:

- Template images must be rebuilt and tagged per release; never deploy
  unversioned templates.
- Run parameters (input paths, table names) are passed at run time; keep
  templates generic.