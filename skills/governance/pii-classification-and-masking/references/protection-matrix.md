# Protection Matrix

## By layer

| Layer | Technique | Preserves joins/analytics |
| --- | --- | --- |
| Serving (views/marts) | masking, row-level policy | masked values only |
| Processing | tokenization (deterministic) | yes, joins preserved |
| Storage/ingest | encryption at rest | yes (transparent) |
| Logs/events | redaction | n/a |

## Mask vs tokenize vs encrypt

| | Mask | Tokenize | Encrypt |
| --- | --- | --- | --- |
| Reversible | no (partial) | yes (with token map) | yes (with key) |
| Analytics on value | partial (last-4) | no (random-looking) | no |
| Cost | low | medium (map storage) | medium (key mgmt) |
| Use | serving layer | cross-system stable ID | at-rest protection |

## Rules

- Never mask in the ingestion/source layer — it destroys the ability to
  reprocess.
- Tokenize with a deterministic algorithm (e.g. HMAC-SHA256 over a
  secret) so the same raw value always maps to the same token.
- Encrypt at rest on the raw store; masking alone is NOT sufficient for
  restricted data.
- Document per dataset which technique applies (contract field
  `protection: mask|tokenize|encrypt`).