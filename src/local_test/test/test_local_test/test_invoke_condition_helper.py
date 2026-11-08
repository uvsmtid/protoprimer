"""
Keep `InvokeCondition` registry, the doc and the test files in sync.

FT_64_09_03_66.invoke_condition.md
"""

import pathlib
import re

from local_test.invoke_condition_helper import (
    InvokeCondition,
    get_repo_root_abs_path,
    not_covered,
)

_doc_rel_path = "doc/feature_topic/FT_64_09_03_66.invoke_condition.md"
_test_dir_rel_path = "src/protoprimer/test/test_protoprimer/test_invoke_condition"


def _read_doc_table() -> dict:
    doc_text = (get_repo_root_abs_path() / _doc_rel_path).read_text()
    table = {}
    for table_match in re.finditer(r"(?m)^\| (\d+)\s*\| `([a-z_]+)`\s*\| ([A-Z]+)\s*\|$", doc_text):
        table[table_match.group(2)] = (int(table_match.group(1)), table_match.group(3))
    return table


def test_enum_matches_doc_table():
    doc_table = _read_doc_table()
    assert {condition.name: condition.value for condition in InvokeCondition} == {title: number for title, (number, _) in doc_table.items()}


def test_doc_status_matches_scenario_heading():
    doc_text = (get_repo_root_abs_path() / _doc_rel_path).read_text()
    for title, (_, status) in _read_doc_table().items():
        assert f"### {status}: `{title}`" in doc_text


def test_enum_numbers_are_sequential():
    assert [condition.value for condition in InvokeCondition] == list(range(1, len(InvokeCondition) + 1))


def test_every_scenario_has_test_file_or_documented_reason():
    test_dir = get_repo_root_abs_path() / _test_dir_rel_path
    known_basenames = {condition.test_file_basename for condition in InvokeCondition}
    actual_basenames = {path.name for path in test_dir.glob("test_invoke_condition_*.py")}
    # No test file for an unknown scenario:
    assert actual_basenames <= known_basenames
    covered = {condition for condition in InvokeCondition if condition.test_file_basename in actual_basenames}
    # Each scenario is either covered or has a reason (but not both):
    assert covered.isdisjoint(not_covered.keys())
    assert covered | set(not_covered.keys()) == set(InvokeCondition)
