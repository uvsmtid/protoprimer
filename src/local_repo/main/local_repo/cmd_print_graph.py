from __future__ import annotations

import argparse

from local_repo.graph_printer import GraphPrinter
from protoprimer.primer_kernel import (
    EnvContext,
    StateGraph,
    StateNode,
    TargetState,
)


def custom_main():

    parsed_args = init_arg_parser().parse_args()

    env_ctx = EnvContext()

    env_ctx.final_state = TargetState.target_full_proto_bootstrap

    state_node: StateNode = env_ctx.state_graph.state_nodes[env_ctx.final_state]
    selected_strategy = GraphPrinter(env_ctx.state_graph)

    selected_strategy.execute_strategy(state_node)


def init_arg_parser():

    arg_parser = argparse.ArgumentParser(
        description=f"Print `{StateGraph.__name__}`.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    return arg_parser


if __name__ == "__main__":
    custom_main()
