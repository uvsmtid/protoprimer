# FT_41_45_81_49.trace_mode.md
import os
import subprocess
import sys
from pathlib import Path

from local_test.fat_mocked_helper import assert_editable_install
from local_test.integrated_helper import (
    create_max_layout,
    test_package_name,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    EnvVar,
    StateStride,
    SyntaxArg,
)


def test_relationship():
    assert_test_module_name_embeds_str("trace_mode")


def test_trace_mode(tmp_path: Path):
    """
    FT_41_45_81_49.trace_mode.md:
    Full boot with PROTOPRIMER_TRACE_EXECUTION=true.

    Asserts:
    - every StateStride name appears in stderr (protoprimer log context includes stride)
    - restart count in stderr == switch_python trace count in stdout,
      verifying trace propagated across every os.execve restart
    """

    # given: fresh max layout boot environment
    (
        proto_kernel_abs_path,
        _ref_root_abs_path,
        project_dir_abs_path,
    ) = create_max_layout(tmp_path)

    stdout_log_path = tmp_path / "trace.stdout.log"
    stderr_log_path = tmp_path / "trace.stderr.log"

    env = os.environ.copy()
    env[EnvVar.var_PROTOPRIMER_TRACE_EXECUTION.value] = "true"

    # when: boot with trace propagating across all python restarts via PROTOPRIMER_TRACE_EXECUTION
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

    # then: every StateStride name appears in stderr log context
    # (each log line embeds the active stride, e.g. "py:stride_py_venv[3]")
    for stride in StateStride:
        assert any(stride.name in line for line in stderr_lines), f"expected stride {stride.name} in stderr log"

    # restart count (stderr) must equal switch_python trace count (stdout):
    # - each os.execve restart logs "<<< restart >>>" to stderr
    # - each call to switch_python is traced to stdout
    # equality verifies trace was re-injected via exec_argv on every restart
    restart_count = sum(1 for line in stderr_lines if "<<< restart >>>" in line)
    switch_python_count = sum(1 for line in stdout_lines if "funcname: switch_python" in line)

    assert restart_count >= 1, "expected at least one python restart"
    assert restart_count == switch_python_count, f"restart count [{restart_count}] != switch_python trace count [{switch_python_count}]: " f"trace was not propagated to all python restarts"

    # boot completed successfully
    assert_editable_install(project_dir_abs_path, test_package_name)
