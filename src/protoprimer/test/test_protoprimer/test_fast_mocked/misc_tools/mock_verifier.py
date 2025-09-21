from unittest.mock import MagicMock

from protoprimer.primer_kernel import (
    EnvContext,
    EnvState,
)


def assert_parent_states_mocked(
    env_ctx: EnvContext,
    final_env_state: EnvState,
) -> None:
    final_state_node = env_ctx.state_graph.get_state_node(final_env_state.name)
    assert final_state_node is not None

    expected_mocked_state_names = set(final_state_node.get_parent_states())

    # Add the target state itself to the set of expected mocked states if it's being mocked in the test
    if isinstance(getattr(final_env_state.value, "eval_own_state"), MagicMock):
        expected_mocked_state_names.add(final_env_state.name)

    for env_state_item in EnvState:
        bootstrapper_class = env_state_item.value
        eval_method = getattr(bootstrapper_class, "eval_own_state")

        is_mocked = isinstance(eval_method, MagicMock)

        effective_state_name = env_state_item.name

        # TODO: Maybe Wizard states (where moved states are used) should not rely on them?
        # See: UC_27_40_17_59.replace_by_new_and_use_old.md:
        # Handle "moved state names" (e.g., `_state_client_conf_file_data`):
        if effective_state_name.startswith("_"):
            original_state_name = effective_state_name[1:]
            # If the original state name is expected to be mocked, then the moved state is also expected:
            if original_state_name in expected_mocked_state_names:
                effective_state_name = original_state_name

        if effective_state_name not in expected_mocked_state_names:
            # If the state is not expected to be mocked, it must not be mocked:
            assert (
                not is_mocked
            ), f"State [{env_state_item.name}] is mocked but is not an expected parent of [{final_env_state.name}]."
        else:
            # If the state is expected to be mocked, it must be mocked:
            assert (
                is_mocked
            ), f"Parent state [{env_state_item.name}] is not mocked as expected."
