#!/usr/bin/env python3
"""
scripts/verify_sample.py — CI Stage 3
=====================================
Runs only TestSampleVerification — proves the tool matches the assessment brief.
Run manually: python scripts/verify_sample.py
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
