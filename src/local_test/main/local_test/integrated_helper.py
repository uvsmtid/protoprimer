import logging
import os
import pathlib
import shutil
import stat
from pathlib import Path

import protoprimer
from local_test.toml_handler import save_toml_data
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstEnv,
    ConfConstInput,
    ConfConstPrimer,
    ConfField,
    PackageDriverType,
    TopDir,
    write_json_file,
)

logger = logging.getLogger()

test_pyproject_src_dir_rel_path = "pyproject_src"
test_package_name = "test_whatever"


def switch_to_ref_root_abs_path(tmp_path: pathlib.Path) -> pathlib.Path:
    """
    Ensure the current directory is the `PathName.path_ref_root`.
    """

    tmp_dir_abs_path = pathlib.Path(tmp_path)
    assert os.path.isdir(tmp_dir_abs_path)
    assert os.path.isabs(tmp_dir_abs_path)
    os.chdir(tmp_path)

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

    # TODO: Instead of returning, set `EvnVar.var_PROTOPRIMER_PROTO_CODE` in case of `EnvVar.var_PROTOPRIMER_TEST_MODE`.
    #       This would allow running `test_slow_integrated` wrapped in mocks set by `test_fast_slim_max_mocked`
    #       without modifications.
    return proto_kernel_abs_path


def create_test_pyproject_toml(
    project_dir_abs_path: pathlib.Path,
    extra_dependencies: list[str] | None = None,
):
    if extra_dependencies is None:
        extra_dependencies = []

    # From `primer_kernel.py` sources to `./src/protoprimer/` where `pyproject.toml` is:
    protoprimer_project_dir = pathlib.Path(protoprimer.__file__).parent.parent.parent
    # From `./src/protoprimer/` to all other `pyproject.toml`:
    local_doc_project_dir = protoprimer_project_dir.parent / "local_doc"
    local_repo_project_dir = protoprimer_project_dir.parent / "local_repo"
    local_test_project_dir = protoprimer_project_dir.parent / "local_test"
    neoprimer_project_dir = protoprimer_project_dir.parent / "neoprimer"

    pyproject_file_abs_path = (
        project_dir_abs_path / ConfConstClient.default_pyproject_toml_basename
    )

    toml_data = {
        "project": {
            "name": test_package_name,
            "version": "0.0.0.dev0",
            "dependencies": [
                f"local_doc @ file://{local_doc_project_dir}",
                f"local_repo @ file://{local_repo_project_dir}",
                f"local_test @ file://{local_test_project_dir}",
                f"neoprimer @ file://{neoprimer_project_dir}",
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


def create_conf_primer_file(
    ref_root_abs_path: pathlib.Path,
    proto_code_dir_abs_path: pathlib.Path,
) -> None:

    ref_root_dir_rel_path: str = os.path.relpath(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    prime_conf_data = {
        ConfField.field_primer_ref_root_dir_rel_path.value: ref_root_dir_rel_path,
        ConfField.field_primer_conf_client_dir_rel_path.value: ConfConstPrimer.default_client_conf_dir_rel_path,
    }

    conf_primer_file_abs_path = (
        proto_code_dir_abs_path / ConfConstInput.default_file_basename_conf_primer
    )

    write_json_file(
        str(conf_primer_file_abs_path),
        prime_conf_data,
    )


def create_conf_client_file(
    ref_root_abs_path: pathlib.Path,
    conf_client_dir_abs_path: pathlib.Path,
    conf_env_dir_abs_path: pathlib.Path,
) -> None:

    conf_env_dir_rel_path: str = os.path.relpath(
        conf_env_dir_abs_path,
        ref_root_abs_path,
    )

    client_conf_data = {
        ConfField.field_client_link_name_dir_rel_path.value: ConfConstClient.default_dir_rel_path_leap_env_link_name,
        ConfField.field_client_default_env_dir_rel_path.value: str(
            conf_env_dir_rel_path
        ),
    }

    conf_client_dir_abs_path.mkdir(parents=True, exist_ok=True)

    conf_client_file_abs_path = (
        conf_client_dir_abs_path / ConfConstPrimer.default_file_basename_leap_client
    )

    write_json_file(
        str(conf_client_file_abs_path),
        client_conf_data,
    )


def create_conf_env_file(
    ref_root_abs_path: pathlib.Path,
    conf_env_dir_abs_path: pathlib.Path,
    project_dir_abs_path: pathlib.Path,
    python_abs_path: str | None = None,
    venv_dir_rel_path: str | None = None,
) -> None:
    if python_abs_path is None:
        python_abs_path = ConfConstEnv.default_file_abs_path_python
    if venv_dir_rel_path is None:
        venv_dir_rel_path = ConfConstEnv.default_dir_rel_path_venv

    project_dir_rel_path: str = os.path.relpath(
        project_dir_abs_path,
        ref_root_abs_path,
    )

    env_conf_data = {
        ConfField.field_required_python_file_abs_path.value: python_abs_path,
        ConfField.field_local_venv_dir_rel_path.value: venv_dir_rel_path,
        # TODO: Parameterize tests to succeed with
        #       both `PackageDriverType.driver_pip` and `PackageDriverType.driver_uv`.
        ConfField.field_package_driver.value: PackageDriverType.driver_pip.name,
        ConfField.field_project_descriptors.value: [
            {
                ConfField.field_build_root_dir_rel_path.value: str(
                    project_dir_rel_path
                ),
                ConfField.field_install_extras.value: [],
            },
        ],
    }

    conf_env_dir_abs_path.mkdir(parents=True, exist_ok=True)

    conf_env_file_abs_path = (
        conf_env_dir_abs_path / ConfConstClient.default_file_basename_leap_env
    )

    write_json_file(
        str(conf_env_file_abs_path),
        env_conf_data,
    )


def create_min_layout(tmp_path: Path) -> tuple[Path, Path, Path]:
    """
    See "min" layout: FT_59_95_81_63.env_layout.md
    """

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

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


def create_max_layout(tmp_path: Path) -> tuple[Path, Path, Path]:
    """
    See "max" layout: FT_59_95_81_63.env_layout.md
    """

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # === create `ConfLeap.leap_primer`

    proto_code_dir_abs_path = (
        ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    )
    proto_kernel_abs_path: Path = create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `ConfLeap.leap_env` / `default_env`

    conf_env_dir_abs_path = (
        ref_root_abs_path / ConfConstClient.default_client_default_env_dir_rel_path
    )

    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # === create `ConfLeap.leap_client`

    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
    )

    # ===

    return (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    )
