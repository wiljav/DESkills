---
name: terraform-for-data
metadata:
  category: DataInfrastructure
description: >-
  Provisions data-platform infrastructure with Terraform: buckets,
  warehouses, orchestrator, and networking, with state management and
  drift control. Use when standing up or changing platform infrastructure.
  Don't use for application deployment (use ci-cd-for-dbt or k8s
  manifests) or one-off manual console changes (code-first required here).
allowed-tools:
  - terraform
  - aws
  - gcloud
---

# Terraform for Data Platforms

The data platform's cloud resources (storage, warehouses, compute) should
be code: reviewable, repeatable, and auditable. This skill covers the
Terraform patterns for data infrastructure.

## Prerequisites

- Terraform CLI (>= 1.5); provider credentials per the auth skill.
- A backend for state (S3/GCS with locking) and a CI runner (GitHub
  Actions per ci.yml).
- The platform's naming/region conventions documented.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `terraform plan`, `state list`, `state show`.
- **Tier M (mutation)**: `terraform apply` (any resource), `state mv/rm`,
  and destroy operations. Apply changes real infrastructure — plans MUST
  be reviewed; destroy requires explicit confirmation with blast radius.

## Workflow

### 1. Structure the Codebase

```
infra/
  environments/
    dev/        # main.tf, variables.tf, backend.tf
    prod/
  modules/
    bucket/     # reusable storage module
    warehouse/
  main.tf       # shared root (providers, backend)
```

Rules:

- One directory per environment; modules for repeatable resources.
- `backend.tf` pins state + locking; never local state for shared
  environments.

### 2. Provision Storage (S3 example)

```hcl
module "raw_bucket" {
  source = "./modules/bucket"
  name   = "de-raw-{env}"
  region = "us-east-1"
  versioning = true
  lifecycle_rules = [{
    prefix = "logs/"
    days   = 30
  }]
}
```

Rules:

- Versioning ON for data buckets (accidental-delete protection).
- Lifecycle rules for logs/temp prefixes; never for warehouse data.
- Server-side encryption default (KMS or SSE-S3) per the platform policy.

### 3. Provision Warehouse Resources

```hcl
# BigQuery
resource "google_bigquery_dataset" "analytics" {
  dataset_id = "analytics"
  location   = "US"
}

# Snowflake (terraform-provider-snowflake)
resource "snowflake_warehouse" "de_wh" {
  name           = "DE_WH"
  warehouse_size = "X-SMALL"
  auto_suspend   = 60
  auto_resume    = true
}
```

Rules:

- Manage datasets/warehouses/roles in Terraform; table DDL belongs to dbt
  (ci-cd-for-dbt) — clear split: infrastructure vs data.
- Secrets (passwords/tokens) from the secret store; never in `.tf`.

### 4. Review and Apply

```bash
terraform init -backend-config="bucket=de-tfstate-{env}"
terraform plan -out=plan.tfplan     # review the diff
terraform apply plan.tfplan          # confirmed; CI gate
```

- CI applies after plan review (PR-based); prod applies require an extra
  approval step.
- `terraform plan` in CI comments the diff on the PR.

### 5. Handle Drift and Destroy

- Drift check: `terraform plan` on a schedule; reconcile by re-applying or
  importing the drifted resource (`terraform import`) — never both.
- Destroy: list the blast radius (`terraform state list`), confirm with
  the platform owner, then `terraform destroy -target` in stages.

## Validation

- `terraform plan` clean (no unexpected diff) in CI.
- Resources created match the conventions (names, tags, region).
- State backend + locking verified; no uncommitted local state.
- Secrets never appear in plan output or state.

## Definition of Done

- Environment directories + modules structured; state remote with
  locking.
- Storage/warehouse/networking resources code-first; plan review gated in
  CI.
- Drift reconciliation documented; destroy discipline defined.

## Reference Directory

- [State & Backend](references/state-backend.md): remote state, locking,
  and state surgery.
- [Module Patterns](references/module-patterns.md): reusable module
  structure and provider wiring.

## Related Skills

- [CI/CD for dbt](../ci-cd-for-dbt/SKILL.md): the data-layer CI/CD split.
- [Kubernetes for Data Jobs](../k8s-for-data-jobs/SKILL.md): compute
  provisioning.
- [Data Engineering Auth](../../platform/data-engineering-auth/SKILL.md):
  provider credentials.