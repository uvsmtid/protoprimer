"""
The contract of `wrap`: the generated file is executable and runs (the exact text of the entry script is not public interface).

FT_75_87_82_46.entry_script.md
FT_78_72_23_04.backward_compatibility.md
"""

import os
import pathlib
import stat
import subprocess

from local_doc import (
    cmd_boot_env_example,
    cmd_start_app_example,
)
from local_test.fat_mocked_helper import run_primer_main
from local_test.integrated_helper import create_max_leaps_shape
from local_test.name_assertion import (
    assert_test_func_name_embeds_str,
    assert_test_module_name_embeds_str,
)
from protoprimer.primer_kernel import (
    EntryFunc,
    ExecOperation,
    SyntaxArg,
)


def test_relationship():
    assert_test_module_name_embeds_str(ExecOperation.op_wrap.value)


def wrap(
    proto_kernel_abs_path: pathlib.Path,
    entry_func: EntryFunc,
    entry_script_abs_path: pathlib.Path,
    main_func: str,
) -> None:
    run_primer_main(
        [
            str(proto_kernel_abs_path),
            ExecOperation.op_wrap.value,
            entry_func.value,
            SyntaxArg.arg_entry_script_path,
            str(entry_script_abs_path),
            SyntaxArg.arg_main_func,
            main_func,
        ]
    )
    assert entry_script_abs_path.is_file()
    assert os.stat(entry_script_abs_path).st_mode & stat.S_IXUSR


def test_wrap_boot_env_runs(tmp_path: pathlib.Path):

    assert_test_func_name_embeds_str(EntryFunc.func_boot_env.value)

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        _project_dir_abs_path,
    ) = create_max_leaps_shape(tmp_path)

    entry_script_abs_path = ref_root_abs_path / "boot_env"

    wrap(
        proto_kernel_abs_path,
        EntryFunc.func_boot_env,
        entry_script_abs_path,
        f"{cmd_boot_env_example.__name__}:{cmd_boot_env_example.custom_boot_env_main.__name__}",
    )

    # when:

    sub_proc = subprocess.run(
        [str(entry_script_abs_path)],
        capture_output=True,
        text=True,
        check=True,
    )

    # then:

    assert "Hello, world!" in sub_proc.stdout


def test_wrap_start_app_runs(tmp_path: pathlib.Path):

    assert_test_func_name_embeds_str(EntryFunc.func_start_app.value)

    # given:

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        _project_dir_abs_path,
    ) = create_max_leaps_shape(tmp_path)

    # `start_app` requires the existing `venv`:
    run_primer_main(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
        ]
    )

    entry_script_abs_path = ref_root_abs_path / "start_app"

    wrap(
        proto_kernel_abs_path,
        EntryFunc.func_start_app,
        entry_script_abs_path,
        f"{cmd_start_app_example.__name__}:{cmd_start_app_example.custom_start_app_main.__name__}",
    )

    # when:

    sub_proc = subprocess.run(
        [str(entry_script_abs_path)],
        capture_output=True,
        text=True,
        check=True,
    )

    # then:

    assert "Hello, world!" in sub_proc.stdout
