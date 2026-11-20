import os
import pathlib

from local_repo.sub_proc_util import (
    get_command_output,
)
from local_test.fat_mocked_helper import run_primer_main
from local_test.integrated_helper import (
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
    create_plain_proto_kernel,
    create_two_envs_shape,
    create_two_envs_shape_with_env_selector,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from local_test.package_version_verifier import extract_package_version
from local_test.version_gate import skip_if_proto_kernel_older_than
from protoprimer.primer_kernel import (
    _ConfConstClient,
    _ConfConstEnv,
    _ConfConstGeneral,
    _ConfConstInput,
    _ConfConstPrimer,
    _ExecOperation,
    _SyntaxArg,
)


def test_op_reset(tmp_path: pathlib.Path):

    # given:

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # === create `_ConfLeap.leap_primer`

    proto_kernel_dir_abs_path = ref_root_abs_path / _ConfConstInput.default_proto_conf_dir_rel_path
    proto_kernel_abs_path: pathlib.Path = create_plain_proto_kernel(proto_kernel_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_kernel_dir_abs_path,
    )

    # === create `pyproject.toml`

    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(
        project_dir_abs_path,
        [
            # NOTE: Install `pip` to query package versions below (even if it might be a `venv` created with `uv`):
            _ConfConstGeneral.name_pip_package,
            "pyfakefs",
        ],
    )

    # === create `_ConfLeap.leap_env` / `default_env`

    conf_env_dir_abs_path = ref_root_abs_path / _ConfConstClient.default_default_env_dir_rel_path

    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # === create `_ConfLeap.leap_client`

    conf_client_dir_abs_path = ref_root_abs_path / _ConfConstPrimer.default_client_conf_dir_rel_path

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    package_name = "pyfakefs"
    constraints_file = conf_env_dir_abs_path / _ConfConstEnv.default_version_constraints_file_basename
    constraints_file.write_text(f"{package_name}==5.7.4")

    # when:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            _ExecOperation.op_boot.value,
            _SyntaxArg.arg_v,
            _SyntaxArg.arg_v,
        ]
    )

    # then:

    venv_pip: str = str(ref_root_abs_path / _ConfConstEnv.default_dir_rel_path_venv / "bin" / _ConfConstGeneral.name_pip_package)
    pip_freeze_output_install = get_command_output(f"{venv_pip} freeze")
    package_version_install = extract_package_version(
        pip_freeze_output_install,
        package_name,
    )
    assert f"{package_name}==5.7.4" in pip_freeze_output_install

    # when:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            _ExecOperation.op_reset.value,
            _SyntaxArg.arg_v,
            _SyntaxArg.arg_v,
        ]
    )

    # then:

    pip_freeze_output_reset = get_command_output(f"{venv_pip} freeze")

    package_version_reset = extract_package_version(
        pip_freeze_output_reset,
        package_name,
    )
    assert package_version_install < package_version_reset


def test_op_reset_overwrites_persisted_env(tmp_path: pathlib.Path):
    """
    FT_03_31_63_70.environment_selection.md: `_ExecOperation.op_reset` selects the env any time.
    """

    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    # given:
    # the default env is persisted:

    two_envs_shape = create_two_envs_shape(tmp_path)
    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name
    os.symlink(
        two_envs_shape.default_env_dir_abs_path.name,
        env_link_abs_path,
    )

    # when:
    # reset with another env:

    run_primer_main(
        [
            str(two_envs_shape.proto_kernel_abs_path),
            _ExecOperation.op_reset.value,
            _SyntaxArg.arg_env,
            two_envs_shape.special_env_dir_abs_path.name,
            _SyntaxArg.arg_v,
            _SyntaxArg.arg_v,
        ]
    )

    # then:
    # the persisted env is overwritten and the new env is bootstrapped:

    assert os.readlink(env_link_abs_path) == two_envs_shape.special_env_dir_abs_path.name
    assert two_envs_shape.special_venv_abs_path.exists()
    assert not two_envs_shape.default_venv_abs_path.exists()


def test_op_reset_with_env_selector_overwrites_persisted_env(tmp_path: pathlib.Path):
    """
    FT_03_31_63_70.environment_selection.md: `_ExecOperation.op_reset` + persisted env + selector mismatch = overwrite.
    """

    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    # given:
    # the default env is persisted, but the selector selects the special env:

    two_envs_shape = create_two_envs_shape_with_env_selector(tmp_path, "special_env")
    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name
    os.symlink(
        two_envs_shape.default_env_dir_abs_path.name,
        env_link_abs_path,
    )

    # when:
    # reset without `--env`:

    run_primer_main(
        [
            str(two_envs_shape.proto_kernel_abs_path),
            _ExecOperation.op_reset.value,
            _SyntaxArg.arg_v,
            _SyntaxArg.arg_v,
        ]
    )

    # then:
    # the persisted env is overwritten by the selected one and bootstrapped:

    assert os.readlink(env_link_abs_path) == two_envs_shape.special_env_dir_abs_path.name
    assert two_envs_shape.special_venv_abs_path.exists()
    assert not two_envs_shape.default_venv_abs_path.exists()


def test_op_reset_with_env_arg_overrides_env_selector(tmp_path: pathlib.Path):
    """
    FT_03_31_63_70.environment_selection.md: the value provided by the selector is override-able via `--env` arg.
    """

    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    # given:
    # nothing is persisted, the selector selects the special env:

    two_envs_shape = create_two_envs_shape_with_env_selector(tmp_path, "special_env")
    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name

    # when:
    # reset with the default env via `--env`:

    run_primer_main(
        [
            str(two_envs_shape.proto_kernel_abs_path),
            _ExecOperation.op_reset.value,
            _SyntaxArg.arg_env,
            two_envs_shape.default_env_dir_abs_path.name,
            _SyntaxArg.arg_v,
            _SyntaxArg.arg_v,
        ]
    )

    # then:

    assert os.readlink(env_link_abs_path) == two_envs_shape.default_env_dir_abs_path.name
    assert two_envs_shape.default_venv_abs_path.exists()
    assert not two_envs_shape.special_venv_abs_path.exists()
