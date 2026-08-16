import os
import re

import pytest

from local_repo import cmd_publish_package
from local_repo.cmd_publish_package import (
    DistribPackage,
    package_name_to_dir,
)
from local_test.name_assertion import assert_test_module_name_embeds_another_module_name
from local_test.repo_tree import change_to_known_repo_path


def test_relationship():
    assert_test_module_name_embeds_another_module_name(cmd_publish_package.__name__)


@pytest.mark.parametrize("distrib_package", list(DistribPackage))
def test_pyproject_toml_name_matches_distrib_package(distrib_package):

    # given:

    package_dir = package_name_to_dir[distrib_package.value]
    pyproject_path = os.path.join("src", package_dir, "pyproject.toml")
    with change_to_known_repo_path("."):
        assert os.path.isfile(pyproject_path), f"Missing: {pyproject_path}"
        with open(pyproject_path, "r") as f:
            content = f.read()

    # when:

    match = re.search(r'^name\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.M)

    # then:

    assert match, f"No name field found in {pyproject_path}"
    assert match.group(1) == distrib_package.value, f"{pyproject_path}: name={match.group(1)!r}, expected {distrib_package.value!r}"
