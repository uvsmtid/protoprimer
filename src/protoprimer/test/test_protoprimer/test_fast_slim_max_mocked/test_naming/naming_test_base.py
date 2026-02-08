from __future__ import annotations

from test_protoprimer.test_fast_slim_max_mocked.test_naming.naming_metadata import (
    verify_naming_convention,
)


class NamingTestBase:
    prod_enum = None
    test_enum = None
    enum_prefix: str = None

    def test_naming_convention(self):
        for test_enum_item in self.test_enum:
            verify_naming_convention(test_enum_item.value)

    def test_prod_enum_item_values_embed_enum_item_names(self):
        for test_enum_item in self.test_enum:
            assert (
                test_enum_item.name[len(self.enum_prefix) :]
                if test_enum_item.name.startswith(self.enum_prefix)
                else test_enum_item.name
            ) in test_enum_item.value.extract_prod_item_value_name()

    def test_enum_items_are_assigned_correctly(self):
        for test_enum_item in self.test_enum:
            assert test_enum_item.name == test_enum_item.value.get_prod_item().name

    def test_prod_enum_name_is_not_embedded_in_any_other_prod_enum_name(self):
        for prod_enum_a in self.prod_enum:
            for prod_enum_b in self.prod_enum:
                if prod_enum_a.name != prod_enum_b.name:
                    assert prod_enum_a.name not in prod_enum_b.name

    def test_every_prod_in_test_and_vice_versa(self):
        prod_enum_names = [prod_enum.name for prod_enum in self.prod_enum]
        test_enum_names = [test_enum.name for test_enum in self.test_enum]

        # prod_enum -> test_enum:
        for prod_enum_name in prod_enum_names:
            if prod_enum_name not in test_enum_names:
                raise AssertionError(
                    f"`{self.prod_enum.__name__}`: prod [{prod_enum_name}] not in test"
                )

        # test_enum -> prod_enum:
        for test_enum_name in test_enum_names:
            if test_enum_name not in prod_enum_names:
                raise AssertionError(
                    f"`{self.prod_enum.__name__}`: test [{test_enum_name}] not in prod"
                )
