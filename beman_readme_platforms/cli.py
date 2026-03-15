# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
"""Command-line interface for beman-readme-platforms."""

import argparse
import sys
from pathlib import Path

from beman_readme_platforms.lib.matrix import extract_matrix_config, read_ci_yaml
from beman_readme_platforms.lib.readme import (
    read_readme,
    replace_supported_platforms,
    write_readme,
)
from beman_readme_platforms.lib.table import generate_table


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate a Markdown supported-platforms table from a Beman CI matrix",
    )

    parser.add_argument(
        "-C",
        "--directory",
        metavar="DIR",
        type=Path,
        default=Path.cwd(),
        help="Repository directory (default: current directory)",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check that the README is already up-to-date; exit 0 if yes, 1 if no",
    )

    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    repo_path = args.directory.resolve()
    if not repo_path.exists():
        print(
            f"Error: Repository directory does not exist: {repo_path}",
            file=sys.stderr,
        )
        return 1

    # Read and parse CI matrix
    try:
        ci_yaml = read_ci_yaml(repo_path)
        matrix_config = extract_matrix_config(ci_yaml)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    table = generate_table(matrix_config)

    # Read README
    try:
        readme_text = read_readme(repo_path)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Generate the updated README
    try:
        updated = replace_supported_platforms(readme_text, table)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.check:
        if readme_text == updated:
            print("README is up-to-date.")
            return 0
        else:
            print("README is out-of-date. Run without --check to update.")
            return 1

    if readme_text == updated:
        print("README is already up-to-date.")
    else:
        write_readme(repo_path, updated)
        print("README updated.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
