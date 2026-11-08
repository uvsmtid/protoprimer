"""
Scenario: `InvokeCondition.state_var_mismatch_reality`

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


def test_py_exec_not_verified_against_actual_python(tmp_path):
    assert InvokeCondition.state_var_mismatch_reality.test_file_basename == "test_invoke_condition_29.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        # Claim `venv` stride while running in the system `python` (and no `venv` exists):
        result = container.run("./prime --env dst/test_python_max", env={EnvVar.var_PROTOPRIMER_PY_EXEC.value: _StateStride.stride_py_venv.name})

    # TODO: FT_64_09_03_66.invoke_condition.md: verify the announced stride against `sys.executable` and fail early with a clear message:
    assert result.exit_code != 0, str(result)
    assert "command failed with `exit_code`" in result.stderr, str(result)
    assert "--python /work/venv/bin/python" in result.stderr, str(result)
