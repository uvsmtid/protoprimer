"""
Scenario: `InvokeCondition.env_selection_mismatch`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    boot_max_script,
    image_python_3_15,
)


def test_boot_with_another_env_than_lconf_symlink_fails(tmp_path):
    assert InvokeCondition.env_selection_mismatch.test_file_basename == "test_invoke_condition_37.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        boot_result = container.run(boot_max_script)
        assert boot_result.exit_code == 0, str(boot_result)

        result = container.run("./prime --env dst/test_python_med")

    assert result.exit_code != 0, str(result)
    assert "target [dst/test_python_max] is not the same as the provided target [dst/test_python_med]" in result.stderr, str(result)
