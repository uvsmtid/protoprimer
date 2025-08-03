from __future__ import annotations

import enum

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    CommandArg,
    ConfField,
)
from test_protoprimer.test_naming.naming_metadata import (
    AbstractMeta,
    NameCategory,
)
from test_protoprimer.test_naming.naming_test_base import NamingTestBase


class FieldMeta(AbstractMeta):

    def __init__(
        self,
        field_name: FieldName,
        name_category: NameCategory,
    ):
        self.field_name: CommandArg = field_name
        self.name_category: NameCategory = name_category

    def get_prod_item(self):
        return self.field_name

    def extract_prod_item_value_name(self) -> str:
        return self.field_name.value

    def get_name(self):
        return self.field_name.value

    def get_category(self):
        return self.name_category


class FieldName(enum.Enum):

    field_primer_ref_root_dir_rel_path = FieldMeta(
        ConfField.field_primer_ref_root_dir_rel_path,
        NameCategory.category_path_field,
    )

    field_primer_conf_client_file_rel_path = FieldMeta(
        ConfField.field_primer_conf_client_file_rel_path,
        NameCategory.category_path_field,
    )

    field_client_link_name_dir_rel_path = FieldMeta(
        ConfField.field_client_link_name_dir_rel_path,
        NameCategory.category_path_field,
    )

    field_client_default_target_dir_rel_path = FieldMeta(
        ConfField.field_client_default_target_dir_rel_path,
        NameCategory.category_path_field,
    )

    field_env_local_python_file_abs_path = FieldMeta(
        ConfField.field_env_local_python_file_abs_path,
        NameCategory.category_path_field,
    )

    field_env_local_venv_dir_rel_path = FieldMeta(
        ConfField.field_env_local_venv_dir_rel_path,
        NameCategory.category_path_field,
    )

    field_env_project_rel_path_to_extras_dict = FieldMeta(
        ConfField.field_env_project_rel_path_to_extras_dict,
        NameCategory.category_value_field,
    )


class TestFieldName(NamingTestBase):
    prod_enum = ConfField
    test_enum = FieldName
    enum_prefix: str = "field_"

    def test_module_naming(self):
        assert_test_module_name_embeds_str(
            self.prod_enum.__name__,
        )
