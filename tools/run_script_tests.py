"""Discover and run every *_test.py inside skills/*/*/scripts/.

Each skill script test is run in a subprocess so a failing skill cannot
poison the tooling test session.
"""

from __future__ import annotations

import subprocess
import sys

from lib import SKILLS_DIR


def main() -> int:
    tests = sorted(SKILLS_DIR.glob("*/*/scripts/*_test.py"))
    if not tests:
        print("OK: no skill script tests found")
        return 0

    failures = 0
    for test in tests:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test), "-q"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failures += 1
            print(f"FAIL: {test.relative_to(SKILLS_DIR.parent)}")
            print(result.stdout[-2000:])
            print(result.stderr[-2000:])
        else:
            print(f"PASS: {test.relative_to(SKILLS_DIR.parent)}")

    if failures:
        print(f"FAIL: {failures} skill script test suite(s) failed", file=sys.stderr)
        return 1
    print(f"OK: {len(tests)} skill script test suite(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
