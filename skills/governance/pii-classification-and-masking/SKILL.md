---
name: pii-classification-and-masking
metadata:
  category: DataGovernance
description: >-
  Identifies PII in datasets, classifies sensitivity, and applies masking,
  tokenization, or encryption for compliance. Use when handling personal
  data in pipelines or designing access controls. Don't use for general
  security hardening (out of scope) or for row-level policy on the
  warehouse itself (handled by the warehouse RBAC).
allowed-tools:
  - python
  - sql
---

# PII Classification and Masking

Personal data needs classification and protection. This skill covers
detecting PII, classifying sensitivity, and applying the right protection
(masking/tokenization/encryption) at the right layer.

## Prerequisites

- A compliance framework to follow (GDPR/CCPA/org policy) — this skill
  implements protection, not policy definition.
- Access to the datasets under review (read-only for classification).
- The warehouse/processing layer where protections will apply.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: scanning datasets for PII patterns, reading
  classification reports, reviewing masking configs.
- **Tier M (mutation)**: applying masks/tokenization, changing table
  schemas for encryption, and deleting raw PII. Protection changes alter
  what consumers see — confirm per dataset with the owner (per
  data-contracts).

## Workflow

### 1. Scan and Classify

```python
import re

PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\+?[0-9][0-9 \-]{8,}"),
    "ssn":   re.compile(r"\d{3}-\d{2}-\d{4}"),
    "ip":    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

def classify(df, sample=10_000):
    found = {col: set() for col in df.columns}
    for col in df.columns:
        for val in df[col].head(sample):
            for kind, rx in PII_PATTERNS.items():
                if rx.fullmatch(str(val)):
                    found[col].add(kind)
    return found
```

Rules:

- Sample + pattern match to FIND candidates; manual review to CONFIRM
  (patterns over/under-match).
- Classify columns, then the dataset: sensitivity = max of its columns.

### 2. Assign Sensitivity

| Level | Example | Required protection |
| --- | --- | --- |
| public | product catalog | none |
| internal | sales aggregations | none (access-controlled) |
| confidential | customer records | masking/tokenization for non-owner roles |
| restricted | SSN, health data | encryption at rest + tokenization + audit |

### 3. Apply Protections

Masking (warehouse layer, SQL):

```sql
-- Redshift/BigQuery style: last-4 visible
CREATE OR REPLACE VIEW analytics.customer_masked AS
SELECT customer_id,
       CONCAT(SUBSTRING(email, 1, 2), '***@', SPLIT_PART(email, '@', 2)) AS email,
       CONCAT('****-****-****-', RIGHT(card_number, 4)) AS card_number
FROM analytics.customer_raw;
```

Tokenization (processing layer):

```python
# map to token at ingest; raw kept encrypted, never in serving tables
df["customer_id_token"] = df["customer_id"].map(tokenizer.tokenize)
```

Rules:

- Mask in the SERVING layer (views/marts), not in source ingestion —
  preserve raw for reprocessing.
- Tokenize once, consistently, per dataset (deterministic token mapping
  preserves joins).
- Never log PII: redact in logs from the start.

### 4. Verify and Document

- Data contract gets a `pii`/`sensitivity` field per dataset
  (data-contracts).
- Test: the masked view exposes no raw values (`SELECT` check + regex
  scan of sample).
- Access: roles that may see raw PII are named in the catalog (ownership
  in datahub-catalog).

## Validation

- Classification report reviewed; sensitivity assigned per dataset.
- Masking/tokenization applied at the serving layer; raw values absent
  from consumer-visible outputs.
- No PII in logs or metadata tooling (scan run as a check).
- Contract + catalog updated with sensitivity and owners.

## Definition of Done

- Datasets classified with a documented sensitivity level.
- Protections applied per level and verified (no raw values in serving
  outputs).
- Access to raw PII limited to named roles; audit trail exists.
- Contracts/catalog carry the sensitivity metadata.

## Reference Directory

- [Patterns Catalog](references/patterns.md): common PII patterns and
  false-positive notes.
- [Protection Matrix](references/protection-matrix.md): mask vs tokenize vs
  encrypt, by sensitivity and layer.

## Related Skills

- [Data Contracts](../data-contracts/SKILL.md): sensitivity belongs in the
  contract.
- [DataHub Catalog](../datahub-catalog/SKILL.md): ownership/tags for PII
  datasets.
- [Data Engineering Auth](../../platform/data-engineering-auth/SKILL.md):
  the access controls around protected data.