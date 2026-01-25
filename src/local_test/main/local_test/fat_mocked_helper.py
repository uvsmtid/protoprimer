import copy
import os
import pathlib
import subprocess
import sys
from contextlib import contextmanager
from unittest.mock import patch

from pyfakefs.fake_filesystem import FakeFilesystem

import protoprimer
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ConfConstGeneral,
    EnvVar,
    app_main,
    PackageDriverBase,
    PackageDriverPip,
    PackageDriverUv,
)


@contextmanager
def fat_mock_wrapper(fs: FakeFilesystem):
    """
    This wrapper allows running some of the `test_slow_integrated` tests as `test_fast_fat_min_mocked` ones.

    The test preparation of the `test_slow_integrated` test is "sandwiched" as:
    *   call this `fat_mock_wrapper` from a new test cass
    *   call the old `integrated_test` test case (to reuse it)
    *   call `run_primer_main` (which selects the test mode) from the old `integrated_test` test case

    See: FT_83_60_72_19.test_perimeter.md / test_fast_fat_min_mocked
    """

    mock_env = {
        EnvVar.var_PROTOPRIMER_TEST_MODE.value: "",
    }

    # Allow copying the real file in `integrated_test`:
    fs.add_real_file(protoprimer.primer_kernel.__file__)

    def _mock_exit(*args, **kwargs):
        raise _ExitCalled(args, kwargs)

    def _mock_execv(*args, **kwargs):
        raise _ExecCalled(args, kwargs)

    def _mock_execve(*args, **kwargs):
        raise _ExecCalled(args, kwargs)

    def _mock_create_venv(
        venv_dir,
        **kwargs,
    ):
        # Create the `venv` directory and the `python` executable within it:
        fs.create_dir(
            os.path.join(venv_dir, ConfConstGeneral.file_rel_path_venv_bin),
        )
        fs.create_file(
            os.path.join(venv_dir, ConfConstGeneral.file_rel_path_venv_python),
            contents="# whatever",
        )

    def _mock_create_pip_venv(
        self,
        env_dir,
        **kwargs,
    ):
        _mock_create_venv(env_dir, **kwargs)

    def _mock_create_uv_venv(
        self,
        env_dir,
        **kwargs,
    ):
        _mock_create_venv(env_dir, **kwargs)
        # TODO: Make this `venv` pass "Is `uv`-managed `venv`?" check.

    def _mock_install_packages(
        required_python_file_abs_path: str,
        given_packages: list[str],
    ):
        # Translate: "./venv/bin/python" -> "./venv/"
        venv_dir_abs_path = os.path.dirname(
            os.path.dirname(required_python_file_abs_path)
        )
        if "uv" in given_packages:
            fs.create_file(
                os.path.join(venv_dir_abs_path, ConfConstGeneral.file_rel_path_venv_uv),
                contents="# whatever",
            )

    with (
        patch("sys.exit", side_effect=_mock_exit),
        patch("os.execv", side_effect=_mock_execv),
        patch("os.execve", side_effect=_mock_execve),
        patch("subprocess.check_call", return_value=0),
        patch(
            f"{primer_kernel.__name__}.{PackageDriverBase.__name__}.install_packages",
            side_effect=_mock_install_packages,
        ),
        patch(
            f"{protoprimer.primer_kernel.__name__}.{PackageDriverPip.__name__}._create_venv_impl",
            side_effect=_mock_create_pip_venv,
        ),
        patch(
            f"{protoprimer.primer_kernel.__name__}.{PackageDriverUv.__name__}._create_venv_impl",
            side_effect=_mock_create_uv_venv,
        ),
        patch("shutil.move"),
        patch.dict(os.environ, mock_env, clear=False),
    ):
        yield


def run_primer_main(
    cli_args: list[str],
) -> None:
    """
    Run the `proto_code` in different test modes (depending on `EnvVar.var_PROTOPRIMER_TEST_MODE`):
    1.  in a separate process (integrated)
    2.  in a mock for the current process test runner

    See: FT_83_60_72_19.test_perimeter.md / test_fast_fat_min_mocked

    NOTE: When it runs in the 2nd (mock env):
    *   many things have already been mocked by `mocking_wrapper`
    *   all the env preparations have already been done by the test case
    """

    if EnvVar.var_PROTOPRIMER_TEST_MODE.value in os.environ:
        proto_kernel_abs_path = cli_args[0]
        os.environ[EnvVar.var_PROTOPRIMER_PROTO_CODE.value] = proto_kernel_abs_path
        _run_primer_main_in_mock_env(cli_args)
    else:
        subprocess.run(
            args=cli_args,
            check=True,
        )


class _ExecCalled(Exception):
    pass


class _ExitCalled(Exception):
    pass


def _run_primer_main_in_mock_env(
    cli_args: list[str],
):
    """
    This function simulates the execution of the `proto_code` main function.

    It handles intercepted calls to `os.exec*` and `sys.exit` functions
    and ensures the tests continue to in the test runner process.

    See: FT_83_60_72_19.test_perimeter.md / test_fast_fat_min_mocked
    """
    mocked_env = copy.deepcopy(os.environ)
    loop_limit: int = 10

    for _ in range(loop_limit):
        try:
            with patch.dict(
                os.environ,
                mocked_env,
            ):
                with patch.object(
                    sys,
                    "argv",
                    cli_args,
                ):
                    app_main()
            break
        except _ExecCalled as e:
            exec_args, exec_kwargs = e.args

            if "argv" in exec_kwargs:
                cli_args = exec_kwargs["argv"]
            else:
                # `argv` is the next arg to `exec*` function after the path to the executable:
                cli_args = exec_args[1]

            if "env" in exec_kwargs:
                mocked_env = exec_kwargs["env"]

            # As long as `python` is invoked:
            # * remove 0-indexed arg (path to the `python` executable)
            # * remove 1-indexed arg (option `-I`) - see FT_28_25_63_06.isolated_python.md
            assert "python" in cli_args[0]
            assert "-I" == cli_args[1]
            cli_args = cli_args[2:]

        except _ExitCalled as e:
            exec_args, exec_kwargs = e.args
            assert exec_args[0] == 0
            break


def assert_editable_install(
    project_dir_abs_path: pathlib.Path,
    package_name: str,
):
    if os.environ.get(EnvVar.var_PROTOPRIMER_TEST_MODE.value, None) is None:
        egg_info_dir = project_dir_abs_path / f"{package_name}.egg-info"
        assert os.path.isdir(egg_info_dir)
    else:
        # The "editable install" is not invoked - no "*.egg-info" dirs:
        pass
