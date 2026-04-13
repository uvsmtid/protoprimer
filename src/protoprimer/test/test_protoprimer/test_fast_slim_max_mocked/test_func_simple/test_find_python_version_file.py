import os
import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    find_python_version_file,
    ConfConstGeneral,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        find_python_version_file.__name__,
    )


def test_finds_version_file_in_current_dir(fs):
    """
    Tests that `find_python_version_file` finds the `.python-version` file in the current directory.
    """

    # given:

    # A fake filesystem with the version file in the current directory.
    current_dir = "/project/src"

    fs.create_dir(current_dir)

    version_file_path = os.path.join(current_dir, ConfConstGeneral.python_version_file_basename)
    fs.create_file(version_file_path, contents="3.9.5")

    # when:

    # The current working directory is where the file is.
    os.chdir(current_dir)
    result_path = find_python_version_file(".")

    # then:
    assert result_path == version_file_path


def test_finds_version_file_in_parent_dir(fs):
    """
    Tests that `find_python_version_file` walks up the tree to find the file.
    """

    # given:

    # A fake filesystem with the version file in a parent directory:
    parent_dir = "/project"

    child_dir = os.path.join(parent_dir, "src", "app")
    fs.create_dir(child_dir)

    version_file_path = os.path.join(parent_dir, ConfConstGeneral.python_version_file_basename)
    fs.create_file(version_file_path, contents="3.8.10")

    # when:

    # The search starts from a deep subdirectory:
    result_path = find_python_version_file(child_dir)

    # then:
    assert result_path == version_file_path


def test_finds_version_file_at_root(fs):
    """
    Tests that `find_python_version_file` can find the file at the filesystem root.
    """

    # given:

    # The version file is in the root directory:
    deep_dir = "/a/b/c/d/e"
    fs.create_dir(deep_dir)

    version_file_path = os.path.join("/", ConfConstGeneral.python_version_file_basename)
    fs.create_file(version_file_path, contents="3.7.0")

    # when:

    result_path = find_python_version_file(deep_dir)

    # then:

    assert result_path == version_file_path


def test_returns_none_when_no_file_exists(fs):
    """
    Tests that `find_python_version_file` returns `None` if the file is not found.
    """

    # given:

    # A fake filesystem without any `.python-version` file:
    some_dir = "/project/no-version-file"
    fs.create_dir(some_dir)

    # when:
    result_path = find_python_version_file(some_dir)

    # then:
    assert result_path is None


def test_finds_closest_version_file(fs):
    """
    Tests that `find_python_version_file` returns the path to the nearest `.python-version` file.
    """

    # given:

    # Two version files, one in the current directory and one in a parent:
    parent_dir = "/project"

    current_dir = os.path.join(parent_dir, "src")
    fs.create_dir(current_dir)

    parent_version_file = os.path.join(parent_dir, ConfConstGeneral.python_version_file_basename)
    fs.create_file(parent_version_file, contents="3.9.0")

    child_version_file = os.path.join(current_dir, ConfConstGeneral.python_version_file_basename)
    fs.create_file(child_version_file, contents="3.10.0")

    # when:

    # The search starts from the directory containing the "child" version file:
    result_path = find_python_version_file(current_dir)

    # then:
    # It should find the one in the current directory, not the parent:
    assert result_path == child_version_file
