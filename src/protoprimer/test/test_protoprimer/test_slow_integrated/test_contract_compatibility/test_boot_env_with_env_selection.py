import os
import pathlib
import shutil
import subprocess

from local_test.fat_mocked_helper import run_primer_main
from local_test.integrated_helper import (
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
    create_plain_proto_kernel,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from protoprimer.primer_kernel import (
    _ConfConstClient,
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


def test_boot_env_with_symlink_to_env_special_but_config_to_env_common(
    tmp_path: pathlib.Path,
):
    """
    *   Bootstrap with override `_SyntaxArg.arg_env` -> picks `special_env` as specified.
    *   Change config to use `_ConfConstClient.common_env_name` as default.
    *   Bootstrap without args -> fails because configured `_ConfConstClient.common_env_name` mismatches with symlink.
        TODO: TODO_53_40_17_68.default_env_config_vs_lconf_symlink.md: review this behavior.
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

    # TODO: TODO_53_40_17_68.default_env_config_vs_lconf_symlink.md:
    #       Review this behavior:
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
