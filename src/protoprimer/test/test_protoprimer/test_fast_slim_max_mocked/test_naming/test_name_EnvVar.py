from __future__ import annotations

import enum

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    ConfConstGeneral,
    EnvVar,
    KeyWord,
    PathName,
    ValueName,
)
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
        name_components: list[str],
    ):
        self.env_var: EnvVar = env_var
        self.name_category: NameCategory = name_category
        self.name_components: list[str] = name_components

    def get_prod_item(self):
        return self.env_var

    def extract_prod_item_value_name(self) -> str:
        return self.env_var.value

    def get_name(self):
        return self.env_var.value

    def get_category(self):
        return self.name_category

    def get_name_components(self) -> list[str]:
        return self.name_components


class EnvVarName(enum.Enum):
    var_PROTOPRIMER_MAIN_FUNC = EnvVarMeta(
        env_var=EnvVar.var_PROTOPRIMER_MAIN_FUNC,
        name_category=NameCategory.category_name_only,
        name_components=[
            ConfConstGeneral.name_protoprimer_package.upper(),
            KeyWord.key_main.value.upper(),
            KeyWord.key_func.value.upper(),
        ],
    )
    var_PROTOPRIMER_STDERR_LOG_LEVEL = EnvVarMeta(
        env_var=EnvVar.var_PROTOPRIMER_STDERR_LOG_LEVEL,
        name_category=NameCategory.category_name_only,
        name_components=[
            ConfConstGeneral.name_protoprimer_package.upper(),
            KeyWord.key_stderr.value.upper(),
            KeyWord.key_log.value.upper(),
            KeyWord.key_level.value.upper(),
        ],
    )
    var_PROTOPRIMER_PY_EXEC = EnvVarMeta(
        env_var=EnvVar.var_PROTOPRIMER_PY_EXEC,
        name_category=NameCategory.category_name_only,
        name_components=[
            ConfConstGeneral.name_protoprimer_package.upper(),
            ValueName.value_py_exec.value.upper(),
        ],
    )
    var_PROTOPRIMER_DO_INSTALL = EnvVarMeta(
        env_var=EnvVar.var_PROTOPRIMER_DO_INSTALL,
        name_category=NameCategory.category_name_only,
        name_components=[
            ConfConstGeneral.name_protoprimer_package.upper(),
            KeyWord.key_do.value.upper(),
            KeyWord.key_install.value.upper(),
        ],
    )
    var_PROTOPRIMER_PROTO_CODE = EnvVarMeta(
        env_var=EnvVar.var_PROTOPRIMER_PROTO_CODE,
        name_category=NameCategory.category_name_only,
        name_components=[
            ConfConstGeneral.name_protoprimer_package.upper(),
            PathName.path_proto_code.value.upper(),
        ],
    )
    var_PROTOPRIMER_CONF_BASENAME = EnvVarMeta(
        env_var=EnvVar.var_PROTOPRIMER_CONF_BASENAME,
        name_category=NameCategory.category_name_only,
        name_components=[
            ConfConstGeneral.name_protoprimer_package.upper(),
            KeyWord.key_conf.value.upper(),
            KeyWord.key_basename.value.upper(),
        ],
    )
    var_PROTOPRIMER_START_ID = EnvVarMeta(
        env_var=EnvVar.var_PROTOPRIMER_START_ID,
        name_category=NameCategory.category_name_only,
        name_components=[
            ConfConstGeneral.name_protoprimer_package.upper(),
            KeyWord.key_start.value.upper(),
            KeyWord.key_id.value.upper(),
        ],
    )
    var_PROTOPRIMER_VENV_DRIVER = EnvVarMeta(
        env_var=EnvVar.var_PROTOPRIMER_VENV_DRIVER,
        name_category=NameCategory.category_name_only,
        name_components=[
            ConfConstGeneral.name_protoprimer_package.upper(),
            ValueName.value_venv_driver.value.upper(),
        ],
    )
    var_PROTOPRIMER_MOCKED_RESTART = EnvVarMeta(
        env_var=EnvVar.var_PROTOPRIMER_MOCKED_RESTART,
        name_category=NameCategory.category_name_only,
        name_components=[
            ConfConstGeneral.name_protoprimer_package.upper(),
            KeyWord.key_mocked.value.upper(),
            KeyWord.key_restart.value.upper(),
        ],
    )


class TestEnvVarName(NamingTestBase):
    prod_enum = EnvVar
    test_enum = EnvVarName
    enum_prefix: str = "var_"

    def test_module_naming(self):
        assert_test_module_name_embeds_str(
            self.prod_enum.__name__,
        )
