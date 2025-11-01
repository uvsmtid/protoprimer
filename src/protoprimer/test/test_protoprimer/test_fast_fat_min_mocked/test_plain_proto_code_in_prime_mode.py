import copy
import os
import pathlib
import sys
from unittest.mock import patch

from pyfakefs.fake_filesystem import FakeFilesystem

import protoprimer
from local_test.integrated_helper import (
    create_conf_client_file,
    create_conf_env_file,
    create_conf_primer_file,
    create_plain_proto_code,
    create_test_pyproject_toml,
    switch_to_ref_root_abs_path,
    test_pyproject_src_dir_rel_path,
)
from protoprimer.primer_kernel import (
    ConfConstClient,
    ConfConstGeneral,
    ConfConstInput,
    ConfConstPrimer,
    ConfDst,
    EnvVar,
    main,
    SyntaxArg,
)


class ExecCalled(Exception):
    pass


class ExitCalled(Exception):
    pass


def mock_execv(*args, **kwargs):
    raise ExecCalled(args, kwargs)


def mock_execve(*args, **kwargs):
    raise ExecCalled(args, kwargs)


def mock_exit(*args, **kwargs):
    raise ExitCalled(args, kwargs)


def mock_install_packages(
    self, local_python_file_abs_path: str, given_packages: list[str]
):
    if given_packages == ["uv"]:
        bin_dir = pathlib.Path(local_python_file_abs_path).parent
        bin_dir.mkdir(parents=True, exist_ok=True)
        (bin_dir / "uv").touch()


# @pytest.mark.skip("incomplete & experimental")
# TODO: Figure out a way to run any `test_slow_integrated` wrapped into these mocks
#       without any modifications.
@patch(
    "protoprimer.primer_kernel.PackageDriverPip.install_packages",
    new=mock_install_packages,
)
@patch("sys.exit", side_effect=mock_exit)
@patch("os.execv", side_effect=mock_execv)
@patch("os.execve", side_effect=mock_execve)
@patch("subprocess.check_call", return_value=0)
@patch("venv.create")
@patch("shutil.move")
def test_prime_with_mocked_execv(
    mock_exit_call,
    mock_execv_call,
    mock_execve_call,
    mock_check_call,
    mock_venv_create,
    mock_shutil_move,
    fs: FakeFilesystem,
):
    """
    See `test_perimeter.md` and `test_fast_fat_min_mocked`.
    """

    # given:

    fs.add_real_file(protoprimer.primer_kernel.__file__)

    tmp_dir_abs_path: str = fs.create_dir("/project_dir").path
    tmp_path: pathlib.Path = pathlib.Path(tmp_dir_abs_path)

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    # ===
    proto_code_dir_abs_path = (
        ref_root_abs_path / ConfConstInput.default_proto_conf_dir_rel_path
    )
    proto_code_abs_path = create_plain_proto_code(proto_code_dir_abs_path)
    create_conf_primer_file(
        ref_root_abs_path,
        proto_code_dir_abs_path,
    )

    # ===
    project_dir_abs_path = ref_root_abs_path / test_pyproject_src_dir_rel_path
    create_test_pyproject_toml(project_dir_abs_path)

    # ===
    conf_env_dir_abs_path = (
        ref_root_abs_path / ConfConstClient.default_client_default_env_dir_rel_path
    )
    create_conf_env_file(
        ref_root_abs_path,
        conf_env_dir_abs_path,
        project_dir_abs_path,
    )

    # ===
    conf_client_dir_abs_path = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_dir_rel_path
    )
    create_conf_client_file(
        ref_root_abs_path,
        conf_client_dir_abs_path,
        conf_env_dir_abs_path,
    )

    # ===
    # when:
    mocked_argv = [
        str(proto_code_dir_abs_path / ConfConstGeneral.default_proto_code_basename),
        SyntaxArg.arg_v,
    ]
    mocked_env = copy.deepcopy(os.environ)
    mocked_env[EnvVar.var_PROTOPRIMER_TEST_MODE.value] = ""
    mocked_env[EnvVar.var_PROTOPRIMER_PROTO_CODE.value] = str(proto_code_abs_path)
    for _ in range(10):
        try:
            with patch.dict(
                os.environ,
                mocked_env,
            ):
                with patch.object(
                    sys,
                    "argv",
                    mocked_argv,
                ):
                    main()
                break
        except ExecCalled as e:
            exec_args, exec_kwargs = e.args
            if "argv" in exec_kwargs:
                mocked_argv = exec_kwargs["argv"]
            else:
                mocked_argv = exec_args[1]
            if "env" in exec_kwargs:
                mocked_env = exec_kwargs["env"]

            # As long as `python` is invoked, remove 0-indexed arg:
            assert "python" in mocked_argv[0]
            mocked_argv = mocked_argv[1:]
        except ExitCalled as e:
            exec_args, exec_kwargs = e.args
            assert exec_args[0] == 0
            break

    # then:
    gconf_dir = ref_root_abs_path / ConfDst.dst_global.value
    lconf_dir = ref_root_abs_path / ConfDst.dst_local.value

    conf_primer_file = (
        ref_root_abs_path
        / ConfConstGeneral.name_proto_code
        / ConfConstInput.default_file_basename_conf_primer
    )
    conf_client_file = (
        ref_root_abs_path / ConfConstPrimer.default_client_conf_file_rel_path
    )
    conf_env_file = ref_root_abs_path / ConfConstClient.default_env_conf_file_rel_path

    assert os.path.isdir(gconf_dir) and not os.path.islink(gconf_dir)
    assert os.path.isdir(lconf_dir) and os.path.islink(lconf_dir)

    assert os.path.isfile(conf_primer_file)
    assert os.path.isfile(conf_client_file)
    assert os.path.isfile(conf_env_file)
