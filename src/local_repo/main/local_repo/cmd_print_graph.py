from __future__ import annotations

import argparse
import logging
import os
import sys
from enum import Enum

from local_repo.graph_printer import (
    GraphPrinterMermaid,
    GraphPrinterPython,
    GraphPrinterTextFlat,
    GraphPrinterTextNested,
)
from local_repo.misc_tools.graph_utils import get_transitive_dependencies
from protoprimer.primer_kernel import (
    ConfLeap,
    configure_default_file_log_handler,
    configure_default_stderr_log_handler,
    EntryFunc,
    EnvContext,
    EnvState,
    get_config,
    reconfigure_file_log_handler,
    reconfigure_stderr_log_handler,
    SubCommand,
    StateGraph,
    StateNode,
    TargetState,
)


logger: logging.Logger = logging.getLogger()

format_text = "text"
format_mermaid = "mermaid"
format_python = "python"


class OutputFormat(Enum):
    output_text = format_text
    output_mermaid = format_mermaid
    output_python = format_python


layout_nested = "nested"
layout_flat = "flat"


class OutputLayout(Enum):
    layout_nested = layout_nested
    layout_flat = layout_flat


def custom_main():

    script_basename = os.path.basename(sys.argv[0])

    # UC_81_50_97_17.reuse_logger.md:
    if reconfigure_stderr_log_handler(logging.INFO) is None:
        configure_default_stderr_log_handler(logging.INFO)

    proto_kernel_abs_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(str(__file__)))))),
        "./cmd/proto_code/proto_kernel.py",
    )

    derived_data = get_config(proto_kernel_abs_path, ConfLeap.leap_derived)

    # UC_81_50_97_17.reuse_logger.md:
    if reconfigure_file_log_handler(logging.INFO) is None:
        configure_default_file_log_handler(
            log_file_abs_path=os.path.join(
                derived_data[EnvState.state_local_log_dir_abs_path_inited.name],
                f"{script_basename}.log",
            ),
            log_level=logging.INFO,
        )

    parsed_args = init_arg_parser().parse_args()

    run_print_graph(
        output_format=OutputFormat(parsed_args.format),
        output_layout=OutputLayout(parsed_args.layout),
        target_state=TargetState[parsed_args.target_state],
        entry_func=EntryFunc[parsed_args.entry_func],
        sub_command=SubCommand[parsed_args.sub_command] if parsed_args.sub_command else None,
    )


def run_print_graph(
    output_format: OutputFormat,
    output_layout: OutputLayout,
    target_state: TargetState,
    entry_func: EntryFunc,
    sub_command: SubCommand | None,
) -> None:

    logger.info(f"output_format: {output_format}")
    logger.info(f"output_layout: {output_layout}")
    logger.info(f"target_state: {target_state}")
    logger.info(f"entry_func: {entry_func}")
    logger.info(f"sub_command: {sub_command}")

    env_ctx = EnvContext()

    env_ctx.graph_coordinates.sub_command = sub_command
    env_ctx.graph_coordinates.entry_func = entry_func
    env_ctx.final_state = target_state.value.name

    # Ensure all nodes are initialized (populated into `state_graph.state_nodes`):
    # TODO: TODO_60_63_68_81.refactor_DAG_builder.md:
    #       Is this still needed?
    for env_state in EnvState:
        env_ctx.state_graph.get_state_node(env_state.name)

    state_node: StateNode = env_ctx.state_graph.get_state_node(env_ctx.final_state)

    if output_format == OutputFormat.output_mermaid and output_layout != OutputLayout.layout_nested:
        raise ValueError(f"Format `{OutputFormat.output_mermaid.value}` requires layout `{OutputLayout.layout_nested.value}`")

    if output_format == OutputFormat.output_python or output_layout == OutputLayout.layout_flat:
        # Implementation for layout_flat (and format_python which implies flat):
        sorted_dependencies = get_transitive_dependencies(
            env_ctx.state_graph,
            state_node.get_state_name(),
            env_ctx,
        )
        sorted_dependencies.append(state_node.get_state_name())

        if output_format == OutputFormat.output_python:
            selected_strategy = GraphPrinterPython(sorted_dependencies)
        else:
            selected_strategy = GraphPrinterTextFlat(sorted_dependencies)

    else:
        if output_format == OutputFormat.output_mermaid:
            selected_strategy = GraphPrinterMermaid(env_ctx.state_graph)
        else:
            selected_strategy = GraphPrinterTextNested(env_ctx.state_graph)

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
