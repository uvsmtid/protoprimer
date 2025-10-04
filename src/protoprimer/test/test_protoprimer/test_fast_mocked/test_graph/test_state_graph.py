import unittest
from unittest.mock import Mock
from protoprimer.primer_kernel import StateGraph, StateNode


class TestStateGraph(unittest.TestCase):

    def setUp(self):
        self.graph = StateGraph()

    def test_register_node(self):
        # given:
        node = Mock(spec=StateNode)
        node.get_state_name.return_value = "A"

        # when:
        self.graph.register_node(node)

        # then:
        self.assertIn("A", self.graph.state_nodes)
        self.assertEqual(self.graph.state_nodes["A"], node)

    def test_register_node_replace(self):
        # given:
        node1 = Mock(spec=StateNode)
        node1.get_state_name.return_value = "A"
        node2 = Mock(spec=StateNode)
        node2.get_state_name.return_value = "A"
        self.graph.register_node(node1)

        # when:
        returned_node = self.graph.register_node(node2, replace_existing=True)

        # then:
        self.assertEqual(self.graph.state_nodes["A"], node2)
        self.assertEqual(returned_node, node1)

    def test_register_node_no_replace(self):
        # given:
        node1 = Mock(spec=StateNode)
        node1.get_state_name.return_value = "A"
        node2 = Mock(spec=StateNode)
        node2.get_state_name.return_value = "A"
        self.graph.register_node(node1)

        # when:
        # then:
        with self.assertRaises(AssertionError):
            self.graph.register_node(node2)

    def test_get_state_node(self):
        # given:
        node = Mock(spec=StateNode)
        node.get_state_name.return_value = "A"
        self.graph.register_node(node)

        # when:
        retrieved_node = self.graph.get_state_node("A")

        # then:
        self.assertEqual(retrieved_node, node)

    def test_get_state_node_not_found(self):
        # given:
        # an empty graph

        # when/then:
        with self.assertRaises(KeyError):
            self.graph.get_state_node("A")

    def test_eval_state(self):
        # given:
        node = Mock(spec=StateNode)
        node.get_state_name.return_value = "A"
        node.eval_own_state.return_value = "value_A"
        self.graph.register_node(node)

        # when:
        value = self.graph.eval_state("A")

        # then:
        self.assertEqual(value, "value_A")
        node.eval_own_state.assert_called_once()

    def test_eval_state_not_found(self):
        # given:
        # an empty graph

        # when/then:
        with self.assertRaises(KeyError):
            self.graph.eval_state("A")
