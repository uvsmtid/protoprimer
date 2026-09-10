"""
FT_21_75_54_18.instant_scenario.md

Covers the `entry_script` case where `protoprimer` is intentionally NOT declared
as a dependency of the wrapped app - only `proto_kernel.py` is seeded directly,
the way the manual's "instant scenario" demos it.

This is distinct from `test_instant_scenario.py`, which covers "no config files"
but still installs `protoprimer` as a dependency via `create_test_pyproject_toml`.
"""

import pathlib
import stat
import subprocess

from local_test.fat_mocked_helper import run_primer_main
from local_test.integrated_helper import (
    create_plain_proto_code,
    create_python_version_file,
    switch_to_ref_root_abs_path,
    test_python_version,
)
from local_test.toml_handler import save_toml_data
from protoprimer.primer_kernel import (
    ConfConstClient,
    EntryFunc,
    SyntaxArg,
    generate_entry_script_content,
)


def _create_instant_pyproject_toml_without_protoprimer(
    project_dir_abs_path: pathlib.Path,
) -> None:
    """
    Unlike `local_test.integrated_helper.create_test_pyproject_toml`,
    this does not declare `protoprimer` (or any other repo package) as
    a dependency - that absence is the whole point of the instant scenario.
    """

    pyproject_file_abs_path = project_dir_abs_path / ConfConstClient.default_pyproject_toml_basename

    toml_data = {
        "project": {
            "name": "instant-app",
            "version": "0.0.0",
            "dependencies": [],
        },
        "tool": {
            "setuptools": {
                "py-modules": ["some_app"],
            },
        },
    }

    project_dir_abs_path.mkdir(parents=True, exist_ok=True)
    save_toml_data(str(pyproject_file_abs_path), toml_data)


def _create_instant_scenario_without_protoprimer(
    tmp_path: pathlib.Path,
) -> pathlib.Path:
    """
    Flat "instant scenario" layout: `proto_kernel.py` and `pyproject.toml`
    both directly at `ref_root` - see FT_59_95_81_63.tree_shape.md / min leaps shape.
    """

    ref_root_abs_path = switch_to_ref_root_abs_path(tmp_path)

    create_python_version_file(str(ref_root_abs_path), test_python_version)

    _create_instant_pyproject_toml_without_protoprimer(ref_root_abs_path)

    (ref_root_abs_path / "some_app.py").write_text("def some_main():\n" '    print("Hello, world!")\n')

    proto_kernel_abs_path = create_plain_proto_code(ref_root_abs_path)

    return proto_kernel_abs_path


def _generate_and_run_entry_script(
    proto_kernel_abs_path: pathlib.Path,
    entry_func: EntryFunc,
    with_main_func: bool = True,
) -> subprocess.CompletedProcess:

    ref_root_abs_path = proto_kernel_abs_path.parent
    entry_script_abs_path = ref_root_abs_path / entry_func.value

    module_name = "some_app" if with_main_func else None
    func_name = "some_main" if with_main_func else None

    entry_script_content = generate_entry_script_content(
        entry_func.value,
        str(proto_kernel_abs_path),
        str(entry_script_abs_path),
        module_name,
        func_name,
    )
    entry_script_abs_path.write_text(entry_script_content)
    entry_script_abs_path.chmod(entry_script_abs_path.stat().st_mode | stat.S_IEXEC)

    return subprocess.run(
        [str(entry_script_abs_path)],
        cwd=str(ref_root_abs_path),
        capture_output=True,
        text=True,
    )


# FT_39_94_24_00.fat_mock.md
# Not wrapped: needs a real `venv` where `protoprimer` genuinely fails to import.
def test_start_app_entry_script_without_protoprimer_dependency(tmp_path: pathlib.Path):
    """
    `start_app()` must not require `protoprimer` to be importable in the `venv`
    (the `stride_py_venv` branch of `_start_main`).
    """

    proto_kernel_abs_path = _create_instant_scenario_without_protoprimer(tmp_path)

    # `start_app` requires the `venv` to already exist - boot it first:
    run_primer_main(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
        ]
    )

    entry_script_process = _generate_and_run_entry_script(
        proto_kernel_abs_path,
        EntryFunc.func_start_app,
    )

    assert entry_script_process.returncode == 0, entry_script_process.stdout + entry_script_process.stderr
    assert "Hello, world!" in entry_script_process.stdout


# FT_39_94_24_00.fat_mock.md
# Not wrapped: needs a real `venv` where `protoprimer` genuinely fails to import.
def test_boot_env_entry_script_without_protoprimer_dependency(tmp_path: pathlib.Path):
    """
    `boot_env()` must not require `protoprimer` to be importable in the `venv`
    once the app's own dependencies reach `StateStride.stride_deps_updated`
    (the corresponding branch of `_start_main`).
    """

    proto_kernel_abs_path = _create_instant_scenario_without_protoprimer(tmp_path)

    # `boot_env` bootstraps the `venv` itself - no prior boot needed:
    entry_script_process = _generate_and_run_entry_script(
        proto_kernel_abs_path,
        EntryFunc.func_boot_env,
    )

    assert entry_script_process.returncode == 0, entry_script_process.stdout + entry_script_process.stderr
    assert "Hello, world!" in entry_script_process.stdout


# FT_39_94_24_00.fat_mock.md
# Not wrapped: needs a real `venv` where `protoprimer` genuinely fails to import.
def test_boot_env_entry_script_with_empty_main_func(tmp_path: pathlib.Path):
    """
    FT_21_75_54_18.instant_scenario.md:
    `boot_env()` with an empty `--main_func` runs the standard bootstrap
    to completion and calls no `module:function` - so the app's own
    `some_main` must NOT run.
    """

    proto_kernel_abs_path = _create_instant_scenario_without_protoprimer(tmp_path)

    entry_script_process = _generate_and_run_entry_script(
        proto_kernel_abs_path,
        EntryFunc.func_boot_env,
        with_main_func=False,
    )

    assert entry_script_process.returncode == 0, entry_script_process.stdout + entry_script_process.stderr
    assert "Hello, world!" not in entry_script_process.stdout
    assert (proto_kernel_abs_path.parent / "venv").is_dir()
