# API & Search

## Search

```bash
curl -s -X POST "http://datahub-gms:8080/api/graphql" \
  -H "Authorization: Bearer ${DATAHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { search(input: {type: DATASET, query: \"orders\"}) { total results { entity { urn } } } }"}'
```

## Lineage

```bash
curl -s -X POST "http://datahub-gms:8080/api/graphql" \
  -H "Authorization: Bearer ${DATAHUB_TOKEN}" \
  -d '{"query": "query { dataset(urn: \"urn:li:dataset:...\") { lineage { downstreamRelationships { entity { urn } } } } }"}'
```

## CLI

```bash
datahub get --urn <urn>                    # entity details
datahub delete --urn <urn> --hard          # destructive; confirmed only
```

## Rules

- API calls in automation use a service token scoped to read (or the
  needed write role).
- Search-first workflow: resolve URNs by name, then read/act on the URN.
- Never hard-delete entities that downstream consumers reference (lineage
  breaks) — soft-delete or fix the source first.
