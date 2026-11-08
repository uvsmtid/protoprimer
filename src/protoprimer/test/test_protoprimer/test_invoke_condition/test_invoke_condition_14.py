"""
Scenario: `InvokeCondition.venv_wrong_driver`

FT_64_09_03_66.invoke_condition.md
"""

from protoprimer.primer_kernel import (
    EnvVar,
    VenvDriverType,
)
from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    boot_max_script,
    image_python_3_14,
)


def test_reusing_venv_created_by_another_driver_fails_with_reset_hint(tmp_path):
    assert InvokeCondition.venv_wrong_driver.test_file_basename == "test_invoke_condition_14.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        boot_result = container.run(boot_max_script)
        assert boot_result.exit_code == 0, str(boot_result)

        result = container.run(boot_max_script, env={EnvVar.var_PROTOPRIMER_VENV_DRIVER.value: VenvDriverType.venv_pip.name})

    assert result.exit_code != 0, str(result)
    assert f"was not created by this driver [{VenvDriverType.venv_pip.name}] retry with [reset] exec operation" in result.stderr, str(result)
