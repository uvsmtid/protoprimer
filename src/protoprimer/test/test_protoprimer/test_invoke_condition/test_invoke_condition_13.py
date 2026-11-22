"""
Scenario: `InvokeCondition.venv_missing_on_start`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    container_work_dir,
    image_python_3_15,
)


def test_start_without_venv_fails_with_hint(tmp_path):
    assert InvokeCondition.venv_missing_on_start.test_file_basename == "test_invoke_condition_13.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        result = container.run("./cmd/echo_app hi")

    assert result.exit_code != 0, str(result)
    assert f"`venv` [{container_work_dir}/venv] is not found, run `boot` first" in result.stderr, str(result)
