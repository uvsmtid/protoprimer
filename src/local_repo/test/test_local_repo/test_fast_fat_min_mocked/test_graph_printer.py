import os
import sys
from io import StringIO
from unittest.mock import (
    MagicMock,
    patch,
)

from local_repo import graph_printer
from local_repo.cmd_print_graph import (
    custom_main,
    OutputFormat,
    OutputLayout,
)
from local_repo.graph_printer import (
    GraphPrinterMermaid,
    GraphPrinterText,
    StateMeta,
    SubGraph,
)
from local_test.name_assertion import (
    assert_test_module_name_embeds_another_module_name,
)
from protoprimer.primer_kernel import (
    EnvState,
    TargetState,
)


def test_relationship():
    assert_test_module_name_embeds_another_module_name(graph_printer.__name__)


def test_state_meta_matches_env_state():

    # given:

    env_state_names = [enum_item.name for enum_item in EnvState]
    state_meta_names = [enum_item.name for enum_item in StateMeta]

    # then:

    if env_state_names != state_meta_names:
        raise AssertionError("StateMeta should define enum item for every EnvState, in the same order, with the same name")


@patch("sys.stdout", new_callable=StringIO)
@patch.object(sys, "argv", [os.path.basename(graph_printer.__file__)])
def test_print_dag_cmd_default(fake_stdout):

    # given:

    # when:

    custom_main()

    # then:

    # do not assert huge output - if it does not fail, that is enough


@patch("sys.stdout", new_callable=StringIO)
@patch.object(sys, "argv", [os.path.basename(graph_printer.__file__), "--format", "text"])
def test_print_dag_cmd_text(fake_stdout):

    # given:

    # when:

    custom_main()

    # then:

    # do not assert huge output - if it does not fail, that is enough


@patch("sys.stdout", new_callable=StringIO)
@patch.object(sys, "argv", [os.path.basename(graph_printer.__file__), "--format", "mermaid"])
def test_print_dag_cmd_mermaid(fake_stdout):

    # given:

    # when:

    custom_main()

    # then:

    # do not assert huge output - if it does not fail, that is enough


@patch("sys.stdout", new_callable=StringIO)
@patch.object(sys, "argv", [os.path.basename(graph_printer.__file__), "--layout", "flat"])
def test_print_dag_cmd_layout_flat(fake_stdout):

    # given:

    # when:

    custom_main()

    # then:

    # do not assert huge output - if it does not fail, that is enough


@patch.object(
    sys,
    "argv",
    [
        os.path.basename(graph_printer.__file__),
        "--format",
        "mermaid",
        "--layout",
        "flat",
    ],
)
def test_print_dag_cmd_mermaid_flat_fail():

    # given:

    # when & then:

    try:
        custom_main()
    except ValueError as error_msg:
        expected_message = "Format `mermaid` requires layout `nested`"
        if expected_message not in str(error_msg):
            raise AssertionError(f"Expected `{expected_message}` in `{str(error_msg)}`")
    else:
        raise AssertionError(f"Expected `{ValueError.__name__}` was not raised")


@patch("sys.stdout", new_callable=StringIO)
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


@patch("sys.stdout", new_callable=StringIO)
def test_print_dag_text_already_printed(fake_stdout):

    # given:

    mock_state_graph = MagicMock()
    mock_node_a = MagicMock()
    mock_node_a.get_state_name.return_value = "A"
    mock_node_a.get_parent_states.return_value = []

    mock_state_graph.state_nodes = {
        "A": mock_node_a,
    }

    graph_printer_text = GraphPrinterText(mock_state_graph)
    graph_printer_text.already_printed.add("A")

    # when:

    graph_printer_text.execute_strategy(mock_node_a)

    # then:

    # already printed node is not printed:
    stdout_text = fake_stdout.getvalue()

    if stdout_text != "":
        raise AssertionError(f"Expected empty string, got `{stdout_text}`")


@patch("sys.stdout", new_callable=StringIO)
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
