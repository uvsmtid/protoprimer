"""
Scenario: `InvokeCondition.py_basename_wrong_version`

FT_64_09_03_66.invoke_condition.md
"""

from protoprimer.primer_kernel import (
    EnvVar,
    VenvDriverType,
)
from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_12,
)


def test_basename_search_picks_python_with_wrong_version_and_fails_late_with_pip_driver(tmp_path):
    assert InvokeCondition.py_basename_wrong_version.test_file_basename == "test_invoke_condition_06.py"

    with ContainerSession(image_python_3_12, tmp_path) as container:
        # Required is 3.15.2, but only `python3` (3.12) is found by the basename search:
        result = container.run("./prime --env dst/test_python_max", env={EnvVar.var_PROTOPRIMER_VENV_DRIVER.value: VenvDriverType.venv_pip.name})

    # TODO: FT_64_09_03_66.invoke_condition.md: prefer a candidate matching the version and fail early when there is none:
    assert result.exit_code != 0, str(result)
    assert "does not satisfy required version [3.15.2]" in result.stderr, str(result)
