"""Assemble and trim agent context from memory files."""

from pathlib import Path
import re

import tiktoken

MAX_MEMORY_TOKENS = 4000
MAX_TOTAL_PROMPT_TOKENS = 12000


def assemble_memory_context(
    repo_root: Path,
    issue_body: str,
    issue_title: str,
) -> str:
    """Build memory context string from PROJECT.md, DECISIONS.md,
    and relevant module memory files."""
    memory_dir = repo_root / ".lotus" / "memory"
    sections: list[str] = []

    # 1. Project memory (highest priority — always full)
    project_mem = memory_dir / "PROJECT.md"
    if project_mem.exists():
        sections.append(project_mem.read_text().strip())

    # 2. Relevant module memory
    modules_dir = memory_dir / "modules"
    if modules_dir.exists():
        relevant = _find_relevant_modules(modules_dir, issue_body, issue_title)
        for mod_file in relevant:
            sections.append(
                f"### Module: {mod_file.stem}\n\n{mod_file.read_text().strip()}"
            )

    # 3. Decision log (lowest priority — last 20 entries)
    decisions = memory_dir / "DECISIONS.md"
    if decisions.exists():
        content = decisions.read_text().strip()
        entries = re.split(r"\n(?=## D\d+)", content)
        if len(entries) > 21:
            entries = entries[:1] + entries[-20:]
            content = "\n".join(entries)
        sections.append(content)

    return "\n\n---\n\n".join(sections)


def _find_relevant_modules(
    modules_dir: Path,
    issue_body: str,
    issue_title: str,
) -> list[Path]:
    """Match module memory files against issue text."""
    combined = f"{issue_title} {issue_body}".lower()
    relevant = []
    for mod_file in sorted(modules_dir.glob("*.md")):
        name = mod_file.stem.lower()
        if name in combined or f"src/{name}" in combined or f"/{name}/" in combined:
            relevant.append(mod_file)
    return relevant


def trim_to_budget(text: str, max_tokens: int = MAX_MEMORY_TOKENS) -> str:
    """Trim text to fit within a token budget.

    Drops sections from the end (lowest priority) first.
    """
    enc = tiktoken.get_encoding("cl100k_base")
    if len(enc.encode(text)) <= max_tokens:
        return text

    sections = text.split("\n\n---\n\n")
    while (
        len(sections) > 1 and len(enc.encode("\n\n---\n\n".join(sections))) > max_tokens
    ):
        sections.pop()

    result = "\n\n---\n\n".join(sections)
    tokens = enc.encode(result)
    if len(tokens) > max_tokens:
        result = enc.decode(tokens[:max_tokens])

    return result


def build_full_prompt(
    system_prompt: str,
    type_prompt: str,
    memory_context: str,
    repo_map: str,
    issue_number: int,
    issue_title: str,
    issue_body: str,
) -> str:
    """Assemble the full agent prompt with token budget enforcement.

    Priority (trimmed last → first):
      1. Issue body (never trimmed)
      2. Type prompt (never trimmed)
      3. System prompt hard rules (never trimmed)
      4. Memory context (trimmed to fit)
      5. Repo map (trimmed to fit)
    """
    enc = tiktoken.get_encoding("cl100k_base")

    # Fixed sections (never trimmed)
    issue_section = f"## Issue #{issue_number}: {issue_title}\n\n{issue_body}"
    fixed = f"{system_prompt}\n\n{type_prompt}\n\n{issue_section}"
    fixed_tokens = len(enc.encode(fixed))

    remaining = MAX_TOTAL_PROMPT_TOKENS - fixed_tokens
    if remaining <= 0:
        return fixed

    # Split remaining budget: 70% memory, 30% repo map
    memory_budget = int(remaining * 0.7)
    map_budget = remaining - memory_budget

    trimmed_memory = trim_to_budget(memory_context, memory_budget)
    trimmed_map = trim_to_budget(repo_map, map_budget)

    return (
        f"{system_prompt}\n\n"
        f"## Project Memory\n\n{trimmed_memory}\n\n"
        f"## Repository Structure\n\n{trimmed_map}\n\n"
        f"{type_prompt}\n\n"
        f"{issue_section}"
    )
