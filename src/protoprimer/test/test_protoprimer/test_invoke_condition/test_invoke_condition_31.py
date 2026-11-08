"""
Scenario: `InvokeCondition.state_var_mocked_restart_leaked`

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


def test_mocked_restart_var_is_not_ignored_in_real_run(tmp_path):
    assert InvokeCondition.state_var_mocked_restart_leaked.test_file_basename == "test_invoke_condition_31.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        result = container.run("./prime --env dst/test_python_max", env={EnvVar.var_PROTOPRIMER_MOCKED_RESTART.value: "1"})

    # TBD: honor the var only in tests - for now the run goes through with the test-only var set:
    assert result.exit_code == 0, str(result)
