from __future__ import annotations

import os
import pathlib
import shutil
import subprocess

import pytest

from local_test.fat_mocked_helper import run_primer_main
from local_test.integrated_helper import (
    create_conf_client_file,
    create_two_envs_shape,
    create_two_envs_shape_with_env_selector,
    create_conf_env_file,
    create_conf_primer_file,
    create_plain_proto_kernel,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from local_test.version_gate import (
    skip_if_proto_kernel_older_than,
    since_version,
    before_version,
)
from protoprimer.primer_kernel import (
    _ConfConstClient,
    _ConfConstEnv,
    _ConfConstInput,
    _ConfConstPrimer,
    _ExecOperation,
    _SyntaxArg,
)


def test_boot_env_with_env_selection_default_to_special(tmp_path: pathlib.Path):
    """
    *   Bootstrap without args -> picks `_ConfConstClient.common_env_name` as configured.
    *   Bootstrap with override `_SyntaxArg.arg_env` -> picks `special_env` as specified.
    """

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
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `_ConfLeap.leap_env` / `_ConfConstClient.common_env_name`

    common_env_dir_name = _ConfConstClient.common_env_name
    common_env_dir_abs_path = ref_root_abs_path / common_env_dir_name
    default_venv_rel_path = "venv_default"
    create_conf_env_file(
        ref_root_abs_path,
        common_env_dir_abs_path,
        project_dir_abs_path,
        venv_dir_rel_path=default_venv_rel_path,
    )

    # === create `_ConfLeap.leap_env` / `special_env`

    special_env_dir_name = "special_env"
    special_env_dir_abs_path = ref_root_abs_path / special_env_dir_name
    special_venv_rel_path = "venv_special"
    create_conf_env_file(
        ref_root_abs_path,
        special_env_dir_abs_path,
        project_dir_abs_path,
        venv_dir_rel_path=special_venv_rel_path,
    )

    # === create `_ConfLeap.leap_client` / `_ConfConstClient.common_env_name`

    conf_client_dir_abs_path = ref_root_abs_path / _ConfConstPrimer.default_client_conf_dir_rel_path

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        common_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    default_venv_abs_path = ref_root_abs_path / default_venv_rel_path
    special_venv_abs_path = ref_root_abs_path / special_venv_rel_path

    # when:
    # bootstrap without args (picks `_ConfConstClient.common_env_name` as configured)

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            _SyntaxArg.arg_v,
            _SyntaxArg.arg_v,
        ]
    )

    # then:
    # assert `_ConfConstClient.common_env_name` created

    assert default_venv_abs_path.exists()
    assert not special_venv_abs_path.exists()

    # clean:
    # remove `_ConfConstClient.common_env_name`

    shutil.rmtree(default_venv_abs_path)
    os.remove(ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name)

    # when:
    # bootstrap with `special_env` (override via CLI args):

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            _SyntaxArg.arg_v,
            _SyntaxArg.arg_v,
            _ExecOperation.op_boot.value,
            _SyntaxArg.arg_env,
            special_env_dir_name,
        ]
    )

    # then:
    # assert `special_env` created (because of override via `_SyntaxArg.arg_env`):

    assert not default_venv_abs_path.exists()
    assert special_venv_abs_path.exists()


def test_boot_env_with_env_selection_special_to_default(tmp_path: pathlib.Path):
    """
    *   Bootstrap with override `_SyntaxArg.arg_env` -> picks `special_env` as specified.
    *   Bootstrap without args -> still picks `special_env` as configured.
    """

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
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `_ConfLeap.leap_env` / `special_env`

    special_env_dir_name = "special_env"
    special_env_dir_abs_path = ref_root_abs_path / special_env_dir_name
    special_venv_rel_path = "venv_special"
    create_conf_env_file(
        ref_root_abs_path,
        special_env_dir_abs_path,
        project_dir_abs_path,
        venv_dir_rel_path=special_venv_rel_path,
    )

    # === create `_ConfLeap.leap_env` / `_ConfConstClient.common_env_name`

    common_env_dir_name = _ConfConstClient.common_env_name
    common_env_dir_abs_path = ref_root_abs_path / common_env_dir_name
    default_venv_rel_path = "venv_default"
    create_conf_env_file(
        ref_root_abs_path,
        common_env_dir_abs_path,
        project_dir_abs_path,
        venv_dir_rel_path=default_venv_rel_path,
    )

    # === create `_ConfLeap.leap_client` / `special_env`

    conf_client_dir_abs_path = ref_root_abs_path / _ConfConstPrimer.default_client_conf_dir_rel_path

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        special_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    default_venv_abs_path = ref_root_abs_path / default_venv_rel_path
    special_venv_abs_path = ref_root_abs_path / special_venv_rel_path

    # when:
    # bootstrap with `special_env`

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            _SyntaxArg.arg_v,
            _SyntaxArg.arg_v,
            _ExecOperation.op_boot.value,
            _SyntaxArg.arg_env,
            special_env_dir_name,
        ]
    )

    # then:
    # assert `special_env` created

    assert not default_venv_abs_path.exists()
    assert special_venv_abs_path.exists()

    # clean:
    # remove `special_env`

    shutil.rmtree(special_venv_abs_path)
    os.remove(ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name)

    # when:
    # bootstrap without args

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            _SyntaxArg.arg_v,
            _SyntaxArg.arg_v,
        ]
    )

    # then:
    # assert still `special_env` is created (not `_ConfConstClient.common_env_name`):

    assert not default_venv_abs_path.exists()
    assert special_venv_abs_path.exists()


def _given_persisted_special_env_but_config_default_common(
    tmp_path: pathlib.Path,
):
    """
    *   Bootstrap with override `_SyntaxArg.arg_env` -> picks `special_env` as specified.
    *   Change config to use `_ConfConstClient.common_env_name` as default.

    The outcome (then) of the following bootstrap without args depends on the version (see `FT_60_28_38_74.compatibility_maintenance.md`).
    """

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
    create_test_pyproject_toml(project_dir_abs_path)

    # === create `_ConfLeap.leap_env` / `special_env`

    special_env_dir_name = "special_env"
    special_env_dir_abs_path = ref_root_abs_path / special_env_dir_name
    special_venv_rel_path = "venv_special"
    create_conf_env_file(
        ref_root_abs_path,
        special_env_dir_abs_path,
        project_dir_abs_path,
        venv_dir_rel_path=special_venv_rel_path,
    )

    # === create `_ConfLeap.leap_env` / `_ConfConstClient.common_env_name`

    common_env_dir_name = _ConfConstClient.common_env_name
    common_env_dir_abs_path = ref_root_abs_path / common_env_dir_name
    default_venv_rel_path = "venv_default"
    create_conf_env_file(
        ref_root_abs_path,
        common_env_dir_abs_path,
        project_dir_abs_path,
        venv_dir_rel_path=default_venv_rel_path,
    )

    # === create `_ConfLeap.leap_client` / `special_env`

    conf_client_dir_abs_path = ref_root_abs_path / _ConfConstPrimer.default_client_conf_dir_rel_path

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        special_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===

    default_venv_abs_path = ref_root_abs_path / default_venv_rel_path
    special_venv_abs_path = ref_root_abs_path / special_venv_rel_path

    # when:
    # bootstrap with `special_env`

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            _SyntaxArg.arg_v,
            _SyntaxArg.arg_v,
            _ExecOperation.op_boot.value,
            _SyntaxArg.arg_env,
            special_env_dir_name,
        ]
    )

    # then:
    # assert `special_env` created

    assert not default_venv_abs_path.exists()
    assert special_venv_abs_path.exists()

    # clean:
    # remove `venv_special` but leave `special_env` symlink

    shutil.rmtree(special_venv_abs_path)

    # given:
    # switch config from `env_special` to `_ConfConstClient.common_env_name`

    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        common_env_dir_abs_path,
        project_dir_abs_path,
    )

    return proto_kernel_abs_path, default_venv_abs_path, special_venv_abs_path


@before_version("0.15.0")
def test_boot_env_with_symlink_to_env_special_but_config_to_env_common_fails(
    tmp_path: pathlib.Path,
):
    """
    *   Bootstrap without args -> fails because configured `_ConfConstClient.common_env_name` mismatches with symlink.
    """

    # given:

    proto_kernel_abs_path, default_venv_abs_path, special_venv_abs_path = _given_persisted_special_env_but_config_default_common(tmp_path)

    # when:
    # then:
    # fails because symlink `lconf_env` points to `special_env`
    # but client config default is `_ConfConstClient.common_env_name`
    try:
        run_primer_main(
            [
                str(proto_kernel_abs_path),
                _SyntaxArg.arg_v,
                _SyntaxArg.arg_v,
            ]
        )
    except AssertionError as e:
        # This path is for the `fast_fat_min_mocked` test:
        assert "is not the same as the provided target" in str(e)
    except subprocess.CalledProcessError:
        # This path is for the direct execution of the `slow_integrated` test:
        pass

    # then:
    # assert bootstrap failed, so no venv created
    assert not default_venv_abs_path.exists()
    assert not special_venv_abs_path.exists()


@since_version("0.15.0")
def test_boot_env_with_symlink_to_env_special_but_config_to_env_common_uses_persisted(
    tmp_path: pathlib.Path,
):
    """
    *   Bootstrap without args -> the persisted `special_env` (symlink) is used:
        the default env is only a fallback (see `FT_03_31_63_70.environment_selection.md`).
    """

    # given:

    proto_kernel_abs_path, default_venv_abs_path, special_venv_abs_path = _given_persisted_special_env_but_config_default_common(tmp_path)

    # when:
    # bootstrap without args: nothing is selected, so the persisted `special_env` is used
    # (even though client config default is `_ConfConstClient.common_env_name`)

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            _SyntaxArg.arg_v,
            _SyntaxArg.arg_v,
            _ExecOperation.op_boot.value,
        ]
    )

    # then:
    # `venv_special` is re-created and `venv_default` is not created

    assert not default_venv_abs_path.exists()
    assert special_venv_abs_path.exists()


def test_boot_env_with_env_mismatching_persisted_env_fails(tmp_path: pathlib.Path):
    """
    FT_03_31_63_70.environment_selection.md: `_ExecOperation.op_boot` + persisted env + `--env` mismatch = failure.
    """

    # given:
    # the default env is persisted:

    two_envs_shape = create_two_envs_shape(tmp_path)
    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name
    os.symlink(
        two_envs_shape.default_env_dir_abs_path.name,
        env_link_abs_path,
    )

    # when:
    # bootstrap with another env:

    with pytest.raises((AssertionError, subprocess.CalledProcessError)):
        run_primer_main(
            [
                str(two_envs_shape.proto_kernel_abs_path),
                _ExecOperation.op_boot.value,
                _SyntaxArg.arg_env,
                two_envs_shape.special_env_dir_abs_path.name,
            ]
        )

    # then:
    # the persisted env is not changed and nothing is installed:

    assert os.readlink(env_link_abs_path) == two_envs_shape.default_env_dir_abs_path.name
    assert not two_envs_shape.default_venv_abs_path.exists()
    assert not two_envs_shape.special_venv_abs_path.exists()


def test_boot_env_without_env_selection_uses_global_conf_dir(tmp_path: pathlib.Path):
    """
    FT_03_31_63_70.environment_selection.md: no env is selected, persisted or configured as the default
    => the global config dir is used (and nothing is persisted).
    """

    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    # given:
    # no default env is configured:

    two_envs_shape = create_two_envs_shape(tmp_path)
    ref_root_abs_path = two_envs_shape.ref_root_abs_path
    conf_client_dir_abs_path = ref_root_abs_path / _ConfConstPrimer.default_client_conf_dir_rel_path
    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        None,
        ref_root_abs_path / test_pyproject_src_dir_rel_path,
    )

    # when:

    run_primer_main(
        [
            str(two_envs_shape.proto_kernel_abs_path),
            _ExecOperation.op_boot.value,
            _SyntaxArg.arg_v,
            _SyntaxArg.arg_v,
        ]
    )

    # then:
    # `venv` is created and the env-specific data lands in the global config dir (no env link):

    assert (ref_root_abs_path / _ConfConstEnv.default_dir_rel_path_venv).exists()
    assert (conf_client_dir_abs_path / _ConfConstEnv.default_version_constraints_file_basename).exists()
    assert not os.path.lexists(ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name)
    assert not two_envs_shape.default_venv_abs_path.exists()
    assert not two_envs_shape.special_venv_abs_path.exists()


def _given_env_selector_shape(
    tmp_path: pathlib.Path,
    selected_env_dir_rel_path: str | None,
):
    """
    Two envs, the default one is configured in the client config,
    and the env selector (also configured in the client config) always returns `selected_env_dir_rel_path`.
    """

    two_envs_shape = create_two_envs_shape_with_env_selector(tmp_path, selected_env_dir_rel_path)

    return two_envs_shape


def _boot_env_args(
    two_envs_shape,
    *extra_args: str,
) -> list:
    return [
        str(two_envs_shape.proto_kernel_abs_path),
        _ExecOperation.op_boot.value,
        _SyntaxArg.arg_v,
        _SyntaxArg.arg_v,
        *extra_args,
    ]


def test_boot_env_with_env_selector_overrides_default_env(tmp_path: pathlib.Path):
    """
    FT_03_31_63_70.environment_selection.md: the env selector (no `--env` arg) selects the env instead of the default one.
    """

    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    # given:

    two_envs_shape = _given_env_selector_shape(tmp_path, "special_env")

    # when:

    run_primer_main(_boot_env_args(two_envs_shape))

    # then:
    # the selected env is persisted and used:

    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name
    assert os.readlink(env_link_abs_path) == two_envs_shape.special_env_dir_abs_path.name
    assert two_envs_shape.special_venv_abs_path.exists()
    assert not two_envs_shape.default_venv_abs_path.exists()


def test_boot_env_with_env_arg_overrides_env_selector(tmp_path: pathlib.Path):
    """
    FT_03_31_63_70.environment_selection.md: the value provided by the env selector is override-able via `--env` arg.
    """

    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    # given:
    # the selector selects the special env:

    two_envs_shape = _given_env_selector_shape(tmp_path, "special_env")

    # when:
    # bootstrap with the default env via `--env`:

    run_primer_main(
        _boot_env_args(
            two_envs_shape,
            _SyntaxArg.arg_env,
            two_envs_shape.default_env_dir_abs_path.name,
        )
    )

    # then:

    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name
    assert os.readlink(env_link_abs_path) == two_envs_shape.default_env_dir_abs_path.name
    assert two_envs_shape.default_venv_abs_path.exists()
    assert not two_envs_shape.special_venv_abs_path.exists()


def test_boot_env_with_env_selector_returning_none_uses_default_env(tmp_path: pathlib.Path):
    """
    FT_03_31_63_70.environment_selection.md: the env selector returns `None` => the default env is used.
    """

    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    # given:

    two_envs_shape = _given_env_selector_shape(tmp_path, None)

    # when:

    run_primer_main(_boot_env_args(two_envs_shape))

    # then:

    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name
    assert os.readlink(env_link_abs_path) == two_envs_shape.default_env_dir_abs_path.name
    assert two_envs_shape.default_venv_abs_path.exists()
    assert not two_envs_shape.special_venv_abs_path.exists()


def test_boot_env_with_env_selector_matching_persisted_env_is_repeatable(tmp_path: pathlib.Path):
    """
    FT_03_31_63_70.environment_selection.md: the selected env matches the persisted env => no conflict.
    """

    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    # given:

    two_envs_shape = _given_env_selector_shape(tmp_path, "special_env")

    # when:
    # bootstrap twice (the second time the selected env is already persisted):

    run_primer_main(_boot_env_args(two_envs_shape))

    # clean:
    # remove `venv_special` but leave `special_env` symlink

    shutil.rmtree(two_envs_shape.special_venv_abs_path)

    run_primer_main(_boot_env_args(two_envs_shape))

    # then:

    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name
    assert os.readlink(env_link_abs_path) == two_envs_shape.special_env_dir_abs_path.name
    assert two_envs_shape.special_venv_abs_path.exists()


def test_boot_env_with_env_selector_mismatching_persisted_env_fails(tmp_path: pathlib.Path):
    """
    FT_03_31_63_70.environment_selection.md: `_ExecOperation.op_boot` + persisted env + selected env mismatch = failure.
    """

    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    # given:
    # the default env is persisted, but the selector selects the special env:

    two_envs_shape = _given_env_selector_shape(tmp_path, "special_env")
    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name
    os.symlink(
        two_envs_shape.default_env_dir_abs_path.name,
        env_link_abs_path,
    )

    # when:

    with pytest.raises((AssertionError, subprocess.CalledProcessError)):
        run_primer_main(_boot_env_args(two_envs_shape))

    # then:
    # the persisted env is not changed and nothing is installed:

    assert os.readlink(env_link_abs_path) == two_envs_shape.default_env_dir_abs_path.name
    assert not two_envs_shape.default_venv_abs_path.exists()
    assert not two_envs_shape.special_venv_abs_path.exists()
