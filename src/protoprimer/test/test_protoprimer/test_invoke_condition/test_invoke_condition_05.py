"""
Scenario: `InvokeCondition.py_selector_fails`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_15,
)


def test_exception_in_selector_script_propagates_as_raw_stack_trace(tmp_path):
    assert InvokeCondition.py_selector_fails.test_file_basename == "test_invoke_condition_05.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        container.write_file(
            "src/proto_code/bad_selector.py",
            """
def select_python_file_abs_path(required_version):
    raise RuntimeError("selector boom")
""",
        )
        container.run("sed -i 's#src/proto_code/python_selector_py3.15.py#src/proto_code/bad_selector.py#' dst/test_python_max/proto_kernel.json")
        result = container.run("./prime --env dst/test_python_max")

    # TODO: FT_64_09_03_66.invoke_condition.md: report the selector path and the cause, then fall back or fail (decision needed):
    assert result.exit_code != 0, str(result)
    assert "RuntimeError: selector boom" in result.stderr, str(result)
