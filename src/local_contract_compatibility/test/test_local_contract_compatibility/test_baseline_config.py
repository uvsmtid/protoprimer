import pathlib

import pytest

from local_contract_compatibility.baseline_config import read_baseline_commit_names


def write_pyproject(repo_dir: pathlib.Path, content: str):
    package_dir = repo_dir / "src" / "some_package"
    package_dir.mkdir(parents=True)
    (package_dir / "pyproject.toml").write_text(content)


def test_read_baseline_commit_names(tmp_path: pathlib.Path):
    write_pyproject(tmp_path, '[tool.local_contract_compatibility]\nbaseline_commit_names = ["HEAD", "v1.2.3"]\n')
    assert read_baseline_commit_names(tmp_path, "some_package") == ["HEAD", "v1.2.3"]


def test_missing_section_fails(tmp_path: pathlib.Path):
    write_pyproject(tmp_path, '[project]\nname = "x"\n')
    with pytest.raises(AssertionError):
        read_baseline_commit_names(tmp_path, "some_package")


def test_empty_list_fails(tmp_path: pathlib.Path):
    write_pyproject(tmp_path, "[tool.local_contract_compatibility]\nbaseline_commit_names = []\n")
    with pytest.raises(AssertionError):
        read_baseline_commit_names(tmp_path, "some_package")
