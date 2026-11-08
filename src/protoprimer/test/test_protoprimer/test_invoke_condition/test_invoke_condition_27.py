"""
Scenario: `InvokeCondition.state_var_invalid_value`

FT_64_09_03_66.invoke_condition.md
"""

from protoprimer.primer_kernel import (
    EnvVar,
)
from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_15,
)


def test_invalid_py_exec_value_fails_with_raw_key_error(tmp_path):
    assert InvokeCondition.state_var_invalid_value.test_file_basename == "test_invoke_condition_27.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        result = container.run("./prime", env={EnvVar.var_PROTOPRIMER_PY_EXEC.value: "garbage"})

    # TODO: FT_64_09_03_66.invoke_condition.md: fail with a message naming the var, the bad value, and the allowed values:
    assert result.exit_code != 0, str(result)
    assert "KeyError: 'garbage'" in result.stderr, str(result)
