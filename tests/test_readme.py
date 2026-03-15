# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
"""Tests for README section replacement."""

import pytest

from beman_readme_platforms.lib.readme import replace_supported_platforms


SAMPLE_README = """\
# My Project

Some intro text.

## Usage

Use it like this.

### Supported Platforms

Old content here.
More old content.

## Development

Dev instructions.
"""

TABLE = """\
| Compiler | Version | C++ Standards | Standard Library |
|----------|---------|---------------|------------------|
| GCC      | 15      | C++26         | libstdc++        |"""


class TestReplaceSupportedPlatforms:
    def test_replaces_section(self):
        result = replace_supported_platforms(SAMPLE_README, TABLE)
        assert "### Supported Platforms" in result
        assert TABLE in result
        assert "Old content here." not in result
        assert "More old content." not in result

    def test_preserves_surrounding(self):
        result = replace_supported_platforms(SAMPLE_README, TABLE)
        assert "# My Project" in result
        assert "Some intro text." in result
        assert "## Usage" in result
        assert "## Development" in result
        assert "Dev instructions." in result

    def test_idempotent(self):
        first = replace_supported_platforms(SAMPLE_README, TABLE)
        second = replace_supported_platforms(first, TABLE)
        assert first == second

    def test_missing_heading(self):
        with pytest.raises(ValueError, match="does not contain"):
            replace_supported_platforms("# Just a README\n", TABLE)

    def test_section_at_end_of_file(self):
        readme = """\
# Project

### Supported Platforms

Old stuff.
"""
        result = replace_supported_platforms(readme, TABLE)
        assert TABLE in result
        assert "Old stuff." not in result
