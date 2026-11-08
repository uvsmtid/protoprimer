"""
Scenario: `InvokeCondition.first_process_not_isolated`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_15,
)


def test_module_in_pythonpath_shadows_stdlib_in_the_first_process(tmp_path):
    assert InvokeCondition.first_process_not_isolated.test_file_basename == "test_invoke_condition_24.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        container.run("mkdir /tmp/shadow && echo 'raise RuntimeError(\"shadow\")' > /tmp/shadow/argparse.py")
        result = container.run("./prime --env dst/test_python_max", env={"PYTHONPATH": "/tmp/shadow"})

    # TODO: FT_64_09_03_66.invoke_condition.md: the first process must be isolated (`-I`) from `PYTHONPATH`:
    assert result.exit_code != 0, str(result)
    assert "RuntimeError: shadow" in result.stderr, str(result)
