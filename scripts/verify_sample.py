#!/usr/bin/env python3
"""
CI Stage 3 — verification sample (Naidu brief / Freyssinet spreadsheet).

Runs the same pytest class used in Stage 2, in-process (no subprocess shell).
"""

import sys

import pytest


def main() -> int:
    return pytest.main(
        [
            "tests/test_checks.py::TestSampleVerification",
            "-v",
            "--tb=short",
        ]
    )


if __name__ == "__main__":
    sys.exit(main())
