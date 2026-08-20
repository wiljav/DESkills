"""Validate internal relative markdown links inside skills/.

Checks that every relative link (./x.md, ../x.md, x.md) found in markdown
files under skills/ resolves to an existing file. Absolute URLs and anchors
(#...) are skipped.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from lib import REPO_ROOT

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def collect_md_files(root: Path) -> list[Path]:
    return sorted((root / "skills").rglob("*.md"))


def check_file(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    try:
        rel = path.relative_to(REPO_ROOT)
    except ValueError:
        rel = path
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        if "|" in target:  # markdown destination with title
            target = target.split("|", 1)[0]
        bare = target.split("#", 1)[0]
        if not bare:
            continue
        resolved = (path.parent / bare).resolve()
        if not resolved.exists():
            errors.append(f"{rel}: link target does not exist: {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(REPO_ROOT))
    args = parser.parse_args()
    root = Path(args.root)

    errors: list[str] = []
    files = collect_md_files(root)
    for path in files:
        check_file(path, errors)

    if errors:
        print(f"FAIL: {len(errors)} broken link(s)", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"OK: {len(files)} markdown files, no broken links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
