import protoprimer
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
    assert version_gate.since("1.2.3").args[0] is False
    assert version_gate.since("1.2.4").args[0] is True
    assert version_gate.until("1.2.3").args[0] is True
    assert version_gate.until("1.2.4").args[0] is False
