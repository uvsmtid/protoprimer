"""
Scenario: `InvokeCondition.py_new_not_required`

FT_64_09_03_66.invoke_condition.md
"""

from protoprimer.primer_kernel import (
    _StateStride,
)
from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_15,
)


def test_python_newer_than_required_switches_to_required_python(tmp_path):
    assert InvokeCondition.py_new_not_required.test_file_basename == "test_invoke_condition_03.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        # The `required_python_version` of this env is 3.11.14:
        result = container.run("./prime -v --env dst/test_python_med")
        venv_version = container.run("./venv/bin/python --version")

    assert result.exit_code == 0, str(result)
    assert _StateStride.stride_py_required.name in result.stderr, str(result)
    assert venv_version.stdout.strip() == "Python 3.11.14", str(venv_version)
