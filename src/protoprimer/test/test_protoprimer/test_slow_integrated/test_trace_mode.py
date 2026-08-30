import os
import stat
import subprocess
import sys
from pathlib import Path

from local_doc import cmd_start_app_example
from local_test.fat_mocked_helper import (
    assert_editable_install,
    run_primer_main,
)
from local_test.integrated_helper import (
    create_max_layout,
    test_package_name,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    EnvVar,
    StateStride,
    ExecOperation,
    SyntaxArg,
)
from protoprimer.proto_generator import generate_entry_script_content


def test_relationship():
    assert_test_module_name_embeds_str("trace_mode")


def test_trace_mode_boot_env(tmp_path: Path):
    """
    FT_41_45_81_49.trace_mode.md:
    Full boot with PROTOPRIMER_TRACE_EXECUTION=true.
    """

    # given:
    # fresh max layout boot environment

    (
        proto_kernel_abs_path,
        _ref_root_abs_path,
        project_dir_abs_path,
    ) = create_max_layout(tmp_path)

    stdout_log_path = tmp_path / "trace.stdout.log"
    stderr_log_path = tmp_path / "trace.stderr.log"

    env = os.environ.copy()
    env[EnvVar.var_PROTOPRIMER_TRACE_EXECUTION.value] = "true"

    # when:
    # boot with trace propagating across all python restarts via `PROTOPRIMER_TRACE_EXECUTION`

    with stdout_log_path.open("w") as stdout_f, stderr_log_path.open("w") as stderr_f:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "trace",
                "--trace",
                str(proto_kernel_abs_path),
                SyntaxArg.arg_v,
                SyntaxArg.arg_v,
            ],
            check=True,
            env=env,
            stdout=stdout_f,
            stderr=stderr_f,
        )

    stderr_lines = stderr_log_path.read_text().splitlines()
    stdout_lines = stdout_log_path.read_text().splitlines()

    # then:
    # every `StateStride` name appears in `stderr` log context

    for stride in StateStride:
        assert any(stride.name in stderr_line for stderr_line in stderr_lines), f"expected stride {stride.name} in stderr log"

    # restart count in `stderr` must equal `switch_python` trace count in `stdout`:
    # *   each `os.execve` restart logs "<<< restart >>>" to `stderr`
    # *   each call to `switch_python` is traced to `stdout`
    restart_count = sum(1 for stderr_line in stderr_lines if "<<< restart >>>" in stderr_line)
    assert restart_count >= 1, "expected at least one python restart"
    switch_python_count = sum(1 for stdout_line in stdout_lines if "funcname: switch_python" in stdout_line)
    # equality verifies trace was re-injected via `exec_argv` on every restart
    assert restart_count == switch_python_count, f"restart count [{restart_count}] != switch_python trace count [{switch_python_count}]: " f"trace was not propagated to all python restarts"

    # boot completed successfully
    assert_editable_install(project_dir_abs_path, test_package_name)


def test_trace_mode_start_app(tmp_path: Path):
    """
    FT_41_45_81_49.trace_mode.md:
    start_app run with PROTOPRIMER_TRACE_EXECUTION=true.
    """

    # given:
    # full layout + boot (no trace) to create the configured `venv`

    (
        proto_kernel_abs_path,
        ref_root_abs_path,
        _project_dir_abs_path,
    ) = create_max_layout(tmp_path)

    run_primer_main(
        [
            str(proto_kernel_abs_path),
            SyntaxArg.arg_v,
            SyntaxArg.arg_v,
        ]
    )

    # create `start_app` entry script
    start_app_script_abs_path = ref_root_abs_path / "start_app"
    start_app_script_content = generate_entry_script_content(
        ExecOperation.op_start.value,
        str(proto_kernel_abs_path),
        str(start_app_script_abs_path),
        f"{cmd_start_app_example.__name__}",
        f"{cmd_start_app_example.custom_start_app_main.__name__}",
        {},
    )
    with open(start_app_script_abs_path, "w") as f:
        f.write(start_app_script_content)
    start_app_script_abs_path.chmod(start_app_script_abs_path.stat().st_mode | stat.S_IEXEC)

    stdout_log_path = tmp_path / "trace_start_app.stdout.log"
    stderr_log_path = tmp_path / "trace_start_app.stderr.log"

    env = os.environ.copy()
    env[EnvVar.var_PROTOPRIMER_TRACE_EXECUTION.value] = "true"

    # when:
    # `start_app` with trace propagating across the single `python` restart

    with stdout_log_path.open("w") as stdout_f, stderr_log_path.open("w") as stderr_f:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "trace",
                "--trace",
                str(start_app_script_abs_path),
            ],
            check=True,
            env=env,
            stdout=stdout_f,
            stderr=stderr_f,
        )

    stderr_lines = stderr_log_path.read_text().splitlines()
    stdout_lines = stdout_log_path.read_text().splitlines()

    # then:
    # `custom_start_app_main` ran successfully despite trace mode

    assert any("Hello, world!" in stdout_line for stdout_line in stdout_lines)

    restart_count = sum(1 for stderr_line in stderr_lines if "<<< restart >>>" in stderr_line)
    switch_python_count = sum(1 for stdout_line in stdout_lines if "funcname: switch_python" in stdout_line)
    # restart count (stderr) == switch_python trace count (stdout) == 1:
    assert restart_count == switch_python_count == 1, f"restart [{restart_count}] != switch_python [{switch_python_count}] != 1: " f"trace was not propagated to the single python restart"
