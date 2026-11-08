"""
Scenario: `InvokeCondition.venv_python_is_selected_python`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    boot_max_script,
    image_python_3_14,
)


def test_selector_returning_python_from_dedicated_venv_is_rejected(tmp_path):
    assert InvokeCondition.venv_python_is_selected_python.test_file_basename == "test_invoke_condition_12.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        boot_result = container.run(boot_max_script)
        assert boot_result.exit_code == 0, str(boot_result)

        container.write_file(
            "src/proto_code/venv_selector.py",
            """
def select_python_file_abs_path(required_version):
    return "/work/venv/bin/python"
""",
        )
        container.run("sed -i 's#src/proto_code/python_selector_py3.14.py#src/proto_code/venv_selector.py#' dst/test_python_max/proto_kernel.json")
        result = container.run(boot_max_script)

    assert result.exit_code != 0, str(result)
    assert "must be outside of configured `venv`" in result.stderr, str(result)
