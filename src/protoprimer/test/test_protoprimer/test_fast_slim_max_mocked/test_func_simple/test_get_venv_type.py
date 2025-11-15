import os

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    get_venv_type,
    PackageDriverType,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        get_venv_type.__name__,
    )


def test_get_venv_type_for_uv(fs):
    # given:
    venv_path = "/fake_venv"
    fs.create_dir(venv_path)
    fs.create_file(os.path.join(venv_path, "pyvenv.cfg"), contents="uv = 1.2.3\n")

    # when:
    result = get_venv_type(venv_path)

    # then:
    assert result == PackageDriverType.driver_uv


def test_get_venv_type_for_pip(fs):
    # given:
    venv_path = "/fake_venv"
    fs.create_dir(venv_path)
    fs.create_file(
        os.path.join(venv_path, "pyvenv.cfg"), contents="some other config\n"
    )

    # when:
    result = get_venv_type(venv_path)

    # then:
    assert result == PackageDriverType.driver_pip


def test_get_venv_type_when_cfg_missing(fs):
    # given:
    venv_path = "/fake_venv"
    fs.create_dir(venv_path)

    # when/then:
    with pytest.raises(AssertionError) as excinfo:
        get_venv_type(venv_path)
    assert "does not exist" in str(excinfo.value)
