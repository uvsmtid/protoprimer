"""
Scenario: `InvokeCondition.state_var_stale_leaked`

FT_64_09_03_66.invoke_condition.md
"""

from protoprimer.primer_kernel import (
    EnvVar,
    _StateStride,
)
from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_14,
)


def test_leaked_py_exec_makes_new_run_skip_switching_to_venv(tmp_path):
    assert InvokeCondition.state_var_stale_leaked.test_file_basename == "test_invoke_condition_28.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        # The last stride leaked from a parent process - nothing is switched, client code runs in a wrong `python`:
        result = container.run("./prime --env dst/test_python_max", env={EnvVar.var_PROTOPRIMER_PY_EXEC.value: _StateStride.stride_src_updated.name})

    # TODO: FT_64_09_03_66.invoke_condition.md: remove the state vars before hand-over to client code and reject stale ones at start:
    assert result.exit_code != 0, str(result)
    assert "ModuleNotFoundError: No module named 'local_repo'" in result.stderr, str(result)
