#!/usr/bin/env python3
"""Post-check: bugfixes need regression tests, minimal logic diff."""

import subprocess
import sys


def run() -> int:
    changed = (
        subprocess.run(
            ["git", "diff", "main", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        .stdout.strip()
        .splitlines()
    )

    test_changes = sum(1 for f in changed if "test" in f.lower() or "spec" in f.lower())
    if test_changes == 0:
        print("FAIL: No test files changed. Bugfixes require a regression test.")
        return 1

    numstat = subprocess.run(
        ["git", "diff", "main", "--numstat", "--", ":!*test*", ":!*spec*"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    logic_lines = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            logic_lines += int(parts[0]) + int(parts[1])

    if logic_lines > 100:
        print(
            f"WARN: {logic_lines} lines changed in non-test files. Bugfixes should be surgical."
        )

    print(
        f"OK: Bugfix post-check passed. {test_changes} test file(s), {logic_lines} logic lines."
    )
    return 0


if __name__ == "__main__":
    sys.exit(run())
