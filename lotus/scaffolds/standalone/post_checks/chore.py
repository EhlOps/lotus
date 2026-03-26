#!/usr/bin/env python3
"""Post-check: chores must not change application logic."""

import subprocess
import sys
from pathlib import Path

import yaml

LOGIC_EXTENSIONS = {
    "python": (".py",),
    "typescript": (".ts", ".tsx"),
    "rust": (".rs",),
    "go": (".go",),
}

EXCLUDE_PATTERNS = {
    "python": ("test", "spec", "conftest", "setup.py"),
    "typescript": ("test", "spec", ".config."),
    "rust": ("test", "bench"),
    "go": ("_test.go",),
}


def run() -> int:
    config = yaml.safe_load(Path(".lotus/config.yml").read_text())
    lang = config["project"]["language"]

    if lang not in LOGIC_EXTENSIONS:
        print(f"WARN: Unknown language '{lang}', skipping.")
        return 0

    exts = LOGIC_EXTENSIONS[lang]
    excludes = EXCLUDE_PATTERNS[lang]

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

    logic_files = [
        f
        for f in changed
        if any(f.endswith(ext) for ext in exts)
        and not any(exc in f.lower() for exc in excludes)
    ]

    if logic_files:
        print("FAIL: Chore tasks must not modify application logic:")
        for f in logic_files:
            print(f"  {f}")
        return 1

    print("OK: Chore post-check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
