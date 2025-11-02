from __future__ import annotations

import argparse

from local_repo.graph_printer import (
    GraphPrinterMermaid,
    GraphPrinterText,
)
from protoprimer.primer_kernel import (
    EnvContext,
    StateGraph,
    StateNode,
    TargetState,
)


def custom_main():

    parsed_args = init_arg_parser().parse_args()

    env_ctx = EnvContext()

    env_ctx.final_state = TargetState.target_proto_bootstrap_completed.value.name

    state_node: StateNode = env_ctx.state_graph.state_nodes[env_ctx.final_state]
    if parsed_args.mermaid:
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

    output_format_group = arg_parser.add_mutually_exclusive_group()
    output_format_group.add_argument(
        "--mermaid",
        dest="mermaid",
        action="store_true",
        help="Print in mermaid format.",
    )
    output_format_group.add_argument(
        "--text",
        dest="mermaid",
        action="store_false",
        help="Print in text format (default).",
    )
    arg_parser.set_defaults(mermaid=False)

    # ===

    return arg_parser


if __name__ == "__main__":
    custom_main()
