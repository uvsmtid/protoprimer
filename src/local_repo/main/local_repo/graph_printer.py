from __future__ import annotations

import dataclasses
import enum

from protoprimer.primer_kernel import (
    EnvState,
    RunStrategy,
    StateGraph,
    StateNode,
)


class SubGraph(enum.Enum):
    graph_input = enum.auto()
    graph_config = enum.auto()
    graph_runtime = enum.auto()


@dataclasses.dataclass
class StateNodeMeta:
    env_state: EnvState
    sub_graph: SubGraph | None


class StateMeta(enum.Enum):
    state_input_stderr_log_level_var_loaded = StateNodeMeta(
        env_state=EnvState.state_input_stderr_log_level_var_loaded,
        sub_graph=SubGraph.graph_input,
    )
    state_input_do_install_var_loaded = StateNodeMeta(
        env_state=EnvState.state_input_do_install_var_loaded,
        sub_graph=SubGraph.graph_input,
    )
    state_default_stderr_log_handler_configured = StateNodeMeta(
        env_state=EnvState.state_default_stderr_log_handler_configured,
        sub_graph=SubGraph.graph_input,
    )
    state_args_parsed = StateNodeMeta(
        env_state=EnvState.state_args_parsed,
        sub_graph=SubGraph.graph_input,
    )
    state_input_wizard_stage_arg_loaded = StateNodeMeta(
        env_state=EnvState.state_input_wizard_stage_arg_loaded,
        sub_graph=SubGraph.graph_input,
    )
    state_input_stderr_log_level_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_input_stderr_log_level_eval_finalized,
        sub_graph=SubGraph.graph_input,
    )
    state_input_run_mode_arg_loaded = StateNodeMeta(
        env_state=EnvState.state_input_run_mode_arg_loaded,
        sub_graph=SubGraph.graph_input,
    )
    state_input_final_state_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_input_final_state_eval_finalized,
        sub_graph=SubGraph.graph_input,
    )
    state_run_mode_executed = StateNodeMeta(
        env_state=EnvState.state_run_mode_executed,
        sub_graph=None,
    )
    state_input_py_exec_var_loaded = StateNodeMeta(
        env_state=EnvState.state_input_py_exec_var_loaded,
        sub_graph=SubGraph.graph_input,
    )
    state_input_start_id_var_loaded = StateNodeMeta(
        env_state=EnvState.state_input_start_id_var_loaded,
        sub_graph=SubGraph.graph_input,
    )
    state_input_proto_code_file_abs_path_var_loaded = StateNodeMeta(
        env_state=EnvState.state_input_proto_code_file_abs_path_var_loaded,
        sub_graph=SubGraph.graph_input,
    )
    state_py_exec_arbitrary_reached = StateNodeMeta(
        env_state=EnvState.state_py_exec_arbitrary_reached,
        sub_graph=SubGraph.graph_input,
    )
    state_input_proto_code_file_abs_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_input_proto_code_file_abs_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_input_proto_code_dir_abs_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_input_proto_code_dir_abs_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_input_proto_conf_primer_file_abs_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_input_proto_conf_primer_file_abs_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_primer_conf_file_data_loaded = StateNodeMeta(
        env_state=EnvState.state_primer_conf_file_data_loaded,
        sub_graph=SubGraph.graph_config,
    )
    state_primer_ref_root_dir_abs_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_primer_ref_root_dir_abs_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_primer_conf_client_file_abs_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_primer_conf_client_file_abs_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_client_conf_file_data_loaded = StateNodeMeta(
        env_state=EnvState.state_client_conf_file_data_loaded,
        sub_graph=SubGraph.graph_config,
    )
    state_client_local_env_conf_dir_rel_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_client_local_env_conf_dir_rel_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_client_conf_env_dir_abs_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_client_conf_env_dir_abs_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_client_link_name_dir_rel_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_client_link_name_dir_rel_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_client_conf_env_file_abs_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_client_conf_env_file_abs_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_env_conf_file_data_loaded = StateNodeMeta(
        env_state=EnvState.state_env_conf_file_data_loaded,
        sub_graph=SubGraph.graph_config,
    )
    state_merged_required_python_file_abs_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_merged_required_python_file_abs_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_merged_local_venv_dir_abs_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_merged_local_venv_dir_abs_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_merged_local_log_dir_abs_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_merged_local_log_dir_abs_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_merged_local_tmp_dir_abs_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_merged_local_tmp_dir_abs_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_merged_local_cache_dir_abs_path_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_merged_local_cache_dir_abs_path_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_merged_project_descriptors_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_merged_project_descriptors_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_merged_package_driver_eval_finalized = StateNodeMeta(
        env_state=EnvState.state_merged_package_driver_eval_finalized,
        sub_graph=SubGraph.graph_config,
    )
    state_merged_conf_data_printed = StateNodeMeta(
        env_state=EnvState.state_merged_conf_data_printed,
        sub_graph=None,
    )
    state_default_file_log_handler_configured = StateNodeMeta(
        env_state=EnvState.state_default_file_log_handler_configured,
        sub_graph=SubGraph.graph_runtime,
    )
    state_py_exec_required_reached = StateNodeMeta(
        env_state=EnvState.state_py_exec_required_reached,
        sub_graph=SubGraph.graph_runtime,
    )
    state_reinstall_triggered = StateNodeMeta(
        env_state=EnvState.state_reinstall_triggered,
        sub_graph=SubGraph.graph_runtime,
    )
    state_package_driver_inited = StateNodeMeta(
        env_state=EnvState.state_package_driver_inited,
        sub_graph=SubGraph.graph_runtime,
    )
    state_py_exec_venv_reached = StateNodeMeta(
        env_state=EnvState.state_py_exec_venv_reached,
        sub_graph=SubGraph.graph_runtime,
    )
    state_protoprimer_package_installed = StateNodeMeta(
        env_state=EnvState.state_protoprimer_package_installed,
        sub_graph=SubGraph.graph_runtime,
    )
    state_version_constraints_generated = StateNodeMeta(
        env_state=EnvState.state_version_constraints_generated,
        sub_graph=SubGraph.graph_runtime,
    )
    state_py_exec_updated_protoprimer_package_reached = StateNodeMeta(
        env_state=EnvState.state_py_exec_updated_protoprimer_package_reached,
        sub_graph=SubGraph.graph_runtime,
    )
    state_proto_code_updated = StateNodeMeta(
        env_state=EnvState.state_proto_code_updated,
        sub_graph=SubGraph.graph_runtime,
    )
    state_py_exec_updated_proto_code = StateNodeMeta(
        env_state=EnvState.state_py_exec_updated_proto_code,
        sub_graph=SubGraph.graph_runtime,
    )
    state_command_executed = StateNodeMeta(
        env_state=EnvState.state_command_executed,
        sub_graph=None,
    )


class GraphPrinterText(RunStrategy):
    """
    This class prints reduced DAG of `EnvState`-s.

    Full DAG for a target may involve the same dependency/parent multiple times.
    Printing each dependency multiple times (with all its transient dependencies) looks excessive.
    Instead, this class prints each dependency/parent only if any of its siblings have not been printed yet.
    Therefore, there is some duplication, but the result is both more concise and less confusing.
    """

    rendered_no_parents: str = "[none]"

    def __init__(
        self,
        state_graph: StateGraph,
    ):
        super().__init__()
        self.state_graph: StateGraph = state_graph
        self.already_printed: set[str] = set()

    def execute_strategy(
        self,
        state_node: StateNode,
    ) -> None:
        self.print_node_parents(
            state_node,
            force_print=False,
            level=0,
        )

    def print_node_parents(
        self,
        state_node,
        force_print: bool,
        level: int,
    ) -> None:
        if state_node.get_state_name() in self.already_printed and not force_print:
            return
        else:
            self.already_printed.add(state_node.get_state_name())

        # Indented name:
        print(
            f"{' ' * level * 4}{state_node.get_state_name()}",
            end="",
        )
        # Dependencies (parents):
        rendered_parent_states: str
        if len(state_node.get_parent_states()) > 0:
            rendered_parent_states = " ".join(state_node.get_parent_states())
        else:
            rendered_parent_states = self.rendered_no_parents
        print(
            f": {rendered_parent_states}",
            end="",
        )
        # new line:
        print()

        # Check ahead if any of the dependencies (parents) are not printed:
        any_parent_to_print: bool = False
        for state_parent in state_node.get_parent_states():
            if state_parent not in self.already_printed:
                any_parent_to_print = True
                break

        # Recurse:
        if any_parent_to_print:
            for state_parent in state_node.get_parent_states():
                self.print_node_parents(
                    self.state_graph.state_nodes[state_parent],
                    # Even if this state was already printed, since we are printing siblings, print them all:
                    force_print=any_parent_to_print,
                    level=level + 1,
                )


class GraphPrinterMermaid(RunStrategy):
    """
    This class prints the full DAG of `EnvState`-s in `mermaid` format.
    Paste the output in the web editor like:
    https://mermaid.live/
    """

    def __init__(
        self,
        state_graph: StateGraph,
    ):
        super().__init__()
        self.state_graph: StateGraph = state_graph

    def execute_strategy(
        self,
        ignored_node: StateNode,
    ) -> None:
        print("graph TD")

        subgraph_states = {subgraph: [] for subgraph in SubGraph}
        standalone_states = []
        for state_name, state_node in self.state_graph.state_nodes.items():
            state_meta = StateMeta[state_name]
            if state_meta.value.sub_graph is None:
                standalone_states.append(state_name)
            else:
                subgraph_states[state_meta.value.sub_graph].append(state_name)

        for sub_graph, sub_states in subgraph_states.items():
            if sub_states:
                print(f'    subgraph "{sub_graph.name}"')
                for state in sub_states:
                    print(f"        {state}")
                print("    end")

        for state in standalone_states:
            print(f"    {state}")

        self.print_relationships()

    def print_relationships(self) -> None:
        for state_name, state_node in self.state_graph.state_nodes.items():
            for parent_state in state_node.get_parent_states():
                print(f"    {parent_state} --> {state_name}")
