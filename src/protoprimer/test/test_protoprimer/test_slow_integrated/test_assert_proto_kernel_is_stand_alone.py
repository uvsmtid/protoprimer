from __future__ import annotations

import os
import pathlib
import platform
import shutil
import subprocess
import sys
import textwrap

import pytest

import protoprimer
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    assert_proto_kernel_is_stand_alone,
    ConfConstGeneral,
    ConfConstInput,
    VenvDriverPip,
)


def test_relationship():
    assert_test_module_name_embeds_str(assert_proto_kernel_is_stand_alone.__name__)


@pytest.fixture(scope="module")
def installed_venv(tmp_path_factory) -> tuple[str, str, dict[str, str]]:
    """
    Create a venv with protoprimer installed (non-editable) into site-packages.
    """
    tmp_path = tmp_path_factory.mktemp("protoprimer_installed_venv")
    venv_dir = tmp_path / "venv"

    venv_driver = VenvDriverPip(
        required_python_version=platform.python_version(),
        selected_python_file_abs_path=sys.executable,
        state_local_venv_dir_abs_path_inited=str(venv_dir),
    )
    venv_driver.create_venv(str(venv_dir))

    venv_python_abs_path = str(venv_dir / ConfConstGeneral.file_rel_path_venv_python)

    # Strip `PYTHONPATH` so subprocess uses only the fresh venv, not the editable source:
    clean_env = os.environ.copy()
    clean_env.pop(ConfConstInput.ext_env_var_PYTHONPATH, None)

    # Install `protoprimer` (non-editable) so primer_kernel.py lands in site-packages:
    protoprimer_project_dir = pathlib.Path(str(protoprimer.__file__)).parent.parent.parent
    subprocess.check_call(
        [
            venv_python_abs_path,
            "-m",
            "pip",
            "install",
            str(protoprimer_project_dir),
        ],
        env=clean_env,
    )

    command_output = subprocess.check_output(
        [
            venv_python_abs_path,
            "-c",
            textwrap.dedent(
                """
                import protoprimer.primer_kernel
                print(protoprimer.primer_kernel.__file__)
                """,
            ),
        ],
        env=clean_env,
    )
    primer_kernel_abs_path_in_venv = command_output.decode().strip()

    return (
        venv_python_abs_path,
        primer_kernel_abs_path_in_venv,
        clean_env,
    )


def _run_stand_alone_check(
    venv_python_abs_path: str,
    path_to_check: str,
    env: dict,
) -> subprocess.CompletedProcess:
    script_body = textwrap.dedent(
        f"""
        from protoprimer.primer_kernel import assert_proto_kernel_is_stand_alone
        assert_proto_kernel_is_stand_alone({repr(path_to_check)})
        """,
    )
    return subprocess.run(
        [
            venv_python_abs_path,
            "-c",
            script_body,
        ],
        capture_output=True,
        text=True,
        env=env,
    )


def test_assert_proto_kernel_is_stand_alone_passes_for_standalone_copy(
    installed_venv,
    tmp_path: pathlib.Path,
):
    """
    Expect no `AssertionError` because `proto_kernel.py` is outside `site-packages`.
    """

    # given:

    (
        venv_python_abs_path,
        primer_kernel_abs_path_in_venv,
        clean_env,
    ) = installed_venv

    standalone_copy = tmp_path / ConfConstGeneral.default_proto_code_basename
    shutil.copy(
        primer_kernel_abs_path_in_venv,
        standalone_copy,
    )

    # when:

    run_proc = _run_stand_alone_check(
        venv_python_abs_path,
        str(standalone_copy),
        clean_env,
    )

    # then:

    if run_proc.returncode != 0:
        raise AssertionError(run_proc.stderr)


def test_assert_proto_kernel_is_stand_alone_raises_for_primer_kernel_in_venv(
    installed_venv,
):
    """
    Expect `AssertionError` because `protoprimer.primer_kernel` is inside `venv`.
    """

    # given:

    (
        venv_python_abs_path,
        primer_kernel_abs_path_in_venv,
        clean_env,
    ) = installed_venv

    # when:

    run_proc = _run_stand_alone_check(
        venv_python_abs_path,
        primer_kernel_abs_path_in_venv,
        clean_env,
    )

    # then:

    assert run_proc.returncode != 0
    assert "AssertionError" in run_proc.stderr
    assert "cannot be from site packages" in run_proc.stderr
