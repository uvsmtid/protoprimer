import os
import sys
from io import StringIO
from unittest.mock import (
    MagicMock,
    patch,
)

from local_repo import graph_printer
from local_repo.cmd_print_graph import custom_main
from local_repo.graph_printer import GraphPrinter
from local_test.base_test_class import BaseTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str


def test_relationship():
    assert_test_module_name_embeds_str(
        graph_printer.__name__.split(".")[-1],
    )


# noinspection PyMethodMayBeStatic
class ThisTestClass(BaseTestClass):

    def test_print_dag_default(self):

        # given:

        test_args = [
            # whatever:
            os.path.basename(graph_printer.__file__),
        ]

        # when:

        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            with patch.object(sys, "argv", test_args):
                custom_main()

        # then:

        # do not assert huge output - if it does not fail, that is enough

    @patch(f"{sys.__name__}.stdout", new_callable=StringIO)
    def test_print_dag_already_printed(self, fake_stdout):
        # given:
        mock_state_graph = MagicMock()
        mock_node_a = MagicMock()
        mock_node_a.get_state_name.return_value = "A"
        mock_node_a.get_parent_states.return_value = []

        mock_state_graph.state_nodes = {
            "A": mock_node_a,
        }

        graph_printer = GraphPrinter(mock_state_graph)
        graph_printer.already_printed.add("A")

        # when:
        graph_printer.execute_strategy(mock_node_a)

        # then:
        # already printed node is not printed:
        stdout_text = fake_stdout.getvalue()
        self.assertEqual("", stdout_text)
