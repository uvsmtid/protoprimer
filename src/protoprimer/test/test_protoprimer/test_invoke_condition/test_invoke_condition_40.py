"""
Scenario: `InvokeCondition.shell_unsupported`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_15,
)


def test_unknown_shell_is_rejected(tmp_path):
    assert InvokeCondition.shell_unsupported.test_file_basename == "test_invoke_condition_40.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        boot_result = container.run("./prime")
        assert boot_result.exit_code == 0, str(boot_result)

        result = container.run("./prime shell", env={"SHELL": "/bin/fish"})

    assert result.exit_code != 0, str(result)
    assert "env var `SHELL` has unknown value [/bin/fish]" in result.stderr, str(result)
