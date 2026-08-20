"""Generate the README skill index from catalog.yaml.

The index is written between the <!-- BEGIN SKILLS --> and <!-- END SKILLS -->
markers in README.md. Use --check to verify the index is up to date (CI gate).
"""

from __future__ import annotations

import argparse
import sys

from lib import README_PATH, load_catalog

BEGIN = "<!-- BEGIN SKILLS -->"
END = "<!-- END SKILLS -->"


def build_index(catalog: dict) -> str:
    categories = {c["id"]: c for c in catalog.get("categories", [])}
    by_category: dict[str, list[dict]] = {}
    for skill in catalog["skills"]:
        by_category.setdefault(skill["category"], []).append(skill)

    lines: list[str] = []
    for cat_id in sorted(by_category, key=lambda c: categories.get(c, {}).get("title", c)):
        title = categories.get(cat_id, {}).get("title", cat_id)
        lines.append(f"- **{title}**")
        for skill in sorted(by_category[cat_id], key=lambda s: s["id"]):
            lines.append(
                f"  - [**{skill['title']}**](./skills/{skill['domain']}/{skill['id']}): "
                f"{skill['description']}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default="catalog.yaml")
    parser.add_argument(
        "--check", action="store_true", help="fail if the README index is stale"
    )
    args = parser.parse_args()

    catalog = load_catalog()
    index = build_index(catalog)

    readme = README_PATH.read_text(encoding="utf-8")
    if BEGIN not in readme or END not in readme:
        print(f"FAIL: README.md is missing {BEGIN}/{END} markers", file=sys.stderr)
        return 1

    head, rest = readme.split(BEGIN, 1)
    _mid, tail = rest.split(END, 1)
    new_readme = f"{head}{BEGIN}\n{index}{END}{tail}"

    if args.check:
        if new_readme != readme:
            print("FAIL: README index is stale; run 'make docs'", file=sys.stderr)
            return 1
        print("OK: README index is up to date")
        return 0

    README_PATH.write_text(new_readme, encoding="utf-8")
    print(f"OK: regenerated README index ({len(catalog['skills'])} skills)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
