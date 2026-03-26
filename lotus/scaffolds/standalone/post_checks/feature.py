#!/usr/bin/env python3
"""Post-check: features should be additive with tests.

Standalone — no lotus imports. Only stdlib + pyyaml.
"""

import subprocess
import sys


def run() -> int:
    diff = subprocess.run(
        ["git", "diff", "main", "--numstat"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    if not diff:
        print("WARN: No files changed.")
        return 0

    existing_changed = 0
    new_files = 0

    for line in diff.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        filepath = parts[2]
        result = subprocess.run(
            ["git", "cat-file", "-t", f"main:{filepath}"],
            capture_output=True,
        )
        if result.returncode == 0:
            existing_changed += 1
        else:
            new_files += 1

    total = existing_changed + new_files
    if total > 3 and existing_changed / total > 0.7:
        print(
            f"WARN: {existing_changed}/{total} changed files are existing code. "
            "Features should prefer adding new files."
        )

    # Hard check: tests must be in the diff
    changed_files = subprocess.run(
        ["git", "diff", "main", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.lower()

    if "test" not in changed_files:
        print("FAIL: No test files added or modified. Features require tests.")
        return 1

    print(
        f"OK: Feature post-check passed. {new_files} new, {existing_changed} existing."
    )
    return 0


if __name__ == "__main__":
    sys.exit(run())
