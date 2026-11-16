import protoprimer
import pytest
from packaging.version import Version

from local_test import version_gate
from local_test.name_assertion import assert_test_module_name_embeds_another_module_name


def test_relationship():
    assert_test_module_name_embeds_another_module_name(
        version_gate.__name__,
    )


def test_new_code_version_ignores_dev_suffix(mocker):
    mocker.patch.object(protoprimer, "__version__", "1.2.3.dev4")
    assert version_gate.new_code_version() == Version("1.2.3")


def test_since_and_until_are_complementary(mocker):
    mocker.patch.object(protoprimer, "__version__", "1.2.3")
    assert version_gate.since_version("1.2.3").args[0] is False
    assert version_gate.since_version("1.2.4").args[0] is True
    assert version_gate.before_version("1.2.3").args[0] is True
    assert version_gate.before_version("1.2.4").args[0] is False


def test_proto_kernel_version_is_read_from_source(tmp_path, mocker):
    proto_kernel_abs_path = tmp_path / "proto_kernel.py"
    proto_kernel_abs_path.write_text('x = 1\n__version__ = "1.2.3.dev4"\n')
    mocker.patch(
        "local_test.integrated_helper.get_proto_kernel_source_abs_path",
        return_value=str(proto_kernel_abs_path),
    )
    assert version_gate.proto_kernel_version() == Version("1.2.3")
    version_gate.skip_if_proto_kernel_older_than("1.2.3")
    with pytest.raises(pytest.skip.Exception):
        version_gate.skip_if_proto_kernel_older_than("1.2.4")
