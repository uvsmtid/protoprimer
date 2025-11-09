from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import is_uv_venv


def test_relationship():
    assert_test_module_name_embeds_str(
        is_uv_venv.__name__,
    )


def test_is_uv_venv_when_uv_present(fs):
    # given:
    cfg_path = "/fake_venv/pyvenv.cfg"
    fs.create_file(cfg_path, contents="uv = 1.2.3\n")

    # when:
    result = is_uv_venv(cfg_path)

    # then:
    assert result is True


def test_is_uv_venv_when_uv_absent(fs):
    # given:
    cfg_path = "/fake_venv/pyvenv.cfg"
    fs.create_file(cfg_path, contents="some other config\n")

    # when:
    result = is_uv_venv(cfg_path)

    # then:
    assert result is False
