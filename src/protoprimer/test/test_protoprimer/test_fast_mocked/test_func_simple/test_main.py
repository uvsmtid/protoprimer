from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

import protoprimer.primer_kernel
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    main,
    TargetState,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        main.__name__,
    )


@patch(f"{protoprimer.primer_kernel.__name__}.atexit.register")
@patch(f"{protoprimer.primer_kernel.__name__}.EnvContext")
@patch(f"{protoprimer.primer_kernel.__name__}.ensure_min_python_version")
def test_main_success(
    mock_ensure_min_python_version,
    mock_env_context,
    mock_atexit_register,
):
    # given:
    mock_env_ctx_instance = MagicMock()
    mock_env_context.return_value = mock_env_ctx_instance
    mock_env_ctx_instance.state_graph.eval_state.return_value = True

    # when:
    main()

    # then:
    mock_ensure_min_python_version.assert_called_once()
    mock_env_context.assert_called_once()
    mock_env_ctx_instance.state_graph.eval_state.assert_called_once_with(
        TargetState.target_run_mode_executed
    )
    mock_atexit_register.assert_called_once()


@patch(f"{protoprimer.primer_kernel.__name__}.atexit.register")
@patch(f"{protoprimer.primer_kernel.__name__}.EnvContext")
@patch(f"{protoprimer.primer_kernel.__name__}.ensure_min_python_version")
def test_main_assertion_error(
    mock_ensure_min_python_version,
    mock_env_context,
    mock_atexit_register,
):
    # given:
    mock_env_ctx_instance = MagicMock()
    mock_env_context.return_value = mock_env_ctx_instance
    mock_env_ctx_instance.state_graph.eval_state.return_value = False

    # when/then:
    with pytest.raises(AssertionError):
        main()

    # then:
    mock_ensure_min_python_version.assert_called_once()
    mock_env_context.assert_called_once()
    mock_env_ctx_instance.state_graph.eval_state.assert_called_once_with(
        TargetState.target_run_mode_executed
    )
    mock_atexit_register.assert_called_once()


@patch(f"{protoprimer.primer_kernel.__name__}.atexit.register")
@patch(f"{protoprimer.primer_kernel.__name__}.EnvContext")
@patch(f"{protoprimer.primer_kernel.__name__}.ensure_min_python_version")
def test_main_system_exit(
    mock_ensure_min_python_version,
    mock_env_context,
    mock_atexit_register,
):
    # given:
    mock_env_ctx_instance = MagicMock()
    mock_env_context.return_value = mock_env_ctx_instance
    mock_env_ctx_instance.state_graph.eval_state.side_effect = SystemExit(1)

    # when/then:
    with pytest.raises(SystemExit):
        main()

    # then:
    mock_ensure_min_python_version.assert_called_once()
    mock_env_context.assert_called_once()
    mock_env_ctx_instance.state_graph.eval_state.assert_called_once_with(
        TargetState.target_run_mode_executed
    )
    mock_atexit_register.assert_called_once()


@patch(f"{protoprimer.primer_kernel.__name__}.atexit.register")
@patch(f"{protoprimer.primer_kernel.__name__}.EnvContext")
@patch(f"{protoprimer.primer_kernel.__name__}.ensure_min_python_version")
def test_main_generic_exception(
    mock_ensure_min_python_version,
    mock_env_context,
    mock_atexit_register,
):
    # given:
    mock_env_ctx_instance = MagicMock()
    mock_env_context.return_value = mock_env_ctx_instance
    mock_env_ctx_instance.state_graph.eval_state.side_effect = Exception(
        "Test Exception"
    )

    # when/then:
    with pytest.raises(Exception, match="Test Exception"):
        main()

    # then:
    mock_ensure_min_python_version.assert_called_once()
    mock_env_context.assert_called_once()
    mock_env_ctx_instance.state_graph.eval_state.assert_called_once_with(
        TargetState.target_run_mode_executed
    )
    mock_atexit_register.assert_called_once()


@patch(f"{protoprimer.primer_kernel.__name__}.atexit.register")
@patch(f"{protoprimer.primer_kernel.__name__}.ensure_min_python_version")
def test_main_with_configure_env_context(
    mock_ensure_min_python_version,
    mock_atexit_register,
):
    # given:
    mock_configure_env_context = MagicMock()
    mock_env_ctx_instance = MagicMock()
    mock_configure_env_context.return_value = mock_env_ctx_instance
    mock_env_ctx_instance.state_graph.eval_state.return_value = True

    # when:
    main(configure_env_context=mock_configure_env_context)

    # then:
    mock_ensure_min_python_version.assert_called_once()
    mock_configure_env_context.assert_called_once()
    mock_env_ctx_instance.state_graph.eval_state.assert_called_once_with(
        TargetState.target_run_mode_executed
    )
    mock_atexit_register.assert_called_once()


@patch(f"{protoprimer.primer_kernel.__name__}.atexit.register")
@patch(f"{protoprimer.primer_kernel.__name__}.EnvContext")
@patch(f"{protoprimer.primer_kernel.__name__}.ensure_min_python_version")
def test_main_atexit_on_success(
    mock_ensure_min_python_version,
    mock_env_context,
    mock_atexit_register,
):
    # given:
    mock_env_ctx_instance = MagicMock()
    mock_env_context.return_value = mock_env_ctx_instance
    mock_env_ctx_instance.state_graph.eval_state.return_value = True

    # when:
    main()

    # then:
    mock_atexit_register.assert_called_once()
    # and:
    registered_lambda = mock_atexit_register.call_args[0][0]
    registered_lambda()
    # and:
    mock_env_ctx_instance.print_exit_line.assert_called_once_with(0)
