import os
import re

import pytest

from local_repo import cmd_publish_package
from local_repo.cmd_publish_package import (
    DistribPackage,
    PACKAGE_NAME_TO_DIR,
)
from local_test.name_assertion import assert_test_module_name_embeds_another_module_name
from local_test.repo_tree import change_to_known_repo_path


def test_relationship():
    assert_test_module_name_embeds_another_module_name(cmd_publish_package.__name__)


@pytest.mark.parametrize("distrib_package", list(DistribPackage))
def test_distrib_package_has_dir_mapping(distrib_package):
    """Every DistribPackage value must have an entry in PACKAGE_NAME_TO_DIR."""
    assert distrib_package.value in PACKAGE_NAME_TO_DIR, f"{distrib_package} value {distrib_package.value!r} missing from PACKAGE_NAME_TO_DIR"


@pytest.mark.parametrize("distrib_package", list(DistribPackage))
def test_pyproject_toml_name_matches_distrib_package(distrib_package):
    """pyproject.toml name field must match the DistribPackage enum value."""
    package_dir = PACKAGE_NAME_TO_DIR[distrib_package.value]
    with change_to_known_repo_path("."):
        pyproject_path = os.path.join("src", package_dir, "pyproject.toml")
        assert os.path.isfile(pyproject_path), f"Missing: {pyproject_path}"
        with open(pyproject_path, "r") as f:
            content = f.read()
    match = re.search(r'^name\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.M)
    assert match, f"No name field found in {pyproject_path}"
    assert match.group(1) == distrib_package.value, f"{pyproject_path}: name={match.group(1)!r}, expected {distrib_package.value!r}"
