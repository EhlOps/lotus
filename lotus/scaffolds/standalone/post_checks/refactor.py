#!/usr/bin/env python3
"""Post-check: refactors must not touch tests or increase complexity."""

import subprocess
import sys
from pathlib import Path

import yaml


def run() -> int:
    config = yaml.safe_load(Path(".lotus/config.yml").read_text())
    lang = config["project"]["language"]

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

    # Hard: no test modifications
    test_files = [f for f in changed if "test" in f.lower() or "spec" in f.lower()]
    if test_files:
        print("FAIL: Refactors must not modify test files:")
        for f in test_files:
            print(f"  {f}")
        return 1

    # Complexity check (Python only for now)
    if lang == "python":
        source_files = [
            f
            for f in changed
            if f.endswith(".py") and "test" not in f.lower() and "spec" not in f.lower()
        ]
        if source_files and _check_complexity(source_files) != 0:
            return 1

    # Net line count
    numstat = subprocess.run(
        ["git", "diff", "main", "--numstat", "--", ":!*test*", ":!*spec*"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    added = removed = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            added += int(parts[0])
            removed += int(parts[1])
    net = added - removed

    if net > 10:
        print(f"WARN: Net +{net} lines. Refactors should shrink the codebase.")

    print(f"OK: Refactor post-check passed. Net {net:+d} lines.")
    return 0


def _check_complexity(files: list[str]) -> int:
    try:
        after = subprocess.run(
            ["radon", "cc", "-a", "-nc", *files],
            capture_output=True,
            text=True,
        ).stdout
        after_cc = _parse_avg(after)

        subprocess.run(["git", "stash", "-q"], check=True)
        for f in files:
            subprocess.run(["git", "checkout", "main", "--", f], capture_output=True)

        before = subprocess.run(
            ["radon", "cc", "-a", "-nc", *files],
            capture_output=True,
            text=True,
        ).stdout
        before_cc = _parse_avg(before)

        subprocess.run(["git", "stash", "pop", "-q"], capture_output=True)

        print(f"Complexity: {before_cc:.2f} → {after_cc:.2f}")
        if after_cc > before_cc:
            print(f"FAIL: Complexity increased ({before_cc:.2f} → {after_cc:.2f}).")
            return 1
    except Exception as e:
        print(f"WARN: Could not measure complexity: {e}")
    return 0


def _parse_avg(output: str) -> float:
    for line in output.splitlines():
        if "Average complexity" in line:
            try:
                return float(line.split("(")[-1].rstrip(")"))
            except (ValueError, IndexError):
                pass
    return 0.0


if __name__ == "__main__":
    sys.exit(run())
