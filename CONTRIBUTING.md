# Contributing to Data Engineering Agent Skills

Thanks for contributing. Every skill in this repository must pass the quality
gates enforced by [CI](.github/workflows/ci.yml). This checklist is the contract.

## Adding or editing a skill

1. Create the skill under `skills/<domain>/<skill-name>/` using the scaffolder
    to guarantee a valid skeleton:

    ```bash
    make scaffold DOMAIN=orchestration NAME=airflow-dag-authoring
    ```

2. Author `SKILL.md` following the [skill authoring guide](docs/skill-authoring-guide.md).

3. Update the registry (`catalog.yaml`) with the new skill so it appears in the
    generated README index.

4. Run the local validation pipeline — **all gates must pass**:

    ```bash
    make ci
    ```

## Definition of Done (every skill)

- [ ] Frontmatter validates against `schema/skill.schema.json`:
  `name` (kebab-case, unique), `metadata.category` (from taxonomy),
  `description` with `Use when` / `Don't use when` clauses, `allowed-tools`.
- [ ] Body contains: **Prerequisites**, **Safety & confirmation tiers**,
  **numbered workflow phases** (MUST/SHOULD), **Validation** section, and
  **Definition of Done** section.
- [ ] `references/` has at least one topic doc; every internal relative link
  resolves (link-check gate).
- [ ] Any `scripts/` files include `requirements.txt` and a `*_test.py`; all
  scripts pass `ruff` and `pytest`.
- [ ] `assets/` contains only templates — no secrets, no real credentials.
- [ ] Skill appears in the generated README index (no drift).
- [ ] Related Skills cross-links resolve to real sibling skills.

## CI pipeline

| Stage | What it checks |
| --- | --- |
| validate | frontmatter schema, naming, registry ↔ filesystem sync |
| lint | markdownlint + ruff |
| test | pytest for tools and all skill scripts |
| links | internal relative links |
| readme | generated index is up to date |
| marketplace | plugin manifests valid |
| security | gitleaks secret scan |

Run the full pipeline locally with `make ci` or individual targets with
`make validate lint test links readme marketplace`.
