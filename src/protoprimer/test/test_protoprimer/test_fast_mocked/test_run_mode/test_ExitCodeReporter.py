from unittest.mock import (
    MagicMock,
    patch,
)

from local_test.base_test_class import BaseTestClass
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ExitCodeReporter,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        ExitCodeReporter.__name__,
    )


class ThisTestClass(BaseTestClass):

    @patch(f"{primer_kernel.__name__}.sys.exit")
    def test_exit_code_reporter(self, mock_sys_exit):
        # given:
        mock_env_ctx = MagicMock()
        mock_state_node = MagicMock()
        mock_state_node.eval_own_state.return_value = 42
        reporter = ExitCodeReporter(mock_env_ctx)

        # when:
        reporter.execute_strategy(mock_state_node)

        # then:
        mock_sys_exit.assert_called_once_with(42)
