"""Tests for tools/validate_marketplace.py."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validate_marketplace import MIN_SCHEMA, validate_manifest  # noqa: E402


def _write(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "marketplace.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_valid_manifest(tmp_path):
    path = _write(
        tmp_path,
        {
            "name": "de-plugins",
            "owner": {"name": "Example"},
            "metadata": {"version": "0.0.1"},
            "plugins": [
                {
                    "name": "spark",
                    "source": {"source": "github", "repo": "org/repo", "ref": "v1"},
                    "description": "d",
                }
            ],
        },
    )
    errors = validate_manifest(path, MIN_SCHEMA[".claude-plugin/marketplace.json"])
    assert errors == []


def test_missing_required_fields(tmp_path):
    path = _write(tmp_path, {"name": "x"})
    errors = validate_manifest(path, MIN_SCHEMA[".claude-plugin/marketplace.json"])
    assert any("missing required field" in e for e in errors)


def test_duplicate_plugins(tmp_path):
    path = _write(
        tmp_path,
        {
            "name": "de-plugins",
            "owner": {"name": "Example"},
            "metadata": {"version": "0.0.1"},
            "plugins": [
                {"name": "spark", "source": {"source": "github"}, "description": "d"},
                {"name": "spark", "source": {"source": "github"}, "description": "d"},
            ],
        },
    )
    errors = validate_manifest(path, MIN_SCHEMA[".claude-plugin/marketplace.json"])
    assert any("duplicate plugin name" in e for e in errors)
