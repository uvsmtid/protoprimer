"""
Scenario: `InvokeCondition.invoke_via_symlink`

FT_64_09_03_66.invoke_condition.md
"""

from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    container_work_dir,
    image_python_3_15,
)


def test_entry_script_invoked_via_symlink_resolves_proto_kernel_relative_to_link(tmp_path):
    assert InvokeCondition.invoke_via_symlink.test_file_basename == "test_invoke_condition_34.py"

    with ContainerSession(image_python_3_15, tmp_path) as container:
        container.run(f"ln -s {container_work_dir}/prime /tmp/prime_link")
        result = container.run("/tmp/prime_link --env dst/test_python_max_linux")

    # TBD: decide which location is intended (the link or the target):
    assert result.exit_code != 0, str(result)
    assert "FileNotFoundError" in result.stderr, str(result)
    assert "/tmp/src/proto_code/proto_kernel.py" in result.stderr, str(result)
