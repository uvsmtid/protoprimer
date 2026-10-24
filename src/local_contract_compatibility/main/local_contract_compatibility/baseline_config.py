from __future__ import annotations

import pathlib

import tomli

config_section_name = "local_contract_compatibility"
config_key_baseline_commit_names = "baseline_commit_names"


def read_baseline_commit_names(
    repo_dir_abs_path: pathlib.Path,
    package_name: str,
) -> list[str]:
    """
    Reads `baseline_commit_names` from `[tool.local_contract_compatibility]` in `src/<package_name>/pyproject.toml`.
    """

    pyproject_toml_abs_path = repo_dir_abs_path / "src" / package_name / "pyproject.toml"
    with open(pyproject_toml_abs_path, "rb") as pyproject_file:
        pyproject_data = tomli.load(pyproject_file)

    section_data = pyproject_data.get("tool", {}).get(config_section_name)
    if section_data is None or config_key_baseline_commit_names not in section_data:
        raise AssertionError(f"[{pyproject_toml_abs_path}] has no [tool.{config_section_name}] `{config_key_baseline_commit_names}`")

    commit_names = section_data[config_key_baseline_commit_names]
    if not isinstance(commit_names, list) or len(commit_names) == 0 or not all(isinstance(commit_name, str) for commit_name in commit_names):
        raise AssertionError(f"`{config_key_baseline_commit_names}` in [{pyproject_toml_abs_path}] must be a non-empty list of strings")
    return commit_names
