"""
FT_78_72_23_04.backward_compatibility.md
"""

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import EnvVar

# The env var names are frozen here: they can be added, but must not be removed or renamed:
frozen_env_var_values = [
    "PROTOPRIMER_PROTO_KERNEL",
    "PROTOPRIMER_MAIN_FUNC",
    "PROTOPRIMER_STDERR_LOG_LEVEL",
    "PROTOPRIMER_PY_EXEC",
    "PROTOPRIMER_CONF_BASENAME",
    "PROTOPRIMER_START_ID",
    "PROTOPRIMER_VENV_DRIVER",
    "PROTOPRIMER_MOCKED_RESTART",
    "PROTOPRIMER_TRACE_EXECUTION",
]


def test_relationship():
    assert_test_module_name_embeds_str(
        EnvVar.__name__,
    )


@pytest.mark.parametrize("frozen_env_var_value", frozen_env_var_values)
def test_frozen_env_var_value_exists(frozen_env_var_value):

    # given:
    current_env_var_values = {env_var.value for env_var in EnvVar}

    # then:
    assert frozen_env_var_value in current_env_var_values
