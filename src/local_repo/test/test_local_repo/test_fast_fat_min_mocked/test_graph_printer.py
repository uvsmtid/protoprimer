import os
import sys
from io import StringIO
from unittest.mock import (
    MagicMock,
    patch,
)

from local_repo import graph_printer
from local_repo.cmd_print_graph import custom_main
from local_repo.graph_printer import (
    GraphPrinterMermaid,
    GraphPrinterText,
    StateMeta,
    SubGraph,
)
from local_test.base_test_class import BaseTestClass
from local_test.name_assertion import (
    assert_test_module_name_embeds_another_module_name,
)
from protoprimer.primer_kernel import EnvState


def test_relationship():
    assert_test_module_name_embeds_another_module_name(
        graph_printer.__name__,
    )


# noinspection PyMethodMayBeStatic
class ThisTestClass(BaseTestClass):

    def test_state_meta_matches_env_state(self):
        # given:
        env_state_names = [s.name for s in EnvState]
        state_meta_names = [s.name for s in StateMeta]

        # then:
        self.assertEqual(
            env_state_names,
            state_meta_names,
            "StateMeta should define enum item for every EnvState, in the same order, with the same name",
        )

    def test_print_dag_cmd_default(self):

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

    def test_print_dag_cmd_text(self):

        # given:

        test_args = [
            # whatever:
            os.path.basename(graph_printer.__file__),
            "--text",
        ]

        # when:

        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            with patch.object(sys, "argv", test_args):
                custom_main()

        # then:

        # do not assert huge output - if it does not fail, that is enough

    def test_print_dag_cmd_mermaid(self):

        # given:

        test_args = [
            # whatever:
            os.path.basename(graph_printer.__file__),
            "--mermaid",
        ]

        # when:

        with patch("sys.stdout", new=StringIO()) as fake_stdout:
            with patch.object(sys, "argv", test_args):
                custom_main()

        # then:

        # do not assert huge output - if it does not fail, that is enough

    @patch(f"{sys.__name__}.stdout", new_callable=StringIO)
    def test_print_dag_text_already_printed(self, fake_stdout):
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
        self.assertEqual("", stdout_text)

    @patch(f"{sys.__name__}.stdout", new_callable=StringIO)
    @patch("local_repo.graph_printer.StateMeta")
    def test_print_dag_mermaid(self, mock_state_meta, fake_stdout):
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
        mock_node_d.get_parent_states.return_value = ["B", "C"]

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
        self.assertEqual(
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
            "    C --> D\n",
            stdout_text,
        )
