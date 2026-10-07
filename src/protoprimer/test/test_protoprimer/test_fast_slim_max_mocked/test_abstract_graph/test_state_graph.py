import unittest
from unittest.mock import Mock

from protoprimer.primer_kernel import (
    EnvContext,
    StateGraph,
    StateNode,
)


class TestStateGraph(unittest.TestCase):

    def setUp(self):
        self.graph = StateGraph()
        self.env_ctx = EnvContext()

    def test_register_factory(self):
        # given:
        node = Mock(spec=StateNode)
        node.get_state_name.return_value = "A"
        node.create_state_node = Mock(return_value=node)
        factory = node

        # when:
        self.graph.register_factory("A", factory)

        # then:
        self.assertIn("A", self.graph.state_factories)
        self.assertEqual(self.graph.state_factories["A"], factory)

    def test_register_factory_replace(self):
        # given:
        node1 = Mock(spec=StateNode)
        node1.get_state_name.return_value = "A"
        node1.create_state_node = Mock(return_value=node1)
        factory1 = node1
        node2 = Mock(spec=StateNode)
        node2.get_state_name.return_value = "A"
        node2.create_state_node = Mock(return_value=node2)
        factory2 = node2
        self.graph.register_factory("A", factory1)

        # when:
        returned_factory = self.graph.register_factory("A", factory2, replace_existing=True)

        # then:
        self.assertEqual(self.graph.state_factories["A"], factory2)
        self.assertEqual(returned_factory, factory1)

    def test_register_factory_no_replace(self):
        # given:
        node1 = Mock(spec=StateNode)
        node1.get_state_name.return_value = "A"
        node1.create_state_node = Mock(return_value=node1)
        factory1 = node1
        node2 = Mock(spec=StateNode)
        node2.get_state_name.return_value = "A"
        node2.create_state_node = Mock(return_value=node2)
        factory2 = node2
        self.graph.register_factory("A", factory1)

        # when:
        # then:
        with self.assertRaises(AssertionError):
            self.graph.register_factory("A", factory2)

    def test_get_state_node(self):
        # given:
        node = Mock(spec=StateNode)
        node.get_state_name.return_value = "A"
        node.create_state_node = Mock(return_value=node)
        factory = node
        self.graph.register_factory("A", factory)

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
        node.create_state_node = Mock(return_value=node)
        factory = node
        self.graph.register_factory("A", factory)

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
