import os
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str

# noinspection PyProtectedMember
from protoprimer.primer_kernel import (
    _start_main,
    app_starter,
    env_bootstrapper,
    EnvVar,
    RunMode,
    StateStride,
)


def test_relationship():
    assert_test_module_name_embeds_str(env_bootstrapper.__name__)
    assert_test_module_name_embeds_str(app_starter.__name__)


class TestStartMain:

    @pytest.fixture(autouse=True)
    def setup_mocks(self, mocker):
        self.mock_app_main = mocker.patch("protoprimer.primer_kernel.app_main")
        self.mock_import_module = mocker.patch(
            "protoprimer.primer_kernel.importlib.import_module"
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_invalid_main_func_format(self):
        with pytest.raises(ValueError):
            _start_main(RunMode.mode_prime, "invalid_format")

    @patch.dict(
        os.environ,
        {EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_src_updated.name},
        clear=True,
    )
    def test_stride_src_updated(self):
        # given
        mock_module = MagicMock()
        mock_func = MagicMock()
        mock_module.my_func = mock_func
        self.mock_import_module.return_value = mock_module

        # when
        _start_main(RunMode.mode_prime, "my_module:my_func")

        # then
        self.mock_import_module.assert_called_once_with("my_module")
        mock_func.assert_called_once()
        self.mock_app_main.assert_not_called()

    @patch.dict(
        os.environ,
        {EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_deps_updated.name},
        clear=True,
    )
    def test_stride_deps_updated(self):
        # given
        mock_module = MagicMock()
        mock_func = MagicMock()
        mock_module.app_main = mock_func
        self.mock_import_module.return_value = mock_module

        # when
        _start_main(RunMode.mode_prime, "my_module:my_func")

        # then
        self.mock_import_module.assert_called_once_with("protoprimer.primer_kernel")
        mock_func.assert_called_once()
        self.mock_app_main.assert_not_called()

    @patch.dict(
        os.environ,
        {EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_src_updated.name},
        clear=True,
    )
    def test_import_error_with_stride_src_updated(self):
        # given
        self.mock_import_module.side_effect = ImportError

        # when/then
        with pytest.raises(AssertionError):
            _start_main(RunMode.mode_prime, "my_module:my_func")

    @patch.dict(
        os.environ,
        {EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name},
        clear=True,
    )
    def test_import_error_with_lower_stride(self):
        # given
        self.mock_import_module.side_effect = ImportError

        # when
        _start_main(RunMode.mode_prime, "my_module:my_func")

        # then
        self.mock_app_main.assert_called_once()

    @patch.dict(
        os.environ,
        {EnvVar.var_PROTOPRIMER_PY_EXEC.value: StateStride.stride_py_venv.name},
        clear=True,
    )
    def test_default_case(self):
        # when
        _start_main(RunMode.mode_prime, "my_module:my_func")

        # then
        self.mock_import_module.assert_not_called()
        self.mock_app_main.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_run_mode_and_main_func_env_vars_set(self):
        # when
        _start_main(RunMode.mode_start, "my_module:my_func")

        # then
        assert (
            os.environ[EnvVar.var_PROTOPRIMER_RUN_MODE.value]
            == RunMode.mode_start.value
        )
        assert os.environ[EnvVar.var_PROTOPRIMER_MAIN_FUNC.value] == "my_module:my_func"
        self.mock_app_main.assert_called_once()


class TestEnvBootstrapperAndAppStarter:

    @pytest.fixture(autouse=True)
    def setup_mocks(self, mocker):
        self.mock_app_main = mocker.patch("protoprimer.primer_kernel.app_main")
        self.mock_import_module = mocker.patch(
            "protoprimer.primer_kernel.importlib.import_module"
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_env_bootstrapper(self):
        # given
        main_func = "my_module:my_func"

        # when
        env_bootstrapper(main_func)

        # then
        assert (
            os.environ[EnvVar.var_PROTOPRIMER_RUN_MODE.value]
            == RunMode.mode_prime.value
        )
        assert os.environ[EnvVar.var_PROTOPRIMER_MAIN_FUNC.value] == main_func
        self.mock_app_main.assert_called_once()
        self.mock_import_module.assert_not_called()  # _start_main calls app_main by default if stride is not high enough

    @patch.dict(os.environ, {}, clear=True)
    def test_app_starter(self):
        # given
        main_func = "my_module:my_func"

        # when
        app_starter(main_func)

        # then
        assert (
            os.environ[EnvVar.var_PROTOPRIMER_RUN_MODE.value]
            == RunMode.mode_start.value
        )
        assert os.environ[EnvVar.var_PROTOPRIMER_MAIN_FUNC.value] == main_func
        self.mock_app_main.assert_called_once()
        self.mock_import_module.assert_not_called()  # _start_main calls app_main by default if stride is not high enough
