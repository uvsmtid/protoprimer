# FT_41_45_81_49.trace_mode.md
import pathlib

from local_repo.sub_proc_util import get_command_code
from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.repo_tree import change_to_known_repo_path
from protoprimer.primer_kernel import EnvVar


def test_relationship():
    assert_test_module_name_embeds_str("trace_mode")


def test_trace_mode(tmp_path: pathlib.Path):
    """
    FT_41_45_81_49.trace_mode.md:
    Run with PROTOPRIMER_TRACE_EXECUTION=true and verify:
    - python restarts include -m trace --trace in exec_argv (stderr log)
    - restart log lines appear in stderr
    - Python trace output (--- modulename:) appears in stdout
    """
    stderr_log_path = tmp_path / "stderr.log"
    stdout_log_path = tmp_path / "stdout.log"

    with change_to_known_repo_path("."):
        get_command_code(
            f"./cmd/print_graph -h > {stdout_log_path} 2> {stderr_log_path}",
            env_vars={
                EnvVar.var_PROTOPRIMER_TRACE_EXECUTION.value: "true",
            },
        )

    stderr_lines = stderr_log_path.read_text().splitlines()
    stdout_lines = stdout_log_path.read_text().splitlines()

    # Restart was logged by switch_python (goes to stderr):
    assert any("<<< restart >>>" in line for line in stderr_lines), "expected at least one python restart log line in stderr"

    # Trace args were injected into exec_argv for the restarted python (stderr log):
    assert any("'-m', 'trace', '--trace'" in line for line in stderr_lines), "expected exec_argv to contain -m trace --trace in stderr"

    # Python trace module output is present in stdout:
    assert any("--- modulename:" in line for line in stdout_lines), "expected Python trace output (--- modulename: ...) in stdout"
