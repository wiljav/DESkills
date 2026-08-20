"""Scaffold a new skill from templates/skill and register it in catalog.yaml.

Usage: python tools/scaffold_skill.py --domain orchestration --name my-skill \
       [--title "My Skill"] [--category Orchestration] [--catalog catalog.yaml]
"""

from __future__ import annotations

import argparse
import sys

import yaml
from lib import NAME_PATTERN, REPO_ROOT, SKILLS_DIR, load_catalog

CATEGORY_DEFAULTS = {
    "ingestion": "DataIngestion",
    "storage": "StorageAndLakehouse",
    "warehousing": "Warehousing",
    "processing": "DataProcessing",
    "transformation": "DataTransformation",
    "orchestration": "Orchestration",
    "streaming": "Streaming",
    "quality": "DataQuality",
    "governance": "DataGovernance",
    "databases": "Databases",
    "infrastructure": "DataInfrastructure",
    "solutions": "Solutions",
    "platform": "GettingStarted",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--title", default=None)
    parser.add_argument("--category", default=None)
    parser.add_argument("--catalog", default="catalog.yaml")
    args = parser.parse_args()

    if not NAME_PATTERN.match(args.name):
        print(f"FAIL: name '{args.name}' must be kebab-case", file=sys.stderr)
        return 1

    domain_dir = SKILLS_DIR / args.domain
    if not domain_dir.is_dir():
        print(f"FAIL: domain '{args.domain}' does not exist under skills/", file=sys.stderr)
        return 1

    skill_dir = domain_dir / args.name
    if skill_dir.exists():
        print(f"FAIL: {skill_dir} already exists", file=sys.stderr)
        return 1

    category = args.category or CATEGORY_DEFAULTS.get(args.domain)
    if not category:
        msg = f"FAIL: no default category for domain '{args.domain}'; pass --category"
        print(msg, file=sys.stderr)
        return 1

    title = args.title or " ".join(w.capitalize() for w in args.name.split("-"))

    template = (REPO_ROOT / "templates" / "skill" / "SKILL.md.tmpl").read_text(encoding="utf-8")
    rendered = (
        template.replace("{{NAME}}", args.name)
        .replace("{{CATEGORY}}", category)
        .replace("{{TITLE}}", title)
    )

    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "assets").mkdir()
    (skill_dir / "SKILL.md").write_text(rendered, encoding="utf-8")
    for sub in ("references", "scripts", "assets"):
        (skill_dir / sub / ".gitkeep").touch()

    catalog = load_catalog()
    if any(s["id"] == args.name for s in catalog["skills"]):
        print(f"WARN: '{args.name}' already in catalog; not re-adding", file=sys.stderr)
    else:
        catalog["skills"].append(
            {
                "id": args.name,
                "title": title,
                "domain": args.domain,
                "category": category,
                "description": "TODO: one-line summary for the README index.",
            }
        )
        catalog["skills"].sort(key=lambda s: (s["domain"], s["id"]))
        catalog_path = REPO_ROOT / args.catalog
        catalog_path.write_text(
            yaml.safe_dump(catalog, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )

    print(f"OK: scaffolded {skill_dir.relative_to(REPO_ROOT)} (category={category})")
    print("Next: author SKILL.md, add references/, then run 'make ci'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
