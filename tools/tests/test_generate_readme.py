"""Tests for tools/generate_readme.py and check_links.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from check_links import check_file  # noqa: E402
from generate_readme import build_index  # noqa: E402
from lib import load_catalog  # noqa: E402


def test_build_index_lists_all_skills(tmp_path):
    catalog = load_catalog()
    index = build_index(catalog)
    for skill in catalog["skills"]:
        assert f"./skills/{skill['domain']}/{skill['id']}" in index
        assert f"**{skill['title']}**" in index


def test_build_index_grouped_by_category():
    catalog = load_catalog()
    index = build_index(catalog)
    for cat in catalog["categories"]:
        assert cat["title"] in index


def test_check_file_missing_target(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text("[missing](./nope.md)\n[ok](./real.md)\n", encoding="utf-8")
    (tmp_path / "real.md").write_text("x", encoding="utf-8")
    errors = []
    check_file(md, errors)
    assert len(errors) == 1
    assert "nope.md" in errors[0]


def test_check_file_ignores_urls_and_anchors(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text(
        "[web](https://example.com)\n[anchor](#section)\n[mail](mailto:a@b.c)\n",
        encoding="utf-8",
    )
    errors = []
    check_file(md, errors)
    assert errors == []
