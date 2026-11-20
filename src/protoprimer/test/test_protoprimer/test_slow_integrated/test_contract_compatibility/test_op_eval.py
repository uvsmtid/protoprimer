import os
from pathlib import Path

from local_test.fat_mocked_helper import (
    run_primer_main,
)
from local_test.integrated_helper import (
    create_max_leaps_shape,
    create_min_leaps_shape,
    create_two_envs_shape,
    create_two_envs_shape_with_env_selector,
)
from local_test.version_gate import skip_if_proto_kernel_older_than
from local_test.name_assertion import (
    assert_test_func_name_embeds_str,
    assert_test_module_name_embeds_str,
)
from protoprimer.primer_kernel import (
    _ConfConstClient,
    _ExecOperation,
    _SyntaxArg,
    _TopDir,
)


def test_relationship():
    assert_test_module_name_embeds_str(_ExecOperation.op_eval.value)


def test_op_eval_with_min_leaps_shape(tmp_path: Path):

    assert_test_func_name_embeds_str(_ExecOperation.op_eval.value)

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_min_leaps_shape(tmp_path)

    # when:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            _ExecOperation.op_eval.value,
        ]
    )

    # then:
    # no installation happened:

    assert not os.path.exists(ref_root_abs_path / _TopDir.dir_venv.value)
    assert not os.path.exists(ref_root_abs_path / _TopDir.dir_cache.value)


def test_op_eval_with_max_leaps_shape(tmp_path: Path):

    assert_test_func_name_embeds_str(_ExecOperation.op_eval.value)

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        project_dir_abs_path,
    ) = create_max_leaps_shape(tmp_path)

    # when:

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            _ExecOperation.op_eval.value,
        ]
    )

    # then:
    # no installation happened:

    assert not os.path.exists(ref_root_abs_path / _TopDir.dir_venv.value)
    assert not os.path.exists(ref_root_abs_path / _TopDir.dir_cache.value)


def test_op_eval_env_overrides_persisted_env_without_changing_it(tmp_path: Path):
    """
    FT_03_31_63_70.environment_selection.md: `_ExecOperation.op_eval` + persisted env + `--env` mismatch = override.
    """

    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    assert_test_func_name_embeds_str(_ExecOperation.op_eval.value)

    # given:
    # the default env is persisted:

    two_envs_shape = create_two_envs_shape(tmp_path)
    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name
    os.symlink(
        two_envs_shape.default_env_dir_abs_path.name,
        env_link_abs_path,
    )

    # when:
    # evaluate another env (does not fail with the mismatch):

    run_primer_main(
        [
            str(two_envs_shape.proto_kernel_abs_path),
            _ExecOperation.op_eval.value,
            _SyntaxArg.arg_env,
            two_envs_shape.special_env_dir_abs_path.name,
        ]
    )

    # then:
    # the persisted env is not changed and nothing is installed:

    assert os.readlink(env_link_abs_path) == two_envs_shape.default_env_dir_abs_path.name
    assert not two_envs_shape.default_venv_abs_path.exists()
    assert not two_envs_shape.special_venv_abs_path.exists()


def test_op_eval_does_not_create_env_link(tmp_path: Path):
    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    assert_test_func_name_embeds_str(_ExecOperation.op_eval.value)

    # given:
    # nothing is persisted:

    two_envs_shape = create_two_envs_shape(tmp_path)
    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name

    # when:
    # evaluate the default env, then another env:

    run_primer_main(
        [
            str(two_envs_shape.proto_kernel_abs_path),
            _ExecOperation.op_eval.value,
        ]
    )
    run_primer_main(
        [
            str(two_envs_shape.proto_kernel_abs_path),
            _ExecOperation.op_eval.value,
            _SyntaxArg.arg_env,
            two_envs_shape.special_env_dir_abs_path.name,
        ]
    )

    # then:
    # only `op_boot` and `op_reset` persist the env:

    assert not os.path.lexists(env_link_abs_path)


def test_op_eval_with_env_selector_overrides_persisted_env_without_changing_it(tmp_path: Path):
    """
    FT_03_31_63_70.environment_selection.md: `_ExecOperation.op_eval` + persisted env + selector mismatch = override.
    """

    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    assert_test_func_name_embeds_str(_ExecOperation.op_eval.value)

    # given:
    # the default env is persisted, but the selector selects the special env:

    two_envs_shape = create_two_envs_shape_with_env_selector(tmp_path, "special_env")
    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name
    os.symlink(
        two_envs_shape.default_env_dir_abs_path.name,
        env_link_abs_path,
    )

    # when:
    # evaluate without `--env` (does not fail with the mismatch):

    run_primer_main(
        [
            str(two_envs_shape.proto_kernel_abs_path),
            _ExecOperation.op_eval.value,
        ]
    )

    # then:
    # the persisted env is not changed and nothing is installed:

    assert os.readlink(env_link_abs_path) == two_envs_shape.default_env_dir_abs_path.name
    assert not two_envs_shape.default_venv_abs_path.exists()
    assert not two_envs_shape.special_venv_abs_path.exists()


def test_op_eval_with_env_selector_does_not_create_env_link(tmp_path: Path):
    """
    FT_03_31_63_70.environment_selection.md: `_ExecOperation.op_eval` + env is not persisted = run (nothing persisted).
    """

    # `proto_kernel.py` older than this does not have the behavior (see `old_proto_on_new_venv`):
    skip_if_proto_kernel_older_than("0.15.0")

    assert_test_func_name_embeds_str(_ExecOperation.op_eval.value)

    # given:
    # nothing is persisted, the selector selects the special env:

    two_envs_shape = create_two_envs_shape_with_env_selector(tmp_path, "special_env")
    env_link_abs_path = two_envs_shape.ref_root_abs_path / _ConfConstClient.default_dir_rel_path_leap_env_link_name

    # when:

    run_primer_main(
        [
            str(two_envs_shape.proto_kernel_abs_path),
            _ExecOperation.op_eval.value,
        ]
    )

    # then:

    assert not os.path.lexists(env_link_abs_path)
