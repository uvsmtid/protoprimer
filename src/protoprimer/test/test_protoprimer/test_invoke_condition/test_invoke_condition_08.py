"""
Scenario: `InvokeCondition.py_without_venv_module`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_debian,
)


def test_python_without_venv_module_fails_with_raw_subprocess_error(tmp_path):
    assert InvokeCondition.py_without_venv_module.test_file_basename == "test_invoke_condition_08.py"

    with ContainerSession(image_debian, tmp_path) as container:
        # Debian ships `venv`/`ensurepip` in a separate package (`python3-venv`) - it is not installed:
        setup_result = container.run("apt-get update && apt-get install -y --no-install-recommends python3")
        assert setup_result.exit_code == 0, str(setup_result)

        result = container.run("./prime --env dst/test_python_max")

    # TODO: FT_64_09_03_66.invoke_condition.md: detect the missing module up front and hint which package to install:
    assert result.exit_code != 0, str(result)
    assert "ensurepip" in result.output, str(result)
    assert "command failed with `exit_code`" in result.stderr, str(result)
