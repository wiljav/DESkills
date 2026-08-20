# Evaluation Rubric

## Scoring template

| Requirement | Weight (must=3, should=2, nice=1) | DataHub | OpenMetadata | Atlan | Amundsen | Marquez |
| --- | --- | --- | --- | --- | --- | --- |
| Column-level lineage | | | | | | |
| OpenLineage support | | | | | | |
| Quality integration | | | | | | |
| Contracts | | | | | | |
| Glossary/ownership | | | | | | |
| SSO/RBAC | | | | | | |
| Ops burden (lower=better) | | | | | | |

Score each cell 0-3 (0=absent, 3=excellent). Weighted total = sum(weight
x cell score).

## POC checklist

- [ ] Ingest one core domain (schema + lineage + ownership)
- [ ] Search finds the dataset; schema correct
- [ ] Lineage walk: upstream source -> downstream dashboards
- [ ] Quality results (GE/dbt) visible
- [ ] RBAC: analyst role cannot edit metadata
- [ ] Two weeks of daily use by the pilot team

## Decision rules

- Weighted score gap < 10%: pick the lower-ops option.
- Any must-have scored 0 is an automatic reject.
- Prefer OpenLineage-compatible tools — lock-in protection.