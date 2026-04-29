import sys
from io import StringIO
from unittest.mock import (
    MagicMock,
    patch,
)

from local_repo.cmd_print_graph import custom_main
from local_repo.graph_printer import (
    compose_python_output,
    GraphPrinterPython,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    EnvState,
    TargetState,
)


def test_relationship():
    assert_test_module_name_embeds_str(GraphPrinterPython.__name__)


@patch(
    "sys.stdout",
    new_callable=StringIO,
)
@patch("local_repo.cmd_print_graph.get_transitive_dependencies")
@patch("local_repo.cmd_print_graph.EnvContext")
@patch.object(
    sys,
    "argv",
    [
        "cmd",
        "--format",
        "python",
        "--target_state",
        TargetState.target_proto_bootstrap_completed.name,
    ],
)
def test_print_dag_python_output(
    mock_env_ctx_class,
    mock_get_trans,
    fake_stdout,
):

    # given:

    mock_env_ctx = mock_env_ctx_class.return_value
    mock_state_graph = mock_env_ctx.state_graph
    mock_state_node = MagicMock()
    mock_state_node.get_state_name.return_value = EnvState.state_args_parsed.name
    mock_state_graph.get_state_node.return_value = mock_state_node

    mock_get_trans.return_value = [
        EnvState.state_input_py_exec_var_loaded.name,
        EnvState.state_input_stderr_log_level_var_loaded.name,
    ]

    # when:

    custom_main()

    # then:

    stdout_text = fake_stdout.getvalue()
    exec_namespace: dict = {}
    exec(
        compile(
            stdout_text,
            "<generated>",
            "exec",
        ),
        exec_namespace,
    )
    exec_result = exec_namespace["get_env_states"]()

    expected_list = [
        EnvState.state_input_py_exec_var_loaded,
        EnvState.state_input_stderr_log_level_var_loaded,
        EnvState.state_args_parsed,
    ]

    if exec_result != expected_list:
        raise AssertionError(f"Expected `{expected_list}`, got `{exec_result}`")


def test_compose_python_output_is_executable():

    # given:

    state_names = [
        EnvState.state_input_py_exec_var_loaded.name,
        EnvState.state_input_stderr_log_level_var_loaded.name,
        EnvState.state_args_parsed.name,
    ]

    # when:

    code_str = compose_python_output(state_names)

    # then:

    exec_namespace: dict = {}
    exec(
        compile(
            code_str,
            "<generated>",
            "exec",
        ),
        exec_namespace,
    )
    exec_result = exec_namespace["get_env_states"]()

    expected_list = [
        EnvState.state_input_py_exec_var_loaded,
        EnvState.state_input_stderr_log_level_var_loaded,
        EnvState.state_args_parsed,
    ]

    if exec_result != expected_list:
        raise AssertionError(f"Expected `{expected_list}`, got `{exec_result}`")
