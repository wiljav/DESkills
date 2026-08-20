# State & Backend

## Remote state with locking

- S3 bucket + DynamoDB lock table (AWS) or GCS (GCP):
  `terraform init -backend-config=...` pins both.
- Locking prevents concurrent applies — CI parallel jobs must share the
  lock (default behavior when configured).

## State surgery

```bash
terraform state list                          # inventory
terraform state show aws_s3_bucket.raw        # inspect one resource
terraform state mv old.module.new_name        # rename/relocate
terraform import aws_s3_bucket.raw de-raw-prod # adopt drifted resource
terraform state rm aws_s3_bucket.legacy       # stop managing (not delete!)
```

Rules:

- `state rm` removes management WITHOUT destroying — only when the
  resource is intentionally unmanaged.
- Backup state (`terraform state pull > backup.tfstate`) before any
  surgery.
- Never hand-edit `.tfstate`; use the commands.

## Secrets in state

- Sensitive values land in state plaintext by default — mark
  `sensitive = true` on variables/attributes and restrict state access.
- Keep state bucket ACL'd to the platform team + CI only.