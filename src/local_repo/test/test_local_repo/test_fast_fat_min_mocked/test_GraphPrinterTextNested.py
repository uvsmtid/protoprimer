import sys
from io import StringIO
from unittest.mock import (
    MagicMock,
    patch,
)

from local_repo.graph_printer import GraphPrinterTextNested
from local_test.name_assertion import assert_test_module_name_embeds_str


def test_relationship():
    assert_test_module_name_embeds_str(GraphPrinterTextNested.__name__)


@patch(
    "sys.stdout",
    new_callable=StringIO,
)
def test_print_dag_text_already_printed(fake_stdout):

    # given:

    mock_state_graph = MagicMock()
    mock_node_a = MagicMock()
    mock_node_a.get_state_name.return_value = "A"
    mock_node_a.get_parent_states.return_value = []

    mock_state_graph.state_nodes = {
        "A": mock_node_a,
    }

    graph_printer_text = GraphPrinterTextNested(mock_state_graph)
    graph_printer_text.already_printed.add("A")

    # when:

    graph_printer_text.execute_strategy(mock_node_a)

    # then:

    # already printed node is not printed:
    stdout_text = fake_stdout.getvalue()

    if stdout_text != "":
        raise AssertionError(f"Expected empty string, got `{stdout_text}`")
