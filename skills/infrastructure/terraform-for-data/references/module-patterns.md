# Module Patterns

## Module shape

```
modules/bucket/
  main.tf        # resource definitions
  variables.tf   # inputs with defaults + validation
  outputs.tf     # what consumers need (arn, name)
  versions.tf    # provider version pinning
```

## Rules

- One responsibility per module (bucket, warehouse, network, roles).
- Validate inputs (`validation { condition = ... }`) — catch typos at
  plan time, not apply time.
- Output only what consumers use; keep modules self-contained (no hidden
  dependencies on the caller's resources).

## Provider wiring

```hcl
# root main.tf
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
    google = { source = "hashicorp/google", version = "~> 5.0" }
  }
}
```

- Pin provider major versions; run `terraform providers lock` to record
  checksums.
- Pass credentials via the provider's standard env vars / workload
  identity — never static keys in `.tf` files.