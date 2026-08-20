"""Tests for tools/lib.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import NAME_PATTERN, load_catalog  # noqa: E402


def test_name_pattern_valid():
    assert NAME_PATTERN.match("kafka-basics")
    assert NAME_PATTERN.match("dbt-core")
    assert NAME_PATTERN.match("a1")


def test_name_pattern_invalid():
    assert not NAME_PATTERN.match("KafkaBasics")
    assert not NAME_PATTERN.match("kafka_basics")
    assert not NAME_PATTERN.match("-kafka")
    assert not NAME_PATTERN.match("kafka-")


def test_load_catalog_has_skills():
    catalog = load_catalog()
    assert isinstance(catalog["skills"], list)
    assert len(catalog["skills"]) > 0
    assert {"id", "title", "domain", "category", "description"} <= set(catalog["skills"][0])


def test_load_catalog_categories_unique():
    catalog = load_catalog()
    ids = [c["id"] for c in catalog["categories"]]
    assert len(ids) == len(set(ids))
