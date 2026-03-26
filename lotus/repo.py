"""Resolve repository metadata from git remote."""

import re
import subprocess
from dataclasses import dataclass


@dataclass
class RepoInfo:
    owner: str
    name: str
    full_name: str  # owner/name
    default_branch: str
    has_commits: bool


def get_repo_info() -> RepoInfo:
    """Parse the current git repo's GitHub remote and branch state."""
    # Get remote URL
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "No git remote 'origin' found. "
            "Run this inside a git repo with a GitHub remote."
        )

    remote_url = result.stdout.strip()

    # Parse owner/name from HTTPS or SSH URL
    patterns = [
        r"github\.com[:/](?P<owner>[^/]+)/(?P<name>[^/.]+?)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, remote_url)
        if match:
            owner = match.group("owner")
            name = match.group("name")
            break
    else:
        raise RuntimeError(
            f"Could not parse GitHub owner/repo from remote: {remote_url}"
        )

    # Check for default branch
    branch_result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        capture_output=True,
    )
    has_commits = branch_result.returncode == 0

    # Get default branch name
    if has_commits:
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True,
        )
        default_branch = branch_result.stdout.strip() or "main"
    else:
        default_branch = "main"

    return RepoInfo(
        owner=owner,
        name=name,
        full_name=f"{owner}/{name}",
        default_branch=default_branch,
        has_commits=has_commits,
    )