"""
Scenario: `InvokeCondition.venv_wrong_python_version`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    boot_max_script,
    image_python_3_14,
)


def test_existing_venv_with_other_python_version_is_silently_reused(tmp_path):
    assert InvokeCondition.venv_wrong_python_version.test_file_basename == "test_invoke_condition_15.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        boot_result = container.run(boot_max_script)
        assert boot_result.exit_code == 0, str(boot_result)

        # Require another `python` version (the `venv` was created with 3.14.0):
        container.run("sed -i s/3.14.0/3.13.0/ dst/test_python_max/proto_kernel.json")
        result = container.run(boot_max_script)
        venv_version = container.run("./venv/bin/python --version")

    # TODO: FT_64_09_03_66.invoke_condition.md: the mismatch must be detected (fail with `reset` hint or re-create `venv`) - for now it is reused:
    assert result.exit_code == 0, str(result)
    assert venv_version.stdout.strip() == "Python 3.14.0", str(venv_version)
