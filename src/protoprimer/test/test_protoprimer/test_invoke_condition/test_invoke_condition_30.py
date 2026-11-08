"""
Scenario: `InvokeCondition.state_var_proto_kernel_wrong`

FT_64_09_03_66.invoke_condition.md
"""

from protoprimer.primer_kernel import (
    EnvVar,
)
from local_test.invoke_condition_helper import (
    ContainerSession,
    InvokeCondition,
    image_python_3_14,
)


def test_relative_proto_kernel_path_is_rejected(tmp_path):
    assert InvokeCondition.state_var_proto_kernel_wrong.test_file_basename == "test_invoke_condition_30.py"

    with ContainerSession(image_python_3_14, tmp_path) as container:
        result = container.run(
            "python src/proto_code/proto_kernel.py --env dst/test_python_max",
            env={EnvVar.var_PROTOPRIMER_PROTO_KERNEL.value: "relative/proto_kernel.py"},
        )

    assert result.exit_code != 0, str(result)
    assert "`PROTOPRIMER_PROTO_KERNEL` must specify absolute path" in result.stderr, str(result)
