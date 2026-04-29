import sys
from io import StringIO
from unittest.mock import (
    MagicMock,
    patch,
)

from local_repo.graph_printer import (
    GraphPrinterMermaid,
    SubGraph,
)
from local_test.name_assertion import assert_test_module_name_embeds_str


def test_relationship():
    assert_test_module_name_embeds_str(GraphPrinterMermaid.__name__)


@patch(
    "sys.stdout",
    new_callable=StringIO,
)
@patch("local_repo.graph_printer.StateMeta")
def test_print_dag_mermaid(
    mock_state_meta,
    fake_stdout,
):

    # given:

    mock_state_graph = MagicMock()

    mock_node_a = MagicMock()
    mock_node_a.get_state_name.return_value = "A"
    mock_node_a.get_parent_states.return_value = []

    mock_node_b = MagicMock()
    mock_node_b.get_state_name.return_value = "B"
    mock_node_b.get_parent_states.return_value = ["A"]

    mock_node_c = MagicMock()
    mock_node_c.get_state_name.return_value = "C"
    mock_node_c.get_parent_states.return_value = ["A"]

    mock_node_d = MagicMock()
    mock_node_d.get_state_name.return_value = "D"
    mock_node_d.get_parent_states.return_value = [
        "B",
        "C",
    ]

    mock_state_graph.state_nodes = {
        "A": mock_node_a,
        "B": mock_node_b,
        "C": mock_node_c,
        "D": mock_node_d,
    }

    mock_state_meta.__getitem__.side_effect = {
        "A": MagicMock(value=MagicMock(sub_graph=SubGraph.graph_input)),
        "B": MagicMock(value=MagicMock(sub_graph=SubGraph.graph_input)),
        "C": MagicMock(value=MagicMock(sub_graph=SubGraph.graph_config)),
        "D": MagicMock(value=MagicMock(sub_graph=SubGraph.graph_runtime)),
    }.__getitem__

    graph_printer_mermaid = GraphPrinterMermaid(mock_state_graph)

    # when:

    graph_printer_mermaid.execute_strategy(mock_node_d)

    # then:

    stdout_text = fake_stdout.getvalue()
    expected_output = (
        ""  #
        "graph TD\n"
        '    subgraph "graph_input"\n'
        "        A\n"
        "        B\n"
        "    end\n"
        '    subgraph "graph_config"\n'
        "        C\n"
        "    end\n"
        '    subgraph "graph_runtime"\n'
        "        D\n"
        "    end\n"
        "    A --> B\n"
        "    A --> C\n"
        "    B --> D\n"
        "    C --> D\n"
    )

    if stdout_text != expected_output:
        raise AssertionError(f"Expected `{expected_output}`, got `{stdout_text}`")
