"""
Tests of `find_breaking_api_changes` itself (not a contract test): additions must pass, removals must fail.

FT_78_72_23_04.backward_compatibility.md
"""

import pathlib

import pytest

from local_test.case_condition import requires_max_python
from local_test.griffe_helper import find_breaking_api_changes
from local_test.name_assertion import assert_test_module_name_embeds_str

old_source = """
import enum

def func_a(a, b=1): ...

class ClassA:
    def method_a(self, x): ...

class EnumA(enum.Enum):
    VALUE_A = "a"
"""

# Everything old is still there, plus more (the compatible case):
additive_source = """
import enum

def func_a(a, b=1, c=2): ...

def func_new(): ...

class ClassA:
    def method_a(self, x, y=None): ...
    def method_new(self): ...

class ClassNew: ...

class EnumA(enum.Enum):
    VALUE_A = "a"
    VALUE_B = "b"
"""


def create_tree(root_dir_abs_path: pathlib.Path, source: str) -> pathlib.Path:
    package_dir_abs_path = root_dir_abs_path / "some_pkg"
    package_dir_abs_path.mkdir(parents=True)
    (package_dir_abs_path / "__init__.py").write_text(source)
    return root_dir_abs_path


def test_relationship():
    assert_test_module_name_embeds_str("find_breaking_api_changes")


@requires_max_python
def test_same_tree_has_no_breaking_changes(tmp_path: pathlib.Path):
    old_root_dir_abs_path = create_tree(tmp_path / "old", old_source)
    assert find_breaking_api_changes("some_pkg", old_root_dir_abs_path, old_root_dir_abs_path) == []


@requires_max_python
def test_additions_are_not_breaking(tmp_path: pathlib.Path):
    old_root_dir_abs_path = create_tree(tmp_path / "old", old_source)
    new_root_dir_abs_path = create_tree(tmp_path / "new", additive_source)
    assert find_breaking_api_changes("some_pkg", old_root_dir_abs_path, new_root_dir_abs_path) == []


@requires_max_python
@pytest.mark.parametrize(
    "new_source, expected_path",
    [
        (old_source.replace("def func_a(a, b=1): ...", ""), "some_pkg.func_a"),
        (old_source.replace("class ClassA:", "class ClassRenamed:"), "some_pkg.ClassA"),
        (old_source.replace("def method_a(self, x)", "def method_a(self, x, req)"), "some_pkg.ClassA.method_a"),
    ],
)
def test_removals_and_changes_are_breaking(
    tmp_path: pathlib.Path,
    new_source: str,
    expected_path: str,
):
    old_root_dir_abs_path = create_tree(tmp_path / "old", old_source)
    new_root_dir_abs_path = create_tree(tmp_path / "new", new_source)
    breaking_changes = find_breaking_api_changes("some_pkg", old_root_dir_abs_path, new_root_dir_abs_path)
    assert any(breaking_change.startswith(expected_path) for breaking_change in breaking_changes), breaking_changes
