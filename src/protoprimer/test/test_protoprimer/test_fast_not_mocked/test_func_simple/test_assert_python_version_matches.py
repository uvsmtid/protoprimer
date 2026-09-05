from __future__ import annotations

import sys

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import assert_python_version_matches


def test_relationship():
    assert_test_module_name_embeds_str(
        assert_python_version_matches.__name__,
    )


def test_assert_python_version_matches_when_major_minor_prefix_satisfied():
    # given:
    major, minor, _patch = sys.version_info[:3]

    # when/then: does not raise
    assert_python_version_matches(sys.executable, f"{major}.{minor}")


def test_assert_python_version_matches_when_exact_version_satisfied():
    # given:
    major, minor, patch = sys.version_info[:3]

    # when/then: does not raise
    assert_python_version_matches(sys.executable, f"{major}.{minor}.{patch}")


def test_assert_python_version_matches_when_minor_mismatch():
    # given:
    major, minor, _patch = sys.version_info[:3]
    mismatched_minor = minor + 1

    # when/then:
    with pytest.raises(AssertionError):
        assert_python_version_matches(sys.executable, f"{major}.{mismatched_minor}")


def test_assert_python_version_matches_when_patch_mismatch():
    # given:
    major, minor, patch = sys.version_info[:3]
    mismatched_patch = patch + 1

    # when/then:
    with pytest.raises(AssertionError):
        assert_python_version_matches(sys.executable, f"{major}.{minor}.{mismatched_patch}")
