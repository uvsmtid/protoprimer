from unittest.mock import MagicMock

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    RunStrategy,
)


def test_relationship():
    assert_test_module_name_embeds_str(RunStrategy.__name__)


def test_execute_strategy_raises_not_implemented_error():
    # given:
    run_strategy = RunStrategy()
    mock_state_node = MagicMock()

    # when/then:
    with pytest.raises(NotImplementedError):
        run_strategy.execute_strategy(mock_state_node)
