"""
Scenario: `InvokeCondition.py_old_not_required`

FT_64_09_03_66.invoke_condition.md
"""

from protoprimer.primer_kernel import (
    _StateStride,
)
from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_9,
)


def test_python_older_than_required_switches_to_required_python(tmp_path):
    assert InvokeCondition.py_old_not_required.test_file_basename == "test_invoke_condition_02.py"

    with ContainerSession(image_python_3_9, tmp_path) as container:
        result = container.run("./prime -v --env dst/test_python_max")
        venv_version = container.run("./venv/bin/python --version")

    assert result.exit_code == 0, str(result)
    assert _StateStride.stride_py_required.name in result.stderr, str(result)
    assert venv_version.stdout.strip() == "Python 3.15.2", str(venv_version)
