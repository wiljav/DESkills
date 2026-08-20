"""Validate all SKILL.md files against the schema and the catalog registry.

Gates:
- frontmatter is valid YAML and validates against schema/skill.schema.json
- frontmatter 'name' matches the containing directory (kebab-case)
- 'metadata.category' exists in catalog.yaml taxonomy
- registry sync: every skill dir on disk is in catalog.yaml and vice versa
- required body sections present (Prerequisites, Validation, Definition of Done)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema
from lib import (
    CATALOG_PATH,
    NAME_PATTERN,
    REPO_ROOT,
    SCHEMA_PATH,
    iter_skill_dirs,
    load_catalog,
    parse_frontmatter,
)

REQUIRED_BODY_SECTIONS = [
    "Prerequisites",
    "Safety & Confirmation Tiers",
    "Validation",
    "Definition of Done",
]

ERRORS: list[str] = []


def fail(msg: str) -> None:
    ERRORS.append(msg)


def validate_frontmatter(frontmatter: dict, skill_dir: Path, domain: str, schema: dict) -> None:
    name = frontmatter.get("name")
    if not isinstance(name, str) or not NAME_PATTERN.match(name):
        fail(f"{skill_dir.relative_to(REPO_ROOT)}: invalid 'name' (must be kebab-case): {name!r}")
    elif name != skill_dir.name:
        fail(
            f"{skill_dir.relative_to(REPO_ROOT)}: 'name' frontmatter '{name}' "
            f"does not match directory name '{skill_dir.name}'"
        )
    try:
        jsonschema.validate(frontmatter, schema)
    except jsonschema.ValidationError as exc:
        fail(f"{skill_dir.relative_to(REPO_ROOT)}: schema violation: {exc.message}")


def validate_body(skill_dir: Path, text: str) -> None:
    for section in REQUIRED_BODY_SECTIONS:
        if section.lower() not in text.lower():
            fail(
                f"{skill_dir.relative_to(REPO_ROOT)}: missing required body section "
                f"'## {section}' (or variant)"
            )


def check_registry(catalog: dict, on_disk: list[tuple[Path, str, str]]) -> None:
    categories = {c["id"] for c in catalog.get("categories", [])}
    catalog_skills = {s["id"]: s for s in catalog.get("skills", [])}
    disk_keys = {(domain, name) for _, domain, name in on_disk}

    for skill in catalog["skills"]:
        if skill["id"] not in {n for _, _, n in on_disk}:
            fail(f"catalog.yaml lists '{skill['id']}' but no skills/*/*/{skill['id']} exists")
        if skill.get("category") not in categories:
            fail(f"catalog.yaml: '{skill['id']}' has unknown category '{skill.get('category')}'")
        domain = skill.get("domain")
        if domain and (domain, skill["id"]) not in disk_keys:
            fail(f"catalog.yaml: '{skill['id']}' domain '{domain}' does not match on-disk layout")

    for skill_dir, domain, name in on_disk:
        entry = catalog_skills.get(name)
        if entry is None:
            fail(f"{skill_dir.relative_to(REPO_ROOT)}: not listed in catalog.yaml")
            continue
        if entry.get("domain") != domain:
            fail(f"catalog.yaml: '{name}' domain '{entry.get('domain')}' != on-disk '{domain}'")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default=str(CATALOG_PATH), help="path to catalog.yaml")
    args = parser.parse_args()
    catalog = load_catalog(args.catalog)
    with SCHEMA_PATH.open(encoding="utf-8") as fh:
        schema = json.load(fh)

    on_disk = iter_skill_dirs()
    check_registry(catalog, on_disk)

    for skill_dir, domain, _name in on_disk:
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        validate_frontmatter(frontmatter, skill_dir, domain, schema)
        validate_body(skill_dir, text)

        refs_dir = skill_dir / "references"
        if refs_dir.is_dir() and not any(refs_dir.iterdir()):
            fail(f"{skill_dir.relative_to(REPO_ROOT)}: references/ exists but is empty")

    if ERRORS:
        print(f"FAIL: {len(ERRORS)} validation error(s)", file=sys.stderr)
        for err in ERRORS:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"OK: validated {len(on_disk)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
