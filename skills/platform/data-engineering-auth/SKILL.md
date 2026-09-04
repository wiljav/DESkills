---
name: data-engineering-auth
metadata:
  category: GettingStarted
description: >-
  Configures cloud and toolchain credentials for data engineering using
  short-lived, scoped access (workload identity, IAM short-lived tokens, and
  credential files that are never committed). Use when a pipeline skill or
  script fails with authentication or permission errors. Don't use for
  rotating user passwords or for fixing application-level OAuth flows.
allowed-tools:
  - gcloud
  - aws
  - az
  - python
---

# Data Engineering Authentication

This skill establishes the authentication foundation for every cloud-backed
skill in this repository: cloud CLI logins, short-lived scoped tokens, and
environment variables that scripts read without storing secrets on disk.

## Prerequisites

- Cloud CLIs installed: `gcloud`, `aws`, and/or `az` depending on the target
  platform.
- A user identity with permission to request scoped credentials
  (`roles/iam.serviceAccountTokenCreator` on GCP, `sts:AssumeRole` on AWS).
- No existing `~/.aws/credentials` or `credentials.json` files that the agent
  is expected to modify without confirmation.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `gcloud auth list`, `aws sts get-caller-identity`,
  `az account show`, and verifying existing tokens.
- **Tier M (mutation)**: starting interactive logins, creating service
  accounts, granting IAM roles, and writing credentials to the filesystem.
  Every mutation MUST be confirmed by the user; never reuse an existing
  credential outside its documented scope.

## Workflow

### 1. Inventory Existing Credentials

Identify what is already available without printing any secret material:

```bash
gcloud auth list --filter=status:ACTIVE --format="value(account)"
aws sts get-caller-identity 2>/dev/null || echo "aws: not authenticated"
az account show --query "{name:name, tenant:tenantId}" -o tsv 2>/dev/null || echo "az: not authenticated"
```

### 2. Request Short-Lived Scoped Credentials

Prefer identity federation over long-lived keys.

On GCP, generate a short-lived access token scoped to the task at hand:

```bash
gcloud auth print-access-token
```

For service-account impersonation (the recommended pattern for jobs):

```bash
gcloud auth application-default login --impersonate-service-account \
  {sa}@{project}.iam.gserviceaccount.com
```

On AWS, use role assumption with an explicit session duration:

```bash
aws sts assume-role --role-arn arn:aws:iam::{account}:role/{pipeline-role} \
  --role-session-name de-skill-session --duration-seconds 3600
```

On Azure, use `az login` with the least-privilege scope requested by the
pipeline.

### 3. Provide Credentials to Scripts Securely

This repository's scripts read credentials from environment variables only.
Never write secrets into `SKILL.md`, assets, or config files.

```bash
export AWS_PROFILE={profile}        # short-lived profile
export GOOGLE_APPLICATION_CREDENTIALS=  # left empty; ADC resolves via impersonation
export DBT_ENV_SECRET_TYPE=env_var  # dbt uses env secrets
```

If a tool requires a JSON credential file (e.g. dbt BigQuery adapter), create
it in the session temp directory, scope it to the project, and delete it when
the task completes:

```bash
CRED_FILE=$(mktemp -d)/sa.json
gcloud iam service-accounts keys create "$CRED_FILE" \
  --iam-account {sa}@{project}.iam.gserviceaccount.com
# ... run the pipeline with GOOGLE_APPLICATION_CREDENTIALS="$CRED_FILE"
rm -rf "$(dirname "$CRED_FILE")"
```

### 4. Validate Access Before Running Pipelines

Every cloud-backed script MUST verify identity before touching data:

```bash
gcloud auth list --filter=status:ACTIVE --format="value(account)"
bq ls --project_id {project} --max_results 1   # if BigQuery is the target
```

## Validation

- `gcloud auth list`, `aws sts get-caller-identity`, or `az account show`
  returns the intended identity without errors.
- The impersonated/scoped identity has only the roles the pipeline needs
  (verify with `gcloud iam list-grantable-roles` or AWS IAM `get-role`).
- No secret material was written into the repository; a final `grep` for
  `BEGIN .* PRIVATE KEY` and `aws_secret_access_key` over changed files finds
  nothing.

## Definition of Done

- The correct scoped identity is active for the target cloud.
- Credentials used are short-lived (token expiry documented to the user).
- All repository scripts run without authentication errors.
- No long-lived keys were created; no secrets were committed.
- Temporary credential files were removed when the task completed.

## Reference Directory

- [GCP Authentication Patterns](references/gcp.md): ADC, impersonation, and
  key hygiene.
- [AWS Authentication Patterns](references/aws.md): profiles, roles, and
  session duration guidance.
- [Credential Hygiene](references/hygiene.md): detection and cleanup of leaked
  or overly-broad credentials.

## Related Skills

- [Data Engineering Stack Setup](../de-stack-getting-started/SKILL.md):
  bootstrap the toolchain that uses these credentials.
- [Data Platform Architecture](../../solutions/data-platform-architecture/SKILL.md):
  how identity is designed across platform components.
