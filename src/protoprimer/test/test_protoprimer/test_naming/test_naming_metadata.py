from __future__ import annotations

import enum

from local_test.consistent_naming import verify_name_enum_order_in_name
from protoprimer.primer_kernel import (
    EnvState,
)
from test_protoprimer.test_naming.naming_metadata import (
    StateCategoryMeta,
    StateItem,
    StateMeta,
)


# noinspection PyPep8Naming
def test_every_EnvState_in_StateMeta_and_vice_versa():

    env_state_names = [env_state.name for env_state in EnvState]
    state_item_names = [state_item.name for state_item in StateItem]

    # EnvState -> StateItem:
    for env_state_name in env_state_names:
        assert env_state_name in state_item_names

    # StateItem -> EnvState:
    for state_item_name in state_item_names:
        assert state_item_name in env_state_names


# noinspection PyPep8Naming
def test_EnvState_and_StateMeta_are_assigned_correctly():

    for state_item in StateItem:
        assert state_item.name == state_item.value.env_state.name


# noinspection PyPep8Naming
def test_EnvState_default_implementation_embeds_its_name():

    for env_state in EnvState:
        assert env_state.name in env_state.value.__name__


# noinspection PyPep8Naming
def test_EnvState_naming_convention():

    for state_item in StateItem:
        state_meta: StateMeta = state_item.value
        category_meta: StateCategoryMeta = state_meta.category_meta
        given_name = state_meta.env_state.name
        ret_val: enum.Enum | None = verify_name_enum_order_in_name(
            category_meta.name_enums,
            state_meta.env_state.name,
        )
        if ret_val is not None:
            raise AssertionError(
                f"name [{given_name}] does not contain value from enum [{ret_val.__name__}]"
            )


# noinspection PyPep8Naming
def test_EnvState_name_is_not_embedded_in_any_other_EnvState_name():

    for env_state_a in EnvState:
        for env_state_b in EnvState:
            if env_state_a.name != env_state_b.name:
                assert env_state_a.name not in env_state_b.name
