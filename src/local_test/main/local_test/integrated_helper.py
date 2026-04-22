import logging
import os
import pathlib
import shutil
import stat
import sys
from pathlib import Path
from typing import (
    List,
    Tuple,
    Union,
)

import protoprimer
from local_test.toml_handler import save_toml_data
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstEnv,
    ConfConstGeneral,
    ConfConstInput,
    ConfConstPrimer,
    ConfField,
    TopDir,
    parse_python_version,
    write_json_file,
    write_text_file,
)

logger = logging.getLogger()

test_pyproject_src_dir_rel_path = "pyproject_src"
test_package_name = "test_whatever"
test_python_version = "3.10"
test_python_abs_path = "/test/python"


def convert_test_python_version(python_version_str: str) -> str:
    """
    It turns out `uv` may not have all `python` versions available for download which fails integration tests.

    This function adjusts version `X.Y.Z` to `X.Y.P` where `P` makes it available for download.

    Use this function only as an input to generate test config files.
    """

    python_version_tuple: tuple[int, int, int] = parse_python_version(python_version_str)

    (
        major_version,
        minor_version,
        patch_level,
    ) = python_version_tuple

    # FT_84_11_73_28.supported_python_versions.md:
    if (3, 14) <= (major_version, minor_version) < (3, 15):
        python_version_tuple = (3, 14, 0)

    return f"{python_version_tuple[0]}.{python_version_tuple[1]}.{python_version_tuple[2]}"


def switch_to_ref_root_abs_path(tmp_path: pathlib.Path) -> pathlib.Path:
    """
    Ensure the current directory is the `PathName.path_ref_root`.
    """

    tmp_dir_abs_path = tmp_path.resolve()
    assert os.path.isdir(str(tmp_dir_abs_path))
    assert os.path.isabs(str(tmp_dir_abs_path))
    os.chdir(str(tmp_dir_abs_path))

    return tmp_dir_abs_path


def create_plain_proto_code(
    proto_code_dir_abs_path: pathlib.Path,
) -> pathlib.Path:
    """
    Creates a test dir with FT_90_65_67_62.proto_code.md.
    """

    primer_kernel_abs_path = protoprimer.primer_kernel.__file__
    logger.info(f"primer_kernel_abs_path: {primer_kernel_abs_path}")

    # Create a `proto_code` directory:
    proto_code_dir_abs_path = proto_code_dir_abs_path
    proto_code_dir_abs_path.mkdir(
        parents=True,
        # It can exists if `proto_code` is placed into `ref_root` dir ~ "instant_scenario":
        exist_ok=True,
    )

    # Copy `primer_kernel.py` to `proto_code/proto_kernel.py`:
    proto_kernel_abs_path = proto_code_dir_abs_path / "proto_kernel.py"

    shutil.copy(primer_kernel_abs_path, proto_kernel_abs_path)

    # Make the `primer_kernel.py` executable:
    if proto_kernel_abs_path.exists():
        curr_stat = os.stat(proto_kernel_abs_path)
        next_stat = curr_stat.st_mode | stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR
        os.chmod(proto_kernel_abs_path, next_stat)

    # TODO: Instead of returning, set `EvnVar.var_PROTOPRIMER_PROTO_CODE` in case of `EnvVar.var_PROTOPRIMER_MOCKED_RESTART`.
    #       This would allow running `test_slow_integrated` wrapped in mocks set by `test_fast_slim_max_mocked`
    #       without modifications.
    return proto_kernel_abs_path


def create_test_pyproject_toml(
    project_dir_abs_path: pathlib.Path,
    extra_dependencies: Union[List[str], None] = None,
):
    if extra_dependencies is None:
        extra_dependencies = []

    # From `primer_kernel.py` sources to `./src/protoprimer/` where `pyproject.toml` is:
    protoprimer_project_dir = pathlib.Path(protoprimer.__file__).parent.parent.parent
    # From `./src/protoprimer/` to all other `pyproject.toml`:
    local_doc_project_dir = protoprimer_project_dir.parent / "local_doc"
    local_repo_project_dir = protoprimer_project_dir.parent / "local_repo"
    local_test_project_dir = protoprimer_project_dir.parent / "local_test"
    metaprimer_project_dir = protoprimer_project_dir.parent / "metaprimer"

    pyproject_file_abs_path = project_dir_abs_path / ConfConstClient.default_pyproject_toml_basename

    toml_data = {
        "project": {
            "name": test_package_name,
            "version": "0.0.0.dev0",
            "dependencies": [
                f"local_doc @ file://{local_doc_project_dir}",
                f"local_repo @ file://{local_repo_project_dir}",
                f"local_test @ file://{local_test_project_dir}",
                f"metaprimer @ file://{metaprimer_project_dir}",
                f"protoprimer @ file://{protoprimer_project_dir}",
            ]
            + extra_dependencies,
        },
        "tool": {
            "setuptools": {
                "packages": {
                    "find": {
                        # Unless we create the "src" dir (to make it auto-discover-able "src-layout"),
                        # we need to exclude top-level dirs (otherwise, auto-discovery fails on multiple candidates):
                        "exclude": [top_dir.value for top_dir in TopDir],
                    }
                }
            }
        },
    }

    pyproject_dir_abs_path = pyproject_file_abs_path.parent
    pyproject_dir_abs_path.mkdir(parents=True, exist_ok=True)

    save_toml_data(
        str(pyproject_file_abs_path),
        toml_data,
    )


def create_test_python_selector(
    ref_root_abs_path: pathlib.Path,
    python_selector_rel_path: pathlib.Path,
    python_version: str,
) -> None:
    """
    Creates a test python selector script.

    See: FT_72_45_12_06.python_executable.md
    """
    python_selector_abs_path = ref_root_abs_path / python_selector_rel_path
    python_selector_abs_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_file(
        str(python_selector_abs_path),
        f"""\
from __future__ import annotations

import shutil


def select_python_file_abs_path(required_version: tuple[int, int, int]) -> str | None:
    return shutil.which("python{python_version}")
""",
    )


def create_conf_primer_file(
    ref_root_abs_path: pathlib.Path,
    proto_code_dir_abs_path: pathlib.Path,
) -> None:

    ref_root_dir_rel_path: str = os.path.relpath(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    prime_conf_data = {
        ConfField.field_ref_root_dir_rel_path.value: ref_root_dir_rel_path,
        ConfField.field_global_conf_dir_rel_path.value: ConfConstPrimer.default_client_conf_dir_rel_path,
    }

    conf_primer_file_abs_path = proto_code_dir_abs_path / ConfConstInput.default_file_basename_conf_primer

    write_json_file(
        str(conf_primer_file_abs_path),
        prime_conf_data,
    )


def create_python_version_file(
    ref_root_dir_abs_path: str,
    python_version: str,
) -> None:
    python_version_file_abs_path: str = os.path.join(
        ref_root_dir_abs_path,
        ConfConstGeneral.python_version_file_basename,
    )
    write_text_file(
        python_version_file_abs_path,
        python_version,
    )


def create_conf_client_file(
    ref_root_abs_path: pathlib.Path,
    conf_client_dir_abs_path: pathlib.Path,
    conf_env_dir_abs_path: pathlib.Path,
    project_dir_abs_path: pathlib.Path,
) -> None:

    project_dir_rel_path: str = os.path.relpath(
        project_dir_abs_path,
        ref_root_abs_path,
    )

    conf_env_dir_rel_path: str = os.path.relpath(
        conf_env_dir_abs_path,
        ref_root_abs_path,
    )

    client_conf_data = {
        ConfField.field_required_python_version.value: test_python_version,
        ConfField.field_local_conf_symlink_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name,
        ConfField.field_default_env_dir_rel_path.value: str(conf_env_dir_rel_path),
        ConfField.field_project_descriptors.value: [
            {
                ConfField.field_build_root_dir_rel_path.value: str(project_dir_rel_path),
                ConfField.field_install_extras.value: [],
            },
        ],
    }

    conf_client_dir_abs_path.mkdir(parents=True, exist_ok=True)

    conf_client_file_abs_path = conf_client_dir_abs_path / ConfConstPrimer.default_file_basename_leap_client

    write_json_file(
        str(conf_client_file_abs_path),
        client_conf_data,
    )


def create_conf_env_file(
    ref_root_abs_path: pathlib.Path,
    conf_env_dir_abs_path: pathlib.Path,
    project_dir_abs_path: pathlib.Path,
    python_abs_path: Union[str, None] = None,
    venv_dir_rel_path: Union[str, None] = None,
    required_python_version: str = test_python_version,
    python_selector_rel_path: pathlib.Path = None,
) -> None:
    if python_abs_path is None:
        python_abs_path = sys.executable
    if venv_dir_rel_path is None:
        venv_dir_rel_path = ConfConstEnv.default_dir_rel_path_venv

    project_dir_rel_path: str = os.path.relpath(
        project_dir_abs_path,
        ref_root_abs_path,
    )

    env_conf_data = {}

    if python_selector_rel_path is not None:
        env_conf_data.update(
            {
                ConfField.field_python_selector_file_rel_path.value: str(python_selector_rel_path),
            }
        )

    env_conf_data.update(
        {
            ConfField.field_required_python_version.value: required_python_version,
            ConfField.field_local_venv_dir_rel_path.value: venv_dir_rel_path,
            # NOTE: Not specifying `ConfField.field_venv_driver.value` - it will be (automatic):
            #       *   `VenvDriverType.venv_pip` for `python` version < 3.8
            #       *   `VenvDriverType.venv_uv` for `python` version >= 3.8
            # ConfField.field_venv_driver.value: VenvDriverType.venv_pip.name,
            ConfField.field_project_descriptors.value: [
                {
                    ConfField.field_build_root_dir_rel_path.value: str(project_dir_rel_path),
                    ConfField.field_install_extras.value: [],
                    ConfField.field_install_group.value: "whatever_group_main",
                },
            ],
            ConfField.field_install_specs.value: [
                {
                    "whatever_group_main": {
                        ConfField.field_extra_command_args.value: [
                            # This is to avoid picking up a stale build during editable installation.
                            # For example, this:
                            # ./src/metaprimer/build/
                            # instead of this:
                            # ./src/metaprimer/main/
                            "--no-cache-dir",
                        ],
                    },
                },
            ],
        }
    )

    conf_env_dir_abs_path.mkdir(parents=True, exist_ok=True)

    conf_env_file_abs_path = conf_env_dir_abs_path / ConfConstClient.default_file_basename_leap_env

    write_json_file(
        str(conf_env_file_abs_path),
        env_conf_data,
    )


def create_min_layout(tmp_path: Path) -> Tuple[Path, Path, Path]:
    """
    See "min" layout: FT_59_95_81_63.env_layout.md
    """

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # Use the `ConfConstGeneral.python_version_file_basename` file in the min layout:
    create_python_version_file(str(ref_root_abs_path), test_python_version)

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path

    create_test_pyproject_toml(project_dir_abs_path)

    # === no `ConfLeap.leap_primer` config file

    proto_kernel_abs_path: Path = create_plain_proto_code(ref_root_abs_path)

    # === no `ConfLeap.leap_env` config file

    # === no `ConfLeap.leap_client` config file

    # ===

    return (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    )


def create_max_layout(tmp_path: Path) -> Tuple[Path, Path, Path]:
    """
    See "max" layout: FT_59_95_81_63.env_layout.md
    """

    ref_root_abs_path: pathlib.Path = switch_to_ref_root_abs_path(tmp_path)

    # === create `ConfLeap.leap_primer`

    proto_code_dir_abs_path = ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    proto_kernel_abs_path: Path = create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `ConfLeap.leap_env` / `default_env`

    conf_env_dir_abs_path = ref_root_abs_path / ConfConstClient.default_default_env_dir_rel_path

    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # === create `ConfLeap.leap_client`

    conf_client_dir_abs_path = ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    return (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    )
