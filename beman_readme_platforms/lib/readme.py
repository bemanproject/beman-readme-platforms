# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
"""README section replacement logic."""

import re
from pathlib import Path

# Matches any Markdown heading (# … ######).
_HEADING_RE = re.compile(r"^(#{1,6})\s")

_SECTION_HEADING = "### Supported Platforms"


def _heading_level(line: str) -> int | None:
    """Return the heading level (1-6) or None if not a heading."""
    m = _HEADING_RE.match(line)
    return len(m.group(1)) if m else None


def replace_supported_platforms(readme_text: str, table: str) -> str:
    """Replace the 'Supported Platforms' section body with the given table.

    Preserves the heading itself.  The section ends at the next heading of
    equal or higher level (fewer or equal '#' characters), or at EOF.
    """
    lines = readme_text.split("\n")

    # Find the heading line
    heading_idx: int | None = None
    for i, line in enumerate(lines):
        if line.strip() == _SECTION_HEADING:
            heading_idx = i
            break

    if heading_idx is None:
        raise ValueError(f"README does not contain a '{_SECTION_HEADING}' heading")

    heading_level = _heading_level(lines[heading_idx])
    assert heading_level is not None

    # Find the end of the section (next heading at same or higher level)
    end_idx = len(lines)
    for i in range(heading_idx + 1, len(lines)):
        level = _heading_level(lines[i])
        if level is not None and level <= heading_level:
            end_idx = i
            break

    # Build replacement: heading, blank line, table, blank line
    new_section = [lines[heading_idx], "", table, ""]

    result_lines = lines[:heading_idx] + new_section + lines[end_idx:]
    return "\n".join(result_lines)


def read_readme(repo_path: Path) -> str:
    """Read the README.md from a repository."""
    readme_path = repo_path / "README.md"
    if not readme_path.exists():
        raise FileNotFoundError(f"README not found: {readme_path}")
    return readme_path.read_text()


def write_readme(repo_path: Path, content: str) -> None:
    """Write updated content to README.md."""
    readme_path = repo_path / "README.md"
    readme_path.write_text(content)
