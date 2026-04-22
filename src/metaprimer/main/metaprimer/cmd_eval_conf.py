from __future__ import annotations

import logging

from metaprimer.conf_renderer import (
    Bootstrapper_state_all_conf_data_rendered,
    Bootstrapper_state_client_conf_file_data_loaded_rendered,
    Bootstrapper_state_derived_conf_data_loaded_rendered,
    Bootstrapper_state_env_conf_file_data_loaded_rendered,
    Bootstrapper_state_primer_conf_file_data_loaded_rendered,
    RendererState,
)
from protoprimer.primer_kernel import (
    EnvContext,
    proto_main,
)

logger = logging.getLogger()


def custom_main():
    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       convert from `boot_env` (do not run `proto_main`) to `start_app` when it can access the config.
    proto_main(customize_env_context)


def customize_env_context():

    env_ctx = EnvContext()

    env_ctx.state_graph.register_factory(
        Bootstrapper_state_primer_conf_file_data_loaded_rendered._state_name(),
        Bootstrapper_state_primer_conf_file_data_loaded_rendered(env_ctx),
    )
    env_ctx.state_graph.register_factory(
        Bootstrapper_state_client_conf_file_data_loaded_rendered._state_name(),
        Bootstrapper_state_client_conf_file_data_loaded_rendered(env_ctx),
    )
    env_ctx.state_graph.register_factory(
        Bootstrapper_state_env_conf_file_data_loaded_rendered._state_name(),
        Bootstrapper_state_env_conf_file_data_loaded_rendered(env_ctx),
    )
    env_ctx.state_graph.register_factory(
        Bootstrapper_state_derived_conf_data_loaded_rendered._state_name(),
        Bootstrapper_state_derived_conf_data_loaded_rendered(env_ctx),
    )
    env_ctx.state_graph.register_factory(
        Bootstrapper_state_all_conf_data_rendered._state_name(),
        Bootstrapper_state_all_conf_data_rendered(env_ctx),
    )

    env_ctx.final_state = RendererState.state_all_conf_data_rendered.name

    return env_ctx


if __name__ == "__main__":
    custom_main()
