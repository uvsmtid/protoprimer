import os
import re
import subprocess

import pytest

from local_repo import cmd_publish_package
from local_repo.cmd_publish_package import (
    DistribPackage,
    find_protected_branch_containing_head,
    package_name_to_dir,
    parse_support_branch_names,
    re_dev_version,
    re_local_version,
    re_release_version,
)
from local_test.name_assertion import assert_test_module_name_embeds_another_module_name
from local_test.repo_tree import change_to_known_repo_path


def test_relationship():
    assert_test_module_name_embeds_another_module_name(cmd_publish_package.__name__)


@pytest.mark.parametrize(
    "version",
    [
        "1.2.3.dev4",
        "1.2.3.dev4+org",
        "0.13.0.dev2+org",
    ],
)
def test_re_dev_version_matches(version):
    assert re.match(re_dev_version, version), f"Expected match: {version!r}"


@pytest.mark.parametrize(
    "version",
    [
        "1.2.3",
        "1.2.3+org",
        "1.2.3.final",
        "1.2.3.dev4.extra",
    ],
)
def test_re_dev_version_no_match(version):
    assert not re.match(re_dev_version, version), f"Expected no match: {version!r}"


@pytest.mark.parametrize(
    "version",
    [
        "1.2.3+org",
        "0.13.0+org",
    ],
)
def test_re_local_version_matches(version):
    assert re.match(re_local_version, version), f"Expected match: {version!r}"


@pytest.mark.parametrize(
    "version",
    [
        "1.2.3",
        "1.2.3.dev4",
        "1.2.3.dev4+org",
    ],
)
def test_re_local_version_no_match(version):
    assert not re.match(re_local_version, version), f"Expected no match: {version!r}"


@pytest.mark.parametrize(
    "version",
    [
        "1.2.3",
        "0.13.0",
    ],
)
def test_re_release_version_matches(version):
    assert re.match(re_release_version, version), f"Expected match: {version!r}"


@pytest.mark.parametrize(
    "version",
    [
        "1.2.3.dev4",
        "1.2.3+org",
        "1.2.3.dev4+org",
        "1.2.3.final",
    ],
)
def test_re_release_version_no_match(version):
    assert not re.match(re_release_version, version), f"Expected no match: {version!r}"


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


def test_parse_support_branch_names():
    """
    FT_60_28_38_74.compatibility_maintenance.md: `support-*` branches are protected as well as `main`.
    """

    # given:

    remote_branch_list_output = "  origin/HEAD -> origin/main\n  origin/main\n  origin/support-protoprimer-v0.14.0\n  origin/support_windows\n  other/support-foo\n  origin/support-v1\n"

    # when:

    support_branch_names = parse_support_branch_names("origin", remote_branch_list_output)

    # then:

    assert support_branch_names == ["support-protoprimer-v0.14.0", "support-v1"]


def _git(repo_dir: str, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", *args],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def test_find_protected_branch_containing_head(tmp_path, monkeypatch):
    """
    FT_60_28_38_74.compatibility_maintenance.md: a commit in `support-*` (not in `main`) is releasable.
    """

    # given:
    # `main` has the first commit, `support-x` has one more:

    repo_dir = str(tmp_path)
    _git(repo_dir, "init", "-q")
    _git(repo_dir, "commit", "-q", "--allow-empty", "-m", "first")
    first_commit = _git(repo_dir, "rev-parse", "HEAD")
    _git(repo_dir, "commit", "-q", "--allow-empty", "-m", "second")
    second_commit = _git(repo_dir, "rev-parse", "HEAD")
    _git(repo_dir, "update-ref", "refs/remotes/origin/main", first_commit)
    _git(repo_dir, "update-ref", "refs/remotes/origin/support-x", second_commit)
    monkeypatch.chdir(tmp_path)

    # when/then:
    # `HEAD` is in `support-x` only:

    assert find_protected_branch_containing_head("origin") == "support-x"

    # `HEAD` is in both: `main` goes first:

    _git(repo_dir, "checkout", "-q", first_commit)
    assert find_protected_branch_containing_head("origin") == "main"

    # `HEAD` is in no protected branch:

    _git(repo_dir, "checkout", "-q", "-b", "feature")
    _git(repo_dir, "commit", "-q", "--allow-empty", "-m", "third")
    assert find_protected_branch_containing_head("origin") is None
