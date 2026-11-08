"""
Scenario: `InvokeCondition.host_offline_or_proxied`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    boot_max_script,
    image_python_3_14,
)


def test_start_and_reboot_work_offline_after_online_boot(tmp_path):
    assert InvokeCondition.host_offline_or_proxied.test_file_basename == "test_invoke_condition_38.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        boot_result = container.run(boot_max_script)
        assert boot_result.exit_code == 0, str(boot_result)

        container.disconnect_network()
        start_result = container.run("./cmd/echo_app hi")
        reboot_result = container.run(boot_max_script)

    assert start_result.exit_code == 0, str(start_result)
    # TBD: the re-boot of the existing `venv` needs no network:
    assert reboot_result.exit_code == 0, str(reboot_result)
