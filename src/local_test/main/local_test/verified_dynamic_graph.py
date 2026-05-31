from __future__ import annotations

from collections.abc import Callable
from typing import Any

from protoprimer.primer_kernel import (
    EntryFunc,
    EnvContext,
    EnvState,
    NodeFactory,
    StateGraph,
    StateNode,
    SubCommand,
)


class GraphAssertionError(AssertionError):
    """
    Raised when `EnvContext` contains an invalid coordinate combination for `VerifyingStateGraph`.
    """


class VerifyingStateGraph(StateGraph):
    """
    Extended `StateGraph` that verifies `EnvContext` before instantiating any `StateNode`.
    See: FT_77_15_06_50.dynamic_DAG.md
    """

    def __init__(self):
        super().__init__()
        self.context_verifiers: list[Callable[[str, NodeFactory], None]] = [
            _verify_entry_func_is_defined,
            _verify_is_app_is_defined,
            _verify_start_app_sub_command_is_not_boot,
            _verify_start_app_does_not_prepare_venv,
            _verify_call_lib_does_not_prepare_venv,
        ]

    def get_state_node(
        self,
        state_name: str,
    ) -> StateNode:
        if state_name not in self.state_nodes:
            node_factory: NodeFactory = self.state_factories[state_name]
            self.verify_context(state_name, node_factory)
        return super().get_state_node(state_name)

    def verify_context(
        self,
        state_name: str,
        node_factory: NodeFactory,
    ) -> None:
        for verify_func in self.context_verifiers:
            verify_func(state_name, node_factory)


class VerifyingEnvContext(EnvContext):
    def _create_state_graph(self) -> StateGraph:
        return VerifyingStateGraph()


class TrackingStateGraph(VerifyingStateGraph):
    """
    Extended `VerifyingStateGraph` that records the order in which states are evaluated via `eval_state()`.
    See: FT_77_15_06_50.dynamic_DAG.md
    """

    def __init__(self):
        super().__init__()
        self._eval_log: list[str] = []
        self._eval_set: set[str] = set()

    def eval_state(
        self,
        state_name: str,
    ) -> Any:
        already_recorded = state_name in self._eval_set
        try:
            result = super().eval_state(state_name)
        finally:
            if not already_recorded:
                self._eval_log.append(state_name)
                self._eval_set.add(state_name)
        return result

    def get_evaluated_state_names(self) -> list[str]:
        return list(self._eval_log)


class TrackingEnvContext(VerifyingEnvContext):
    _state_graph: TrackingStateGraph

    def _create_state_graph(self) -> TrackingStateGraph:
        return TrackingStateGraph()


def _verify_entry_func_is_defined(
    state_name: str,
    node_factory: NodeFactory,
) -> None:
    """
    `EntryFunc` must be set before any `StateNode` is instantiated.
    """
    if node_factory.env_ctx._entry_func is None:
        raise GraphAssertionError(f"`{EntryFunc.__name__}` is not set when instantiating state [{state_name}]")


def _verify_is_app_is_defined(
    state_name: str,
    node_factory: NodeFactory,
) -> None:
    """
    `EnvContext._is_app` must be set before it can be used.
    """
    if (
        state_name
        not in [
            EnvState.state_input_py_exec_var_loaded.name,
            EnvState.state_is_app_defined.name,
        ]
        and node_factory.env_ctx._is_app is None
    ):
        raise GraphAssertionError(f"`_is_app` is not set when instantiating state [{state_name}]")


def _verify_start_app_sub_command_is_not_boot(
    state_name: str,
    node_factory: NodeFactory,
) -> None:
    """
    `Bootstrapper_state_args_parsed_not_func_boot_env` always sets `command_start` for `func_start_app`.
    """
    if (
        #
        node_factory.env_ctx._entry_func == EntryFunc.func_start_app
        and node_factory.env_ctx._sub_command == SubCommand.command_boot
    ):
        raise GraphAssertionError(
            #
            f"`{EntryFunc.func_start_app}` with `{SubCommand.command_boot}` is not a valid combination "
            f"when instantiating state [{state_name}]"
        )


def _verify_start_app_does_not_prepare_venv(
    state_name: str,
    node_factory: NodeFactory,
) -> None:
    """
    `func_start_app` assumes `venv` is already created - `prepare_venv` must be `False`.
    See: FT_05_08_64_67.start_app.md
    """
    if (
        #
        node_factory.env_ctx._entry_func == EntryFunc.func_start_app
        and node_factory.env_ctx._prepare_venv
    ):
        raise GraphAssertionError(
            #
            f"`{EntryFunc.func_start_app}` with `prepare_venv=True` is not a valid combination "
            f"when instantiating state [{state_name}]"
        )


def _verify_call_lib_does_not_prepare_venv(
    state_name: str,
    node_factory: NodeFactory,
) -> None:
    """
    `func_call_lib` assumes `venv` is already created - `prepare_venv` must be `False`.
    See: FT_85_17_35_21.call_lib.md
    """
    if (
        #
        node_factory.env_ctx._entry_func == EntryFunc.func_call_lib
        and node_factory.env_ctx._prepare_venv
    ):
        raise GraphAssertionError(
            #
            f"`{EntryFunc.func_call_lib}` with `prepare_venv=True` is not a valid combination "
            f"when instantiating state [{state_name}]"
        )


# Pre-configured `EnvContext` producing the maximum number of unique parent states
# (maximizing ordering check coverage). Clone with `copy.deepcopy` before use.
max_deps_env_ctx = VerifyingEnvContext()
max_deps_env_ctx._entry_func = EntryFunc.func_boot_env
max_deps_env_ctx._is_app = True
max_deps_env_ctx._prepare_venv = True
max_deps_env_ctx._sub_command = SubCommand.command_boot
max_deps_env_ctx._is_log_enabled = True
