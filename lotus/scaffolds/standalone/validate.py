#!/usr/bin/env python3
"""Lotus validation runner. Runs standard checks + type-specific post-check.

Usage: python .lotus/validate.py <issue_type>

Standalone script — no lotus package imports.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml


def main(issue_type: str) -> int:
    config = yaml.safe_load(Path(".lotus/config.yml").read_text())
    commands = config["commands"]
    failed = False

    # Standard checks
    checks = [
        ("Format", f"{commands['format']} --check"),
        ("Lint", commands["lint"]),
    ]
    if commands.get("typecheck"):
        checks.append(("Typecheck", commands["typecheck"]))
    checks.append(("Test", commands["test"]))

    for name, cmd in checks:
        print(f"\n{'=' * 3} {name} {'=' * 3}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            print(f"FAIL: {name}")
            failed = True

    # Type-specific post-check
    post_check_name = config["issue_types"][issue_type]["post_check"]
    post_check_path = Path(f".lotus/post-checks/{post_check_name}.py")

    if post_check_path.exists():
        print(f"\n{'=' * 3} Post-Check ({issue_type}) {'=' * 3}")
        spec = importlib.util.spec_from_file_location("post_check", post_check_path)
        try:
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec for {post_check_path}")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if mod.run() != 0:
                failed = True
        except Exception as e:
            print(f"FAIL: Post-check error: {e}")
            failed = True
    else:
        print(f"WARN: No post-check found at {post_check_path}")

    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python .lotus/validate.py <issue_type>")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
