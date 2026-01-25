import os
import sys
from unittest.mock import patch

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    ConfConstEnv,
    ConfConstGeneral,
    ConfConstInput,
    switch_to_venv,
)


def test_relationship():
    assert_test_module_name_embeds_str(
        switch_to_venv.__name__,
    )


class TestSuite:

    # noinspection PyAttributeOutsideInit
    @pytest.fixture(autouse=True)
    def setup_mocks(
        self,
        mocker,
        monkeypatch,
    ):
        self.mock_execv = mocker.patch("os.execv")
        self.mock_path_exists = mocker.patch("os.path.exists")
        self.mock_is_venv = mocker.patch(f"{primer_kernel.__name__}.is_venv")

    @patch.dict(
        os.environ, {ConfConstInput.ext_env_var_PATH: "/some/original/path"}, clear=True
    )
    def test_in_venv(self):

        # given:

        self.mock_is_venv.return_value = True

        ref_root_path = "/mock/client/dir"

        # when:

        ret_val = switch_to_venv(ref_root_path)

        assert ret_val is True
        self.mock_execv.assert_not_called()
        self.mock_path_exists.assert_not_called()
        assert os.environ.get("PATH", "") == "/some/original/path"

    @patch.dict(
        os.environ, {ConfConstInput.ext_env_var_PATH: "/some/original/path"}, clear=True
    )
    def test_not_in_venv(self):

        # given:

        self.mock_is_venv.return_value = False
        self.mock_path_exists.return_value = True

        ref_root_path = "/mock/client/dir"

        # when:

        switch_to_venv(ref_root_path)

        # then:

        expected_venv_bin = os.path.join(
            ref_root_path,
            # TODO: This might be passed as arg to the func (that being a default):
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_bin,
        )
        expected_venv_python = os.path.join(
            ref_root_path,
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

        assert os.environ[ConfConstInput.ext_env_var_PATH].startswith(
            expected_venv_bin + os.pathsep
        )
        assert os.environ[ConfConstInput.ext_env_var_PATH].endswith(
            "/some/original/path"
        )

        self.mock_path_exists.assert_called_once_with(expected_venv_python)

    def test_venv_python_does_not_exist(self):

        # given:

        self.mock_is_venv.return_value = False
        self.mock_path_exists.return_value = False

        ref_root_path = "/mock/client/dir"

        # when:

        with pytest.raises(AssertionError) as exc_info:
            switch_to_venv(ref_root_path)

        # then:

        expected_venv_python = os.path.join(
            ref_root_path,
            ConfConstEnv.default_dir_rel_path_venv,
            ConfConstGeneral.file_rel_path_venv_python,
        )

        assert str(exc_info.value) == (
            f"`{expected_venv_python}` does not exist - has `venv` been bootstrapped?"
        )

        self.mock_execv.assert_not_called()
        self.mock_path_exists.assert_called_once_with(expected_venv_python)
