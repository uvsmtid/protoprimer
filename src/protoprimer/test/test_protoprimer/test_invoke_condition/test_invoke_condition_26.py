"""
Scenario: `InvokeCondition.env_foreign_tool_vars`

FT_64_09_03_66.invoke_condition.md
"""

from protoprimer.primer_kernel import (
    EnvVar,
    VenvDriverType,
)
from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_14,
)


def test_pip_user_var_breaks_pip_driver_install(tmp_path):
    assert InvokeCondition.env_foreign_tool_vars.test_file_basename == "test_invoke_condition_26.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        result = container.run(
            "./prime --env dst/test_python_max",
            env={
                EnvVar.var_PROTOPRIMER_VENV_DRIVER.value: VenvDriverType.venv_pip.name,
                "PIP_USER": "1",
            },
        )

    # TODO: FT_64_09_03_66.invoke_condition.md: drop the vars redirecting installs (with a warning) before calling `pip`/`uv`:
    assert result.exit_code != 0, str(result)
    assert "command failed with `exit_code`" in result.stderr, str(result)
    assert "/work/venv/bin/python -m pip install" in result.stderr, str(result)
