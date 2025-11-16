from __future__ import annotations

import pytest

from protoprimer.primer_kernel import (
    EnvContext,
    StateGraph,
    StateNode,
)
from .graph_utils import (
    get_transitive_dependencies,
    topological_sort,
)


class TestTopologicalSort:

    def test_empty_graph(self):
        state_graph = StateGraph()
        sorted_nodes = topological_sort(state_graph)
        assert sorted_nodes == []

    def test_single_node_graph(self):
        # given:
        env_context_instance = EnvContext()
        state_graph_instance = env_context_instance.state_graph
        # Clear default nodes for this specific test
        state_graph_instance.state_nodes = {}

        class DummyStateNode(StateNode):
            def __init__(self, env_context_param, state_name_param):
                super().__init__(env_context_param, [], state_name_param)

            def _eval_own_state(self):
                return None

        node_a_instance = DummyStateNode(env_context_instance, "A")
        state_graph_instance.register_node(node_a_instance)

        # when:
        sorted_nodes = topological_sort(state_graph_instance)

        # then:
        assert sorted_nodes == ["A"]

    def test_simple_dag(self):
        # given:
        env_context_instance = EnvContext()
        state_graph_instance = env_context_instance.state_graph
        state_graph_instance.state_nodes = {}

        class DummyStateNode(StateNode):
            def __init__(
                self, env_context_param, parent_states_param, state_name_param
            ):
                super().__init__(
                    env_context_param, parent_states_param, state_name_param
                )

            def _eval_own_state(self):
                return None

        node_a_instance = DummyStateNode(env_context_instance, [], "A")
        node_b_instance = DummyStateNode(env_context_instance, ["A"], "B")
        node_c_instance = DummyStateNode(env_context_instance, ["A"], "C")
        node_d_instance = DummyStateNode(env_context_instance, ["B", "C"], "D")

        state_graph_instance.register_node(node_a_instance)
        state_graph_instance.register_node(node_b_instance)
        state_graph_instance.register_node(node_c_instance)
        state_graph_instance.register_node(node_d_instance)

        # when:
        sorted_nodes = topological_sort(state_graph_instance)

        # then:
        # A, B, C, D or A, C, B, D are valid topological sorts
        assert sorted_nodes.index("A") < sorted_nodes.index("B")
        assert sorted_nodes.index("A") < sorted_nodes.index("C")
        assert sorted_nodes.index("B") < sorted_nodes.index("D")
        assert sorted_nodes.index("C") < sorted_nodes.index("D")
        assert len(sorted_nodes) == 4

    def test_complex_dag(self):
        # given:
        env_context_instance = EnvContext()
        state_graph_instance = env_context_instance.state_graph
        state_graph_instance.state_nodes = {}

        class DummyStateNode(StateNode):
            def __init__(
                self, env_context_param, parent_states_param, state_name_param
            ):
                super().__init__(
                    env_context_param, parent_states_param, state_name_param
                )

            def _eval_own_state(self):
                return None

        node_f_instance = DummyStateNode(env_context_instance, [], "F")
        node_e_instance = DummyStateNode(env_context_instance, [], "E")
        node_d_instance = DummyStateNode(env_context_instance, ["F", "E"], "D")
        node_c_instance = DummyStateNode(env_context_instance, ["D"], "C")
        node_b_instance = DummyStateNode(env_context_instance, ["D"], "B")
        node_a_instance = DummyStateNode(env_context_instance, ["B", "C"], "A")

        state_graph_instance.register_node(node_f_instance)
        state_graph_instance.register_node(node_e_instance)
        state_graph_instance.register_node(node_d_instance)
        state_graph_instance.register_node(node_c_instance)
        state_graph_instance.register_node(node_b_instance)
        state_graph_instance.register_node(node_a_instance)

        # when:
        sorted_nodes = topological_sort(state_graph_instance)

        # then:
        # F, E must come before D
        assert sorted_nodes.index("F") < sorted_nodes.index("D")
        assert sorted_nodes.index("E") < sorted_nodes.index("D")
        # D must come before C and B
        assert sorted_nodes.index("D") < sorted_nodes.index("C")
        assert sorted_nodes.index("D") < sorted_nodes.index("B")
        # C and B must come before A
        assert sorted_nodes.index("C") < sorted_nodes.index("A")
        assert sorted_nodes.index("B") < sorted_nodes.index("A")
        assert len(sorted_nodes) == 6

    def test_cycle_detection(self):
        # given:
        env_context_instance = EnvContext()
        state_graph_instance = env_context_instance.state_graph
        state_graph_instance.state_nodes = {}

        class DummyStateNode(StateNode):
            def __init__(
                self, env_context_param, parent_states_param, state_name_param
            ):
                super().__init__(
                    env_context_param, parent_states_param, state_name_param
                )

            def _eval_own_state(self):
                return None

        node_a_instance = DummyStateNode(env_context_instance, ["B"], "A")
        node_b_instance = DummyStateNode(env_context_instance, ["A"], "B")

        state_graph_instance.register_node(node_a_instance)
        state_graph_instance.register_node(node_b_instance)

        # when:
        # then:
        with pytest.raises(ValueError, match="cycle detected in graph"):
            topological_sort(state_graph_instance)

    def test_self_loop_cycle_detection(self):
        # given:
        env_context_instance = EnvContext()
        state_graph_instance = env_context_instance.state_graph
        state_graph_instance.state_nodes = {}

        class DummyStateNode(StateNode):
            def __init__(
                self, env_context_param, parent_states_param, state_name_param
            ):
                super().__init__(
                    env_context_param, parent_states_param, state_name_param
                )

            def _eval_own_state(self):
                return None

        node_a_instance = DummyStateNode(env_context_instance, ["A"], "A")

        state_graph_instance.register_node(node_a_instance)

        # when:
        # then:
        with pytest.raises(ValueError, match="cycle detected in graph"):
            topological_sort(state_graph_instance)

    def test_node_not_found(self):
        # given:
        env_context_instance = EnvContext()
        state_graph_instance = env_context_instance.state_graph
        state_graph_instance.state_nodes = {}

        class DummyStateNode(StateNode):
            def __init__(
                self, env_context_param, parent_states_param, state_name_param
            ):
                super().__init__(
                    env_context_param, parent_states_param, state_name_param
                )

            def _eval_own_state(self):
                return None

        node_a_instance = DummyStateNode(env_context_instance, ["B"], "A")
        state_graph_instance.register_node(node_a_instance)

        # when:
        # then:
        with pytest.raises(ValueError, match="`StateNode` \[B\] not found in graph"):
            topological_sort(state_graph_instance)


class TestGetTransitiveDependencies:

    def test_simple_dag(self):

        # given:

        env_context_instance = EnvContext()
        state_graph_instance = env_context_instance.state_graph
        state_graph_instance.state_nodes = {}

        class DummyStateNode(StateNode):
            def __init__(
                self, env_context_param, parent_states_param, state_name_param
            ):
                super().__init__(
                    env_context_param, parent_states_param, state_name_param
                )

            def _eval_own_state(self):
                return None

        node_a_instance = DummyStateNode(env_context_instance, [], "A")
        node_b_instance = DummyStateNode(env_context_instance, ["A"], "B")
        node_c_instance = DummyStateNode(env_context_instance, ["A"], "C")
        node_d_instance = DummyStateNode(env_context_instance, ["B", "C"], "D")

        state_graph_instance.register_node(node_a_instance)
        state_graph_instance.register_node(node_b_instance)
        state_graph_instance.register_node(node_c_instance)
        state_graph_instance.register_node(node_d_instance)

        # when:

        trans_dependencies = get_transitive_dependencies(state_graph_instance, "D")

        # then:

        assert set(trans_dependencies) == {"A", "B", "C"}

    def test_complex_dag(self):

        # given:

        env_context_instance = EnvContext()
        state_graph_instance = env_context_instance.state_graph
        state_graph_instance.state_nodes = {}

        class DummyStateNode(StateNode):
            def __init__(
                self, env_context_param, parent_states_param, state_name_param
            ):
                super().__init__(
                    env_context_param, parent_states_param, state_name_param
                )

            def _eval_own_state(self):
                return None

        node_f_instance = DummyStateNode(env_context_instance, [], "F")
        node_e_instance = DummyStateNode(env_context_instance, [], "E")
        node_d_instance = DummyStateNode(env_context_instance, ["F", "E"], "D")
        node_c_instance = DummyStateNode(env_context_instance, ["D"], "C")
        node_b_instance = DummyStateNode(env_context_instance, ["D"], "B")
        node_a_instance = DummyStateNode(env_context_instance, ["B", "C"], "A")

        state_graph_instance.register_node(node_f_instance)
        state_graph_instance.register_node(node_e_instance)
        state_graph_instance.register_node(node_d_instance)
        state_graph_instance.register_node(node_c_instance)
        state_graph_instance.register_node(node_b_instance)
        state_graph_instance.register_node(node_a_instance)

        # when:

        trans_dependencies = get_transitive_dependencies(state_graph_instance, "A")

        # then:

        assert set(trans_dependencies) == {"B", "C", "D", "E", "F"}

    def test_no_dependencies(self):

        # given:

        env_context_instance = EnvContext()
        state_graph_instance = env_context_instance.state_graph
        state_graph_instance.state_nodes = {}

        class DummyStateNode(StateNode):
            def __init__(
                self, env_context_param, parent_states_param, state_name_param
            ):
                super().__init__(
                    env_context_param, parent_states_param, state_name_param
                )

            def _eval_own_state(self):
                return None

        node_a_instance = DummyStateNode(env_context_instance, [], "A")
        state_graph_instance.register_node(node_a_instance)

        # when:

        trans_dependencies = get_transitive_dependencies(state_graph_instance, "A")

        # then:

        assert trans_dependencies == []
