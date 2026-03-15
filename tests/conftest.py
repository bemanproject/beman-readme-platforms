# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
"""Shared pytest fixtures."""

import pytest


@pytest.fixture
def exemplar_matrix():
    """Matrix config matching the exemplar ci_tests.yml."""
    return {
        "gcc": [
            {
                "versions": ["15"],
                "tests": [
                    {
                        "cxxversions": ["c++26"],
                        "tests": [
                            {
                                "stdlibs": ["libstdc++"],
                                "tests": [
                                    "Debug.Default",
                                    "Release.Default",
                                    "Release.TSan",
                                    "Release.MaxSan",
                                    "Debug.Werror",
                                    "Debug.Coverage",
                                ],
                            }
                        ],
                    },
                    {
                        "cxxversions": ["c++23", "c++20", "c++17"],
                        "tests": [
                            {"stdlibs": ["libstdc++"], "tests": ["Release.Default"]}
                        ],
                    },
                ],
            },
            {
                "versions": ["14", "13"],
                "tests": [
                    {
                        "cxxversions": ["c++26", "c++23", "c++20", "c++17"],
                        "tests": [
                            {"stdlibs": ["libstdc++"], "tests": ["Release.Default"]}
                        ],
                    }
                ],
            },
            {
                "versions": ["12", "11"],
                "tests": [
                    {
                        "cxxversions": ["c++23", "c++20", "c++17"],
                        "tests": [
                            {"stdlibs": ["libstdc++"], "tests": ["Release.Default"]}
                        ],
                    }
                ],
            },
        ],
        "clang": [
            {
                "versions": ["21"],
                "tests": [
                    {
                        "cxxversions": ["c++26"],
                        "tests": [
                            {
                                "stdlibs": ["libstdc++", "libc++"],
                                "tests": [
                                    "Debug.Default",
                                    "Release.Default",
                                    "Release.TSan",
                                    "Release.MaxSan",
                                    "Debug.Werror",
                                ],
                            }
                        ],
                    },
                    {
                        "cxxversions": ["c++23", "c++20", "c++17"],
                        "tests": [
                            {
                                "stdlibs": ["libstdc++", "libc++"],
                                "tests": ["Release.Default"],
                            }
                        ],
                    },
                ],
            },
            {
                "versions": ["20", "19"],
                "tests": [
                    {
                        "cxxversions": ["c++26", "c++23", "c++20", "c++17"],
                        "tests": [
                            {
                                "stdlibs": ["libstdc++", "libc++"],
                                "tests": ["Release.Default"],
                            }
                        ],
                    }
                ],
            },
            {
                "versions": ["18", "17"],
                "tests": [
                    {
                        "cxxversions": ["c++26", "c++23", "c++20", "c++17"],
                        "tests": [
                            {"stdlibs": ["libc++"], "tests": ["Release.Default"]}
                        ],
                    },
                    {
                        "cxxversions": ["c++20", "c++17"],
                        "tests": [
                            {"stdlibs": ["libstdc++"], "tests": ["Release.Default"]}
                        ],
                    },
                ],
            },
        ],
        "appleclang": [
            {
                "versions": ["latest"],
                "tests": [
                    {
                        "cxxversions": ["c++26", "c++23", "c++20", "c++17"],
                        "tests": [
                            {"stdlibs": ["libc++"], "tests": ["Release.Default"]}
                        ],
                    }
                ],
            }
        ],
        "msvc": [
            {
                "versions": ["latest"],
                "tests": [
                    {
                        "cxxversions": ["c++23"],
                        "tests": [
                            {
                                "stdlibs": ["stl"],
                                "tests": [
                                    "Debug.Default",
                                    "Release.Default",
                                    "Release.MaxSan",
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }


@pytest.fixture
def simple_matrix():
    """Minimal matrix for unit tests."""
    return {
        "gcc": [
            {
                "versions": ["15"],
                "tests": [
                    {
                        "cxxversions": ["c++26"],
                        "tests": [
                            {
                                "stdlibs": ["libstdc++"],
                                "tests": ["Debug.Default"],
                            }
                        ],
                    }
                ],
            }
        ]
    }
