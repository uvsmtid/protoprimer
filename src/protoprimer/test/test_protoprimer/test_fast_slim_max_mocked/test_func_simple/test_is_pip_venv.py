from unittest.mock import patch
import protoprimer.primer_kernel
from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import is_pip_venv


def test_relationship():
    assert_test_module_name_embeds_str(
        is_pip_venv.__name__,
    )


@patch(f"{protoprimer.primer_kernel.__name__}.is_uv_venv", return_value=False)
def test_is_pip_venv_when_pip_venv(mock_is_uv_venv):
    # given:
    cfg_path = "/fake_venv/pyvenv.cfg"

    # when:
    result = is_pip_venv(cfg_path)

    # then:
    assert result is True
    mock_is_uv_venv.assert_called_once_with(cfg_path)


@patch(f"{protoprimer.primer_kernel.__name__}.is_uv_venv", return_value=True)
def test_is_pip_venv_when_not_pip_venv(mock_is_uv_venv):
    # given:
    cfg_path = "/fake_venv/pyvenv.cfg"

    # when:
    result = is_pip_venv(cfg_path)

    # then:
    assert result is False
    mock_is_uv_venv.assert_called_once_with(cfg_path)
