from __future__ import annotations

import enum

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import EnvVar
from test_protoprimer.test_fast_slim_max_mocked.test_naming.naming_metadata import (
    AbstractMeta,
    NameCategory,
)
from test_protoprimer.test_fast_slim_max_mocked.test_naming.naming_test_base import (
    NamingTestBase,
)


class EnvVarMeta(AbstractMeta):

    def __init__(
        self,
        env_var: EnvVar,
        name_category: NameCategory,
    ):
        self.env_var: EnvVar = env_var
        self.name_category: NameCategory = name_category

    def get_prod_item(self):
        return self.env_var

    def extract_prod_item_value_name(self) -> str:
        return self.env_var.value

    def get_name(self):
        return self.env_var.value

    def get_category(self):
        return self.name_category


class EnvVarName(enum.Enum):
    var_PROTOPRIMER_STDERR_LOG_LEVEL = EnvVarMeta(
        EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL,
        NameCategory.category_name_only,
    )
    var_PROTOPRIMER_PY_EXEC = EnvVarMeta(
        EnvVar.var_PROTOPRIMER_PY_EXEC,
        NameCategory.category_name_only,
    )
    var_PROTOPRIMER_DO_INSTALL = EnvVarMeta(
        EnvVar.var_PROTOPRIMER_DO_INSTALL,
        NameCategory.category_name_only,
    )
    var_PROTOPRIMER_PROTO_CODE = EnvVarMeta(
        EnvVar.var_PROTOPRIMER_PROTO_CODE,
        NameCategory.category_name_only,
    )
    var_PROTOPRIMER_CONF_BASENAME = EnvVarMeta(
        EnvVar.var_PROTOPRIMER_CONF_BASENAME,
        NameCategory.category_name_only,
    )
    var_PROTOPRIMER_START_ID = EnvVarMeta(
        EnvVar.var_PROTOPRIMER_START_ID,
        NameCategory.category_name_only,
    )
    var_PROTOPRIMER_PACKAGE_DRIVER = EnvVarMeta(
        EnvVar.var_PROTOPRIMER_PACKAGE_DRIVER,
        NameCategory.category_name_only,
    )
    var_PROTOPRIMER_TEST_MODE = EnvVarMeta(
        EnvVar.var_PROTOPRIMER_TEST_MODE,
        NameCategory.category_name_only,
    )


class TestEnvVarName(NamingTestBase):
    prod_enum = EnvVar
    test_enum = EnvVarName
    enum_prefix: str = "var_"

    def test_module_naming(self):
        assert_test_module_name_embeds_str(
            self.prod_enum.__name__,
        )
