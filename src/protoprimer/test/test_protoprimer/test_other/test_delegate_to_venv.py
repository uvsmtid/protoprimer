import os
import sys

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ConfConstEnv,
    ConfConstGeneral,
    delegate_to_venv,
    EnvVarConst,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        delegate_to_venv.__name__,
    )


class TestSuite:

    # noinspection PyAttributeOutsideInit
    @pytest.fixture(autouse=True)
    def setup_mocks(self, mocker, monkeypatch):
        self.mock_execv = mocker.patch("os.execv")
        self.mock_path_exists = mocker.patch("os.path.exists")
        self.mock_is_venv = mocker.patch(f"{primer_kernel.__name__}.is_venv")

    def setup_method(self):
        self.original_path = os.environ.get(EnvVarConst.name_PATH, "")

    def teardown_method(self):
        os.environ[EnvVarConst.name_PATH] = self.original_path

    def test_in_venv(self):

        # given:

        self.mock_is_venv.return_value = True

        client_ref_dir_path = "/mock/client/dir"

        # when:

        ret_val = delegate_to_venv(client_ref_dir_path)

        assert ret_val is False
        self.mock_execv.assert_not_called()
        self.mock_path_exists.assert_not_called()
        assert os.environ.get("PATH", "") == self.original_path

    def test_not_in_venv(self):

        # given:

        self.mock_is_venv.return_value = False
        self.mock_path_exists.return_value = True

        client_ref_dir_path = "/mock/client/dir"

        # when:

        delegate_to_venv(client_ref_dir_path)

        # then:

        expected_venv_bin = os.path.join(
            client_ref_dir_path,
            # TODO: This might be passed as arg to the func (that being a default):
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_bin,
        )
        expected_venv_python = os.path.join(
            client_ref_dir_path,
            # TODO: This might be passed as arg to the func (that being a default):
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )

        self.mock_execv.assert_called_once_with(
            expected_venv_python,
            [
                expected_venv_python,
                *sys.argv,
            ],
        )

        assert os.environ[EnvVarConst.name_PATH].startswith(
            expected_venv_bin + os.pathsep
        )
        assert os.environ[EnvVarConst.name_PATH].endswith(self.original_path)

        self.mock_path_exists.assert_called_once_with(expected_venv_python)
