"""
Scenario: `InvokeCondition.venv_right_active`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    boot_max_script,
    image_python_3_14,
)


def test_boot_from_inside_the_dedicated_venv_succeeds(tmp_path):
    assert InvokeCondition.venv_right_active.test_file_basename == "test_invoke_condition_11.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        boot_result = container.run(boot_max_script)
        assert boot_result.exit_code == 0, str(boot_result)

        result = container.run(f". venv/bin/activate && {boot_max_script}")

    assert result.exit_code == 0, str(result)
