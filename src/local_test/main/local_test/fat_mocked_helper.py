import copy
import os
import subprocess
import sys
from contextlib import contextmanager
from unittest.mock import patch

from pyfakefs.fake_filesystem import FakeFilesystem

import protoprimer
from protoprimer.primer_kernel import (
    EnvVar,
    main,
)


@contextmanager
def fat_mock_wrapper(fs: FakeFilesystem):
    """
    This wrapper allows running some of the `test_slow_integrated` tests as `test_fast_fat_min_mocked` ones.

    The test preparation of the `test_slow_integrated` test is "sandwiched" as:
    *   call this `fat_mock_wrapper` from a new test cass
    *   call the old `integrated_test` test case (to reuse it)
    *   call `run_primer_main` (which selects the test mode) from the old `integrated_test` test case

    See also `test_perimeter.md` and `test_fast_fat_min_mocked`.
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
        env_dir,
        **kwargs,
    ):
        # Create the venv directory and the python executable within it
        fs.create_dir(f"{env_dir}/bin")
        fs.create_file(f"{env_dir}/bin/python", contents="# whatever")

    with (
        patch("sys.exit", side_effect=_mock_exit),
        patch("os.execv", side_effect=_mock_execv),
        patch("os.execve", side_effect=_mock_execve),
        patch("subprocess.check_call", return_value=0),
        patch("venv.create", side_effect=_mock_create_venv),
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

    See also `test_perimeter.md` and `test_fast_fat_min_mocked`.

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

    See also `test_perimeter.md` and `test_fast_fat_min_mocked`.
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
                    main()
            break
        except _ExecCalled as e:
            exec_args, exec_kwargs = e.args
            if "argv" in exec_kwargs:
                cli_args = exec_kwargs["argv"]
            else:
                cli_args = exec_args[1]
            if "env" in exec_kwargs:
                mocked_env = exec_kwargs["env"]

            # As long as `python` is invoked, remove 0-indexed arg:
            assert "python" in cli_args[0]
            cli_args = cli_args[1:]
        except _ExitCalled as e:
            exec_args, exec_kwargs = e.args
            assert exec_args[0] == 0
            break
