"""Shared helpers for DE_skills repository tooling."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
CATALOG_PATH = REPO_ROOT / "catalog.yaml"
SCHEMA_PATH = REPO_ROOT / "schema" / "skill.schema.json"
README_PATH = REPO_ROOT / "README.md"

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def load_catalog(path: str | Path | None = None) -> dict:
    """Load catalog.yaml. Requires PyYAML."""
    import yaml

    catalog_path = Path(path) if path else CATALOG_PATH
    with catalog_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict) or "skills" not in data:
        sys.exit("catalog.yaml must define a top-level 'skills' list")
    return data


def iter_skill_dirs() -> list[tuple[Path, str, str]]:
    """Yield (skill_dir, domain, name) for every skill directory on disk."""
    found: list[tuple[Path, str, str]] = []
    if not SKILLS_DIR.exists():
        return found
    for domain_dir in sorted(SKILLS_DIR.iterdir()):
        if not domain_dir.is_dir():
            continue
        for skill_dir in sorted(domain_dir.iterdir()):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                found.append((skill_dir, domain_dir.name, skill_dir.name))
    return found


def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter delimited by leading '---' fences."""
    import yaml

    if not text.startswith("---"):
        sys.exit("SKILL.md must start with a YAML frontmatter block (---)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        sys.exit("SKILL.md frontmatter is not closed (expected closing '---')")
    body = parts[1]
    try:
        return yaml.safe_load(body) or {}
    except yaml.YAMLError as exc:
        sys.exit(f"SKILL.md frontmatter is not valid YAML: {exc}")
