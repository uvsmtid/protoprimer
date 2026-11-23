import os
from unittest.mock import (
    patch,
)

from local_test.base_test_class import BasePyfakefsTestClass
from local_test.mock_verifier import (
    assert_parent_factories_mocked,
)
from local_test.name_assertion import assert_test_module_name_embeds_str
from local_test.path_helper import abs_path
from protoprimer.primer_kernel import (
    _EnvContext,
    _EnvState,
    EnvVar,
)


# noinspection PyPep8Naming
class ThisTestClass(BasePyfakefsTestClass):

    def setUp(self):
        self.setUpPyfakefs()
        self.env_ctx = _EnvContext()

    # noinspection PyMethodMayBeStatic
    def test_relationship(self):
        assert_test_module_name_embeds_str(_EnvState.state_input_proto_kernel_file_abs_path_var_loaded.name)

    @patch.dict(
        f"{os.__name__}.environ",
        {},
        clear=True,
    )
    def test_success_when_proto_kernel_file_abs_path_is_not_set(
        self,
    ):
        # given:
        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_input_proto_kernel_file_abs_path_var_loaded.name,
        )
        # when:
        state_value = self.env_ctx.eval_state(_EnvState.state_input_proto_kernel_file_abs_path_var_loaded.name)
        # then:
        self.assertIsNone(state_value)

    @patch.dict(
        f"{os.__name__}.environ",
        {EnvVar.var_PROTOPRIMER_PROTO_KERNEL.value: "relative/path"},
        clear=True,
    )
    def test_failure_when_proto_kernel_file_abs_path_is_not_abs(
        self,
    ):
        # given:
        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_input_proto_kernel_file_abs_path_var_loaded.name,
        )
        # when/then:
        with self.assertRaises(AssertionError):
            self.env_ctx.eval_state(
                _EnvState.state_input_proto_kernel_file_abs_path_var_loaded.name,
            )

    @patch.dict(
        f"{os.__name__}.environ",
        {EnvVar.var_PROTOPRIMER_PROTO_KERNEL.value: abs_path("/abs/path/not_exist")},
        clear=True,
    )
    def test_failure_when_proto_kernel_file_abs_path_does_not_exist(
        self,
    ):
        # given:
        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_input_proto_kernel_file_abs_path_var_loaded.name,
        )
        # when/then:
        with self.assertRaises(AssertionError):
            self.env_ctx.eval_state(
                _EnvState.state_input_proto_kernel_file_abs_path_var_loaded.name,
            )

    def test_success_when_proto_kernel_file_abs_path_is_set_and_exists(
        self,
    ):
        # given:
        # (`abs_path` is evaluated inside the test: the drive of the fake file system differs from the real one)
        self.fs.create_file(abs_path("/abs/path/exists"))
        assert_parent_factories_mocked(
            self.env_ctx,
            _EnvState.state_input_proto_kernel_file_abs_path_var_loaded.name,
        )
        # when:
        with patch.dict(
            f"{os.__name__}.environ",
            {EnvVar.var_PROTOPRIMER_PROTO_KERNEL.value: abs_path("/abs/path/exists")},
            clear=True,
        ):
            state_value = self.env_ctx.eval_state(_EnvState.state_input_proto_kernel_file_abs_path_var_loaded.name)
        # then:
        self.assertEqual(abs_path("/abs/path/exists"), state_value)
