"""
Scenario: `InvokeCondition.py_too_old_for_kernel`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    image_python_3_6,
    ContainerSession,
    InvokeCondition,
)


def test_python_3_6_fails_with_syntax_error(tmp_path):
    assert InvokeCondition.py_too_old_for_kernel.test_file_basename == "test_invoke_condition_01.py"

    # SKIP: `python` < 3.7 is not supported - the raw `SyntaxError` is the accepted behavior:
    with ContainerSession(image_python_3_6, tmp_path) as container:
        result = container.run("./prime")

    assert result.exit_code != 0, str(result)
    assert "SyntaxError: future feature annotations is not defined" in result.stderr, str(result)
