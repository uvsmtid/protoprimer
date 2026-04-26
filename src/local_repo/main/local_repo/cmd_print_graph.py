from __future__ import annotations

import argparse
from enum import Enum

from local_repo.graph_printer import (
    GraphPrinterMermaid,
    GraphPrinterText,
)
from local_repo.misc_tools.graph_utils import get_transitive_dependencies
from protoprimer.primer_kernel import (
    EntryFunc,
    EnvContext,
    EnvState,
    SubCommand,
    StateGraph,
    StateNode,
    TargetState,
)


format_text = "text"
format_mermaid = "mermaid"


class OutputFormat(Enum):
    output_text = format_text
    output_mermaid = format_mermaid


layout_nested = "nested"
layout_flat = "flat"


class OutputLayout(Enum):
    layout_nested = layout_nested
    layout_flat = layout_flat


def custom_main():

    parsed_args = init_arg_parser().parse_args()

    env_ctx = EnvContext()

    if parsed_args.sub_command:
        env_ctx.graph_coordinates.sub_command = SubCommand[parsed_args.sub_command]

    env_ctx.graph_coordinates.entry_func = EntryFunc[parsed_args.entry_func]

    env_ctx.final_state = TargetState[parsed_args.target_state].value.name

    # Ensure all nodes are initialized (populated into `state_graph.state_nodes`):
    # TODO: TODO_60_63_68_81.refactor_DAG_builder.md:
    #       Is this still needed?
    for env_state in EnvState:
        env_ctx.state_graph.get_state_node(env_state.name)

    state_node: StateNode = env_ctx.state_graph.get_state_node(env_ctx.final_state)

    if parsed_args.format == OutputFormat.output_mermaid.value and parsed_args.layout != OutputLayout.layout_nested.value:
        raise ValueError(f"Format `{OutputFormat.output_mermaid.value}` requires layout `{OutputLayout.layout_nested.value}`")

    if parsed_args.layout == OutputLayout.layout_flat.value:
        # Implementation for layout_flat:
        sorted_dependencies = get_transitive_dependencies(
            env_ctx.state_graph,
            state_node.get_state_name(),
            env_ctx,
        )
        sorted_dependencies.append(state_node.get_state_name())

        for state_name in sorted_dependencies:
            print(state_name)

    else:
        if parsed_args.format == OutputFormat.output_mermaid.value:
            selected_strategy = GraphPrinterMermaid(env_ctx.state_graph)
        else:
            selected_strategy = GraphPrinterText(env_ctx.state_graph)

        selected_strategy.execute_strategy(state_node)


def init_arg_parser():

    arg_parser = argparse.ArgumentParser(
        description=f"Print `{StateGraph.__name__}`.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # ===

    arg_parser.add_argument(
        "--format",
        dest="format",
        choices=[enum_item.value for enum_item in OutputFormat],
        default=OutputFormat.output_text.value,
        help="Output format.",
    )
    arg_parser.add_argument(
        "--layout",
        dest="layout",
        choices=[enum_item.value for enum_item in OutputLayout],
        default=OutputLayout.layout_nested.value,
        help="Output layout.",
    )

    # ===

    arg_parser.add_argument(
        "--target_state",
        dest="target_state",
        choices=[enum_item.name for enum_item in TargetState],
        default=TargetState.target_proto_bootstrap_completed.name,
        help="Target state to print.",
    )
    arg_parser.add_argument(
        "--entry_func",
        dest="entry_func",
        choices=[enum_item.name for enum_item in EntryFunc],
        default=EntryFunc.func_boot_env.name,
        help="Entry function coordinate.",
    )
    arg_parser.add_argument(
        "--sub_command",
        dest="sub_command",
        choices=[enum_item.name for enum_item in SubCommand],
        default=None,
        help="Sub command coordinate.",
    )

    # ===

    return arg_parser


if __name__ == "__main__":
    custom_main()
