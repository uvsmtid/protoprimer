import sys
from io import StringIO
from unittest.mock import (
    MagicMock,
    patch,
)

from local_repo.cmd_print_graph import custom_main
from local_repo.graph_printer import GraphPrinterTextFlat
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import TargetState


def test_relationship():
    assert_test_module_name_embeds_str(GraphPrinterTextFlat.__name__)


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
        "--layout",
        "flat",
        "--target_state",
        TargetState.target_proto_bootstrap_completed.name,
    ],
)
def test_print_dag_flat_output(
    mock_env_ctx_class,
    mock_get_trans,
    fake_stdout,
):

    # given:

    mock_env_ctx = mock_env_ctx_class.return_value
    mock_state_graph = mock_env_ctx.state_graph
    mock_node = MagicMock()
    mock_node.get_state_name.return_value = "FINAL_STATE"
    mock_state_graph.get_state_node.return_value = mock_node

    mock_get_trans.return_value = [
        "DEP1",
        "DEP2",
    ]

    # when:

    custom_main()

    # then:

    stdout_text = fake_stdout.getvalue()
    expected_output = "DEP1\nDEP2\nFINAL_STATE\n"

    if stdout_text != expected_output:
        raise AssertionError(f"Expected `{expected_output}`, got `{stdout_text}`")
