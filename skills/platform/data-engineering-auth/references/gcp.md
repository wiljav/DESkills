# GCP Authentication Patterns

## Application Default Credentials (ADC)

All Google client libraries resolve credentials via ADC. Order of resolution:

1. `GOOGLE_APPLICATION_CREDENTIALS` environment variable (file path).
2. `gcloud auth application-default login` credentials.
3. GCE/GKE metadata service (workload identity).

For local development, prefer:

```bash
gcloud auth application-default login --impersonate-service-account \
  {sa}@{project}.iam.gserviceaccount.com
```

This keeps a personal user token out of the pipeline and tests the exact
service account the job will run as.

## Service account keys: rules

- Keys are **long-lived** and MUST be avoided for scheduled jobs.
- If a key file is unavoidable (some dbt adapters), create it in a temp
  directory, use it for the session, and delete it.
- Never name a key file `credentials.json` in a repo path; `.gitignore`
  patterns exist for `*-key.json` and `service-account*.json`.

## Common failure modes

| Symptom | Cause | Fix |
| --- | --- | --- |
| `PERMISSION_DENIED` on a job the user can run | impersonation missing roles | grant `roles/iam.serviceAccountTokenCreator` + job roles to the impersonator |
| `ADC could not be located` | no login and no env var | run `gcloud auth application-default login` |
| `401 UNAUTHENTICATED` intermittently | expired short-lived token | refresh and re-export before the job |
