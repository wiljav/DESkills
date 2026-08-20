"""Validate plugin marketplace manifests (.claude-plugin, .agents)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lib import REPO_ROOT

MANIFESTS = [
    REPO_ROOT / ".claude-plugin" / "marketplace.json",
    REPO_ROOT / ".agents" / "plugins" / "marketplace.json",
]

MIN_SCHEMA = {
    ".claude-plugin/marketplace.json": {
        "required": ["name", "owner", "metadata", "plugins"],
        "plugin_fields": ["name", "source", "description"],
    },
    ".agents/plugins/marketplace.json": {
        "required": ["name", "owner", "metadata", "plugins"],
        "plugin_fields": ["name", "source", "description"],
    },
}


def validate_manifest(path: Path, spec: dict) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return errors
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.name}: invalid JSON: {exc}"]

    for field in spec["required"]:
        if field not in data:
            errors.append(f"{path.name}: missing required field '{field}'")

    plugins = data.get("plugins", [])
    seen: set[str] = set()
    for plugin in plugins:
        for field in spec["plugin_fields"]:
            if field not in plugin:
                errors.append(f"{path.name}: plugin missing '{field}': {plugin}")
        name = plugin.get("name")
        if name in seen:
            errors.append(f"{path.name}: duplicate plugin name '{name}'")
        seen.add(name)
        source = plugin.get("source", {})
        if isinstance(source, dict) and source.get("source") not in (None, "github"):
            errors.append(f"{path.name}: plugin '{name}' has unsupported source type")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(REPO_ROOT))
    args = parser.parse_args()
    root = Path(args.root)

    errors: list[str] = []
    checked = 0
    for rel, spec in MIN_SCHEMA.items():
        path = root / rel
        if not path.exists():
            continue
        checked += 1
        errors.extend(validate_manifest(path, spec))

    if errors:
        print(f"FAIL: {len(errors)} marketplace error(s)", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"OK: {checked} marketplace manifest(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
