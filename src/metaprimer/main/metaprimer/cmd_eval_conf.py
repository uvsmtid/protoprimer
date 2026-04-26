from __future__ import annotations

import json
import logging
import os
import sys

from metaprimer.conf_renderer import (
    RenderConfigVisitor,
    RootNode_client,
    RootNode_derived,
    RootNode_env,
    RootNode_input,
    RootNode_primer,
)
from protoprimer.primer_kernel import (
    ConfLeap,
    EnvState,
    EnvVar,
    get_config,
)

logger = logging.getLogger()


def custom_main():
    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       Who to make `venv`-module independent of the any entry script path it was called from?
    #       NOTE: This is a wrong fix (because the script is not supposed to be called via `boot_env`):
    #       Fix: check PROTOPRIMER_PROTO_CODE env var first (available when called via boot_env).
    proto_kernel_abs_path = os.environ.get(EnvVar.var_PROTOPRIMER_PROTO_CODE.value)
    if proto_kernel_abs_path is None:
        proto_kernel_abs_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(str(__file__)))))),
            "./cmd/proto_code/proto_kernel.py",
        )

    derived_data = get_config(proto_kernel_abs_path, ConfLeap.leap_derived)

    state_proto_code_file_abs_path_inited = derived_data[EnvState.state_proto_code_file_abs_path_inited.name]
    state_primer_conf_file_abs_path_inited = derived_data[EnvState.state_primer_conf_file_abs_path_inited.name]
    state_global_conf_file_abs_path_inited = derived_data[EnvState.state_global_conf_file_abs_path_inited.name]
    state_local_conf_file_abs_path_inited = derived_data[EnvState.state_local_conf_file_abs_path_inited.name]

    conf_input = RootNode_input(
        node_indent=0,
        orig_data={
            EnvState.state_proto_code_file_abs_path_inited.name: state_proto_code_file_abs_path_inited,
            EnvState.state_primer_conf_file_abs_path_inited.name: state_primer_conf_file_abs_path_inited,
        },
    )
    print(RenderConfigVisitor().render_node(conf_input))

    conf_primer = RootNode_primer(
        node_indent=0,
        orig_data=get_config(proto_kernel_abs_path, ConfLeap.leap_primer),
        state_primer_conf_file_abs_path_inited=state_primer_conf_file_abs_path_inited,
    )
    print(RenderConfigVisitor().render_node(conf_primer))

    conf_client = RootNode_client(
        node_indent=0,
        orig_data=get_config(proto_kernel_abs_path, ConfLeap.leap_client),
        state_global_conf_file_abs_path_inited=state_global_conf_file_abs_path_inited,
    )
    print(RenderConfigVisitor().render_node(conf_client))

    conf_env = RootNode_env(
        node_indent=0,
        orig_data=get_config(proto_kernel_abs_path, ConfLeap.leap_env),
        state_local_conf_file_abs_path_inited=state_local_conf_file_abs_path_inited,
    )
    print(RenderConfigVisitor().render_node(conf_env))

    conf_derived = RootNode_derived(
        node_indent=0,
        orig_data=derived_data,
    )
    print(RenderConfigVisitor().render_node(conf_derived))


if __name__ == "__main__":
    custom_main()
