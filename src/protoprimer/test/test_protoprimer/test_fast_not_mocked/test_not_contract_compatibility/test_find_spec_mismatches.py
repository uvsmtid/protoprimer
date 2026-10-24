"""
Tests of `find_spec_mismatches` itself (not a contract test): extras must pass, missing or changed must fail.

FT_78_72_23_04.backward_compatibility.md
"""

import argparse

from local_test.cli_spec_helper import find_spec_mismatches
from local_test.name_assertion import assert_test_module_name_embeds_str


def test_relationship():
    assert_test_module_name_embeds_str("find_spec_mismatches")


def test_same_values_match():
    assert find_spec_mismatches({"a": 1}, argparse.Namespace(a=1)) == []


def test_extra_actual_attributes_are_not_mismatches():
    assert find_spec_mismatches({"a": 1}, argparse.Namespace(a=1, new_option="x")) == []


def test_missing_actual_attribute_is_a_mismatch():
    assert len(find_spec_mismatches({"a": 1}, argparse.Namespace(b=1))) == 1


def test_changed_actual_value_is_a_mismatch():
    assert len(find_spec_mismatches({"a": 1}, argparse.Namespace(a=2))) == 1
