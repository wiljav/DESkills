# AWS Authentication Patterns

## Preferred: role assumption with short sessions

Scheduled jobs assume a pipeline role with an explicit session duration:

```bash
aws sts assume-role \
  --role-arn arn:aws:iam::{account}:role/{pipeline-role} \
  --role-session-name de-skill-session \
  --duration-seconds 3600
```

Export the returned values as `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
and `AWS_SESSION_TOKEN` for the job's process only — never persist them.

## Profiles and SSO

For interactive work, use named profiles in `~/.aws/config`:

```ini
[profile data-platform]
sso_session = de-sso
region = us-east-1
```

Authenticate with `aws sso login --profile data-platform` and run jobs with
`AWS_PROFILE=data-platform`. SSO sessions are short-lived by default.

## Least privilege

- Grant data roles (`s3:GetObject`, `glue:GetTable*`, `athena:StartQueryExecution`)
  only on the buckets/tables the pipeline touches.
- Verify effective permissions with `aws iam simulate-principal-policy` before
  running a new pipeline.
- Never place long-lived keys in `~/.aws/credentials` for jobs; prefer
  identity federation (SSO, IAM Roles Anywhere, EKS IRSA).
