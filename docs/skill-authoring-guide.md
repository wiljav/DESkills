# Skill Authoring Guide

Every `SKILL.md` in this repository is a machine-validated instruction manual
for an AI agent. The frontmatter tells the agent *when* to use the skill; the
body tells it *how* to do the job safely and verifiably.

## Frontmatter contract

Validated against `schema/skill.schema.json`:

| Field | Rules |
| --- | --- |
| `name` | kebab-case, must equal the containing directory name |
| `metadata.category` | must exist in `catalog.yaml` categories |
| `description` | >= 40 chars; include a `Use when` and a `Don't use when` clause |
| `allowed-tools` | unique list of CLI tools/runtimes the skill may invoke |

## Body contract

Required sections (checked by `make validate`):

1.  **Prerequisites** — environment, versions, credentials, and prior skills
    the agent must confirm before starting.
2.  **Safety & Confirmation Tiers** — split actions into:
    - `Tier R` (read-only): run without confirmation.
    - `Tier M` (mutation): creating resources, running destructive SQL
      (`--full-refresh`, `DROP`, `TRUNCATE`), deploying — requires explicit
      user confirmation, with cost/blast-radius warnings.
3.  **Workflow** — numbered phases using MUST/SHOULD language, concrete
    commands, expected outputs, and failure branches.
4.  **Validation** — how to prove the work succeeded (pass criteria).
5.  **Definition of Done** — checklist that must all be true before the agent
    concludes.
6.  **Reference Directory** — links into `references/`.
7.  **Related Skills** — cross-links to sibling skills.

## Writing conventions

- Commands must be copy-paste runnable; parameterize with `{placeholders}`.
- Never hardcode credentials; point to the auth skill.
- Reference product documentation only via stable URLs.
- Keep `references/` files focused: one topic per file (e.g. `core-concepts.md`,
  `cli-usage.md`, `failure-signatures.md`).

## Scripts

- Any script in `scripts/` needs `requirements.txt` and a `*_test.py` test
  file; both must pass `ruff` and `pytest`.
- Scripts must default to read-only behavior. Mutating operations require a
  `--apply`-style flag gated by user confirmation (see Safety tiers).
- Never commit secrets; use environment variables with `os.environ` lookups.

## Assets

- `assets/` holds templates only: DAGs, dbt projects, Terraform, compose files.
- No real credentials, keys, or private data in assets.

## Checklist before submitting

Run `make ci`. It must pass every gate: validate, lint, test, links, readme,
marketplace.