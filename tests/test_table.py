# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
"""Tests for table generation and consolidation."""

from beman_readme_platforms.lib.matrix import extract_platform_entries
from beman_readme_platforms.lib.table import (
    build_table_rows,
    generate_table,
    _format_version_range,
    _format_cxx_range,
)


class TestFormatVersionRange:
    def test_single(self):
        assert _format_version_range(["15"]) == "15"

    def test_consecutive(self):
        assert _format_version_range(["15", "14", "13"]) == "15-13"

    def test_two_consecutive(self):
        assert _format_version_range(["12", "11"]) == "12-11"

    def test_non_consecutive(self):
        assert _format_version_range(["15", "13"]) == "15, 13"

    def test_latest(self):
        assert _format_version_range(["latest"]) == "latest"


class TestFormatCxxRange:
    def test_single(self):
        assert _format_cxx_range(["c++26"]) == "C++26"

    def test_two(self):
        assert _format_cxx_range(["c++20", "c++17"]) == "C++20, C++17"

    def test_three_consecutive(self):
        assert _format_cxx_range(["c++26", "c++23", "c++20"]) == "C++26-C++20"

    def test_four_consecutive(self):
        assert _format_cxx_range(["c++26", "c++23", "c++20", "c++17"]) == "C++26-C++17"

    def test_non_consecutive(self):
        assert _format_cxx_range(["c++26", "c++20", "c++17"]) == "C++26, C++20, C++17"


class TestBuildTableRows:
    def test_simple(self, simple_matrix):
        entries = extract_platform_entries(simple_matrix)
        rows = build_table_rows(entries)
        assert len(rows) == 1
        assert rows[0].compiler == "gcc"
        assert rows[0].versions == ["15"]
        assert rows[0].cxx_versions == ["c++26"]
        assert rows[0].stdlibs == ["libstdc++"]

    def test_exemplar(self, exemplar_matrix):
        entries = extract_platform_entries(exemplar_matrix)
        rows = build_table_rows(entries)

        # Expected rows:
        # GCC 15-13: C++26-C++17, libstdc++
        # GCC 12-11: C++23-C++17, libstdc++
        # Clang 21-19: C++26-C++17, libstdc++, libc++
        # Clang 18-17: C++26-C++17, libc++
        # Clang 18-17: C++20, C++17, libstdc++
        # AppleClang latest: C++26-C++17, libc++
        # MSVC latest: C++23, stl
        assert len(rows) == 7

        # Check GCC rows
        gcc_rows = [r for r in rows if r.compiler == "gcc"]
        assert len(gcc_rows) == 2
        assert gcc_rows[0].versions == ["15", "14", "13"]
        assert gcc_rows[1].versions == ["12", "11"]

        # Check Clang rows
        clang_rows = [r for r in rows if r.compiler == "clang"]
        assert len(clang_rows) == 3
        assert clang_rows[0].versions == ["21", "20", "19"]
        assert clang_rows[0].stdlibs == ["libstdc++", "libc++"]

        # Check AppleClang
        ac_rows = [r for r in rows if r.compiler == "appleclang"]
        assert len(ac_rows) == 1
        assert ac_rows[0].versions == ["latest"]

        # Check MSVC
        msvc_rows = [r for r in rows if r.compiler == "msvc"]
        assert len(msvc_rows) == 1
        assert msvc_rows[0].stdlibs == ["stl"]


class TestRenderTable:
    def test_exemplar_output(self, exemplar_matrix):
        table = generate_table(exemplar_matrix)
        lines = table.split("\n")

        # Header + separator + 7 data rows
        assert len(lines) == 9

        # Check header
        assert "Compiler" in lines[0]
        assert "Version" in lines[0]
        assert "C++ Standards" in lines[0]
        assert "Standard Library" in lines[0]

        # Check separator is dashes
        assert all(c in "-|" for c in lines[1])

        # Check specific content
        assert "GCC" in lines[2]
        assert "15-13" in lines[2]
        assert "MSVC" in lines[8]
        assert "MSVC STL" in lines[8]


class TestEndToEnd:
    def test_deterministic(self, exemplar_matrix):
        """Table generation must be deterministic."""
        t1 = generate_table(exemplar_matrix)
        t2 = generate_table(exemplar_matrix)
        assert t1 == t2
