# ADR Template

```markdown
# ADR-012: Choose Iceberg as the table format

## Status
Accepted (2024-02-01) / Proposed / Superseded by ADR-0xx

## Context
- The platform needed ACID + time travel on object storage.
- Candidates: Iceberg, Delta, Hudi (with Apache-licensed option).
- Requirements: multi-engine access (Spark/Flink/Trino), open standard.

## Decision
- Iceberg with a REST catalog as the platform's table format.
- Reason: open spec, engine-agnostic catalog, best multi-engine story.

## Consequences
- Positive: no vendor lock-in; REST catalog centralizes metadata.
- Negative: maintenance of the catalog service; new team skills.

## Alternatives considered
- Delta: excellent Databricks integration, but catalog coupling.
- Hudi: strong upserts, but heavier ops for the use cases here.
```

## Rules

- One ADR per decision; context MUST include the alternatives rejected.
- Status lifecycle: Proposed -> Accepted -> (Superseded).
- Review cadence: quarterly with the platform review.
