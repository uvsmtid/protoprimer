"""
Scenario: `InvokeCondition.invoke_not_as_script`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_14,
)


def test_proto_kernel_executed_via_exec_in_python_c(tmp_path):
    assert InvokeCondition.invoke_not_as_script.test_file_basename == "test_invoke_condition_33.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        result = container.run("python -c \"exec(open('src/proto_code/proto_kernel.py').read())\" --env dst/test_python_max")

    # TBD: detect (no `__file__`, `sys.argv[0]` is not a file) and fail with "run it as a script":
    assert result.exit_code != 0, str(result)
    assert "NameError: name '__file__' is not defined" in result.stderr, str(result)
