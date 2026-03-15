# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
"""CI matrix parsing and extraction."""

import json
from pathlib import Path

import yaml


def read_ci_yaml(repo_path: Path) -> dict:
    """Read and parse the ci_tests.yml file."""
    ci_yaml_path = repo_path / ".github" / "workflows" / "ci_tests.yml"
    if not ci_yaml_path.exists():
        raise FileNotFoundError(f"CI YAML not found: {ci_yaml_path}")

    with open(ci_yaml_path, "r") as f:
        return yaml.safe_load(f)


def extract_matrix_config(ci_yaml: dict) -> dict:
    """Extract the matrix_config JSON from the build-and-test job."""
    jobs = ci_yaml.get("jobs", {})
    build_and_test = jobs.get("build-and-test", {})
    with_params = build_and_test.get("with", {})
    matrix_config_str = with_params.get("matrix_config", "")

    if not matrix_config_str:
        raise ValueError("No matrix_config found in build-and-test job")

    return json.loads(matrix_config_str.strip())


def extract_platform_entries(matrix_config: dict) -> set[tuple[str, str, str, str]]:
    """Extract unique (compiler, version, cxxversion, stdlib) tuples from the matrix.

    Includes all compilers (gcc, clang, appleclang, msvc, etc.).
    Test types are ignored.
    """
    entries: set[tuple[str, str, str, str]] = set()
    for compiler, compiler_groups in matrix_config.items():
        for group in compiler_groups:
            for version in group["versions"]:
                for test_group in group["tests"]:
                    for cxxversion in test_group["cxxversions"]:
                        for stdlib_test in test_group["tests"]:
                            for stdlib in stdlib_test["stdlibs"]:
                                entries.add((compiler, version, cxxversion, stdlib))
    return entries
