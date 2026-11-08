"""
Scenario: `InvokeCondition.py_uv_needs_newer_selected_python`

FT_64_09_03_66.invoke_condition.md
"""

from protoprimer.primer_kernel import (
    EnvVar,
    VenvDriverType,
)
from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_7,
)


def test_uv_driver_is_replaced_by_pip_driver_for_python_older_than_3_8(tmp_path):
    assert InvokeCondition.py_uv_needs_newer_selected_python.test_file_basename == "test_invoke_condition_09.py"

    with ContainerSession(image_python_3_7, tmp_path) as container:
        result = container.run("./prime -v --env dst/test_python_min", env={EnvVar.var_PROTOPRIMER_VENV_DRIVER.value: VenvDriverType.venv_uv.name})

    assert result.exit_code == 0, str(result)
    assert "Overriding package driver" in result.stderr, str(result)
