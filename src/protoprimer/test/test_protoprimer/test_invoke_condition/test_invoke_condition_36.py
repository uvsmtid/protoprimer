"""
Scenario: `InvokeCondition.invoke_lib_call`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    boot_max_script,
    image_python_3_14,
)


def test_get_config_outside_start_app_fails_with_proto_kernel_path_not_set(tmp_path):
    assert InvokeCondition.invoke_lib_call.test_file_basename == "test_invoke_condition_36.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        boot_result = container.run(boot_max_script)
        assert boot_result.exit_code == 0, str(boot_result)

        result = container.run('./venv/bin/python -c "from protoprimer.primer_kernel import get_config, _ConfLeap; get_config(_ConfLeap.leap_client)"')

    # TBD: improve the message (how to provide the path):
    assert result.exit_code != 0, str(result)
    assert "`proto_kernel_abs_path` [None] is not set" in result.stderr, str(result)
