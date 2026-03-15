# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
"""Table generation and consolidation logic."""

from dataclasses import dataclass

# Canonical ordering for compilers, C++ standards, and standard libraries.
COMPILER_ORDER = ["gcc", "clang", "appleclang", "msvc"]

CXX_STANDARDS_ORDER = ["c++26", "c++23", "c++20", "c++17", "c++14", "c++11"]

STDLIB_SORT_KEY = {"libstdc++": 0, "libc++": 1, "stl": 2}

COMPILER_DISPLAY = {
    "gcc": "GCC",
    "clang": "Clang",
    "appleclang": "AppleClang",
    "msvc": "MSVC",
}

STDLIB_DISPLAY = {
    "libstdc++": "libstdc++",
    "libc++": "libc++",
    "stl": "MSVC STL",
}


@dataclass(frozen=True)
class TableRow:
    """A single row of the output table."""

    compiler: str
    versions: list[str]
    cxx_versions: list[str]
    stdlibs: list[str]


def _version_sort_key(v: str) -> tuple[int, int]:
    """Sort key: 'latest' first, then numeric descending, then alpha."""
    if v == "latest":
        return (0, 0)
    try:
        return (1, -int(v))
    except ValueError:
        return (2, 0)


def _can_merge_version(last: str, new: str) -> bool:
    """True if new is numerically one less than last (descending sequence)."""
    try:
        return int(last) - int(new) == 1
    except ValueError:
        return False


# A profile captures the set of (cxx_versions, stdlibs) "config rows" for a
# compiler version, ignoring test types.  Two versions can be merged into a
# single version range iff they share the same profile.
Profile = tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]


def _compute_profile(
    entries: set[tuple[str, str, str, str]], compiler: str, version: str
) -> Profile:
    """Compute the canonical profile for a (compiler, version)."""
    # per_stdlib: stdlib → set of cxxversions
    per_stdlib: dict[str, set[str]] = {}
    for c, v, cxx, stdlib in entries:
        if c == compiler and v == version:
            per_stdlib.setdefault(stdlib, set()).add(cxx)

    # Invert: group stdlibs that share the same cxxversion set
    cxx_to_stdlibs: dict[frozenset[str], list[str]] = {}
    for stdlib, cxx_set in per_stdlib.items():
        key = frozenset(cxx_set)
        cxx_to_stdlibs.setdefault(key, []).append(stdlib)

    # Canonical form: sorted tuple of (sorted cxx_versions, sorted stdlibs)
    # Sort rows: more cxx standards first, then by first stdlib sort key.
    rows_unsorted = [
        (
            tuple(
                sorted(
                    cxx,
                    key=lambda s: (
                        CXX_STANDARDS_ORDER.index(s)
                        if s in CXX_STANDARDS_ORDER
                        else 999
                    ),
                )
            ),
            tuple(sorted(stdlibs, key=lambda s: STDLIB_SORT_KEY.get(s, 999))),
        )
        for cxx, stdlibs in cxx_to_stdlibs.items()
    ]
    profile = tuple(
        sorted(
            rows_unsorted,
            key=lambda r: (-len(r[0]), min(STDLIB_SORT_KEY.get(s, 999) for s in r[1])),
        )
    )
    return profile


def build_table_rows(entries: set[tuple[str, str, str, str]]) -> list[TableRow]:
    """Build consolidated table rows from raw platform entries."""
    # Collect all (compiler, version) pairs and their profiles.
    compilers_seen: dict[str, set[str]] = {}
    for compiler, version, _, _ in entries:
        compilers_seen.setdefault(compiler, set()).add(version)

    profiles: dict[tuple[str, str], Profile] = {}
    for compiler, versions in compilers_seen.items():
        for version in versions:
            profiles[(compiler, version)] = _compute_profile(entries, compiler, version)

    rows: list[TableRow] = []

    for compiler in COMPILER_ORDER:
        if compiler not in compilers_seen:
            continue

        # Sort versions: latest first, then numeric descending
        sorted_versions = sorted(compilers_seen[compiler], key=_version_sort_key)

        # Group consecutive versions sharing the same profile
        groups: list[tuple[list[str], Profile]] = []
        current_versions = [sorted_versions[0]]
        current_profile = profiles[(compiler, sorted_versions[0])]

        for v in sorted_versions[1:]:
            if profiles[(compiler, v)] == current_profile and _can_merge_version(
                current_versions[-1], v
            ):
                current_versions.append(v)
            else:
                groups.append((current_versions, current_profile))
                current_versions = [v]
                current_profile = profiles[(compiler, v)]
        groups.append((current_versions, current_profile))

        # Emit rows for each group
        for versions, profile in groups:
            for cxx_versions, stdlibs in profile:
                rows.append(
                    TableRow(
                        compiler=compiler,
                        versions=list(versions),
                        cxx_versions=list(cxx_versions),
                        stdlibs=list(stdlibs),
                    )
                )

    return rows


def _format_version_range(versions: list[str]) -> str:
    """Format a version list as a range or comma-separated list."""
    if len(versions) == 1:
        return versions[0]
    try:
        nums = sorted([int(v) for v in versions], reverse=True)
        if all(nums[i] - nums[i + 1] == 1 for i in range(len(nums) - 1)):
            return f"{nums[0]}-{nums[-1]}"
    except ValueError:
        pass
    return ", ".join(versions)


def _format_cxx_range(standards: list[str]) -> str:
    """Format C++ standards as a range (if >2 consecutive) or comma-separated."""
    sorted_stds = sorted(
        standards,
        key=lambda s: CXX_STANDARDS_ORDER.index(s) if s in CXX_STANDARDS_ORDER else 999,
    )
    display = [s.replace("c++", "C++") for s in sorted_stds]

    if len(display) > 2:
        indices = [
            CXX_STANDARDS_ORDER.index(s)
            for s in sorted_stds
            if s in CXX_STANDARDS_ORDER
        ]
        if len(indices) == len(sorted_stds) and all(
            indices[i + 1] == indices[i] + 1 for i in range(len(indices) - 1)
        ):
            return f"{display[0]}-{display[-1]}"

    return ", ".join(display)


def _format_stdlibs(stdlibs: list[str]) -> str:
    """Format stdlib list with display names."""
    return ", ".join(STDLIB_DISPLAY.get(s, s) for s in stdlibs)


def render_table(rows: list[TableRow]) -> str:
    """Render table rows as a Markdown table string."""
    # Compute display values for each row
    display_rows: list[tuple[str, str, str, str]] = []
    for row in rows:
        display_rows.append(
            (
                COMPILER_DISPLAY.get(row.compiler, row.compiler),
                _format_version_range(row.versions),
                _format_cxx_range(row.cxx_versions),
                _format_stdlibs(row.stdlibs),
            )
        )

    # Compute column widths
    headers = ("Compiler", "Version", "C++ Standards", "Standard Library")
    widths = [len(h) for h in headers]
    for dr in display_rows:
        for i, cell in enumerate(dr):
            widths[i] = max(widths[i], len(cell))

    def _fmt_row(cells: tuple[str, ...]) -> str:
        return "| " + " | ".join(c.ljust(widths[i]) for i, c in enumerate(cells)) + " |"

    lines = [
        _fmt_row(headers),
        "|" + "|".join("-" * (w + 2) for w in widths) + "|",
    ]
    for dr in display_rows:
        lines.append(_fmt_row(dr))

    return "\n".join(lines)


def generate_table(matrix_config: dict) -> str:
    """End-to-end: matrix config dict → Markdown table string."""
    from beman_readme_platforms.lib.matrix import extract_platform_entries

    entries = extract_platform_entries(matrix_config)
    rows = build_table_rows(entries)
    return render_table(rows)
