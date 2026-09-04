---
name: object-storage-basics
metadata:
  category: StorageAndLakehouse
description: >-
  Designs buckets, prefixes, lifecycle policies, and security for object
  storage (S3, GCS): naming, tiers, versioning, and access control. Use when
  creating or reorganizing the storage layer of a data platform. Don't use
  for table-format concerns (use iceberg-basics or delta-lake-basics) or
  file-level ingestion (use file-ingestion-gcs-s3).
allowed-tools:
  - gcloud
  - aws
  - gsutil
  - python
---

# Object Storage Basics

Object storage (S3, GCS, Azure Blob) is the lakehouse foundation. This skill
covers the design decisions that prevent cost, performance, and security
problems later.

## Prerequisites

- Cloud account access with storage permissions per the auth skill.
- Knowledge of the data platform's zones and retention requirements
  (raw/intermediate/curated).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `gsutil ls`, `aws s3 ls`, lifecycle previews,
  bucket policy reads.
- **Tier M (mutation)**: creating buckets, setting lifecycle rules, version
  deletion, and policy changes. Bucket deletion is irreversible and MUST be
  confirmed with the bucket's contents reviewed.

## Workflow

### 1. Design the Bucket Layout

Rules:

- One bucket per environment per domain is usually enough; separate buckets
  for code/artifacts vs data.
- Follow the zone layout: `raw/`, `intermediate/`, `curated/` (see
  data-platform-architecture) inside the data bucket.
- Bucket names are globally unique: `{org}-{env}-{domain}-data`.

```bash
gsutil mb -l {region} -b on gs://{org}-{env}-{domain}-data
aws s3api create-bucket --bucket {org}-{env}-{domain}-data --region {region}
```

### 2. Configure Versioning and Retention

- Versioning: enable on buckets holding mutable pipeline data (protects
  against overwrite accidents).
- Retention: object lock / retention policy for compliance-mandated data.
- Never rely on versioning alone for long-term archives — lifecycle rules
  (step 3) do that.

```bash
gsutil versioning set on gs://{bucket}
aws s3api put-bucket-versioning --bucket {bucket} --versioning-configuration Status=Enabled
```

### 3. Define Lifecycle Policies

Typical pattern (cost control):

| Path | Action | Age |
| --- | --- | --- |
| `curated/*` | move to nearline/infrequent-access | 30d |
| `raw/*` | move to coldline/glacier | 90d |
| `raw/*` | delete | 365d |

```bash
# GCS lifecycle JSON
gsutil lifecycle set lifecycle.json gs://{bucket}
# AWS
aws s3api put-bucket-lifecycle-configuration --bucket {bucket} --lifecycle-configuration file://lifecycle.json
```

Rules:

- Lifecycle actions on prefixes, not blanket bucket rules.
- Never auto-delete `curated/` — curate the retention decision with data
  owners first.

### 4. Secure Access

- IAM/service roles over access keys; workloads assume roles (see auth).
- Bucket policies: least privilege per zone; block public access.
- Encrypt at rest (KMS) and in transit (TLS) — default on modern clouds.

```bash
aws s3api put-public-access-block --bucket {bucket} --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### 5. Verify and Document

- `gsutil du -sh gs://{bucket}/raw` / `aws s3 ls --summarize` — record
  baseline sizes.
- Write the layout + lifecycle + ownership into the platform docs (or this
  skill's reference for the team).

## Validation

- Buckets exist with the designed layout; versioning enabled where planned.
- Lifecycle rules listed and scoped to the intended prefixes.
- Public access blocked; encryption confirmed (`--get-encryption`).
- Baseline sizes recorded for cost tracking.

## Definition of Done

- Bucket layout designed and created per the zone model.
- Versioning/retention and lifecycle policies configured and verified.
- Access is least-privilege, non-public, encrypted.
- Ownership and layout documented.

## Reference Directory

- [Storage Classes & Tiers](references/storage-classes.md): when each tier
  pays off.
- [Cost & Performance](references/cost-performance.md): request pricing,
  prefix design, and transfer patterns.

## Related Skills

- [File Ingestion (GCS/S3)](../../ingestion/file-ingestion-gcs-s3/SKILL.md):
  the load patterns that use this layout.
- [Iceberg Basics](../iceberg-basics/SKILL.md) and
  [Delta Lake Basics](../delta-lake-basics/SKILL.md): table formats on top.
- [Data Platform Architecture](../../solutions/data-platform-architecture/SKILL.md):
  the zone model this layout follows.
