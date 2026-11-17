from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    _ContextBuilder,
    _EntryFunc,
    _EnvState,
    _Factory_state_derived_conf_data_loaded,
    _Node_state_derived_conf_data_loaded_is_app,
    _Node_state_derived_conf_data_loaded_not_is_app,
)


def test_relationship():
    assert_test_module_name_embeds_str(_EnvState.state_derived_conf_data_loaded.name)


def test_factory_is_app_node_depends_on_exec_operation_before_symlink():
    # given:
    env_ctx = _ContextBuilder().entry_func(_EntryFunc.func_boot_env).is_app(True).build_context()

    # when:
    state_node = _Factory_state_derived_conf_data_loaded(env_ctx).create_state_node()

    # then: the exec operation selects the `Node` of the symlink state
    assert type(state_node) is _Node_state_derived_conf_data_loaded_is_app
    parent_states = state_node.get_parent_states()
    assert _EnvState.state_input_exec_operation_loaded.name in parent_states
    assert parent_states.index(_EnvState.state_input_exec_operation_loaded.name) < parent_states.index(_EnvState.state_local_conf_symlink_abs_path_inited.name)


def test_factory_not_is_app_node_does_not_depend_on_exec_operation():
    # given:
    env_ctx = _ContextBuilder().entry_func(_EntryFunc.func_call_lib).is_app(False).build_context()

    # when:
    state_node = _Factory_state_derived_conf_data_loaded(env_ctx).create_state_node()

    # then: `FT_77_15_06_50.dynamic_DAG.md`: the exec operation is not processed outside of `_is_app`
    assert type(state_node) is _Node_state_derived_conf_data_loaded_not_is_app
    assert _EnvState.state_input_exec_operation_loaded.name not in state_node.get_parent_states()


def test_parent_states_only_differ_by_exec_operation():
    # given:
    app_ctx = _ContextBuilder().entry_func(_EntryFunc.func_boot_env).is_app(True).build_context()
    lib_ctx = _ContextBuilder().entry_func(_EntryFunc.func_call_lib).is_app(False).build_context()

    # when:
    app_parent_states = _Factory_state_derived_conf_data_loaded(app_ctx).create_state_node().get_parent_states()
    lib_parent_states = _Factory_state_derived_conf_data_loaded(lib_ctx).create_state_node().get_parent_states()

    # then:
    assert [parent_state for parent_state in app_parent_states if parent_state != _EnvState.state_input_exec_operation_loaded.name] == lib_parent_states
