from __future__ import annotations

from types import CodeType
from typing import Any

import pytest

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    AbstractConfigNode,
    AbstractDictNode,
    AbstractListNode,
    AbstractRootNode,
    AbstractValueNode,
)

some_var: str = "some_var"


# noinspection PyMethodMayBeStatic
class AbstractConfigBuilder:

    def build_config(
        self,
        var_name: str,
        config_data: dict,
    ) -> AbstractRootNode:
        base_indent = 0
        dict_node = self._build_dict_node(base_indent, config_data)
        return AbstractRootNode(
            node_indent=base_indent,
            config_data=config_data,
            var_name=var_name,
            dict_node=dict_node,
        )

    def _build_node(
        self,
        node_indent: int,
        config_data: Any,
    ) -> AbstractConfigNode:
        if isinstance(config_data, dict):
            return self._build_dict_node(node_indent, config_data)
        elif isinstance(config_data, list):
            return self._build_list_node(node_indent, config_data)
        else:
            return self._build_value_node(node_indent, config_data)

    def _build_dict_node(
        self,
        node_indent: int,
        config_data: dict,
    ) -> AbstractDictNode:
        config_node = AbstractDictNode(node_indent=node_indent)
        for field_name, field_value in config_data.items():
            child_node = self._build_node(
                node_indent=node_indent + AbstractConfigNode.indent_child_dict,
                config_data=field_value,
            )
            config_node.child_nodes[field_name] = child_node
        return config_node

    def _build_list_node(
        self,
        node_indent: int,
        config_data: list,
    ) -> AbstractListNode:
        config_node = AbstractListNode(node_indent=node_indent)
        for list_item in config_data:
            child_node = self._build_node(
                node_indent=node_indent + AbstractConfigNode.indent_child_list,
                config_data=list_item,
            )
            config_node.child_nodes.append(child_node)
        return config_node

    def _build_value_node(
        self,
        node_indent: int,
        config_data: Any,
    ) -> AbstractValueNode:
        config_node = AbstractValueNode(
            node_indent=node_indent + AbstractConfigNode.indent_child_value,
            is_present=True,
            config_data=config_data,
        )
        return config_node


def test_relationship():
    assert_test_module_name_embeds_str(AbstractConfigBuilder.__name__)


def test_build_graph():
    config_data = {
        "a": 1,
        "b": "hello",
        "c": True,
        "d": [
            1,
            2,
            3,
        ],
        "e": {
            "f": "nested",
        },
    }

    abstract_config_builder = AbstractConfigBuilder()
    root_node = abstract_config_builder.build_config(
        some_var,
        config_data,
    )

    assert isinstance(root_node, AbstractRootNode)
    dict_node = root_node.dict_node
    assert isinstance(dict_node, AbstractDictNode)

    assert isinstance(dict_node.child_nodes["a"], AbstractValueNode)
    assert dict_node.child_nodes["a"].config_data == 1

    assert isinstance(dict_node.child_nodes["b"], AbstractValueNode)
    assert dict_node.child_nodes["b"].config_data == "hello"

    assert isinstance(dict_node.child_nodes["c"], AbstractValueNode)
    assert dict_node.child_nodes["c"].config_data is True

    assert isinstance(dict_node.child_nodes["d"], AbstractListNode)
    assert isinstance(dict_node.child_nodes["d"].child_nodes[0], AbstractValueNode)
    assert dict_node.child_nodes["d"].child_nodes[0].config_data == 1

    assert isinstance(dict_node.child_nodes["e"], AbstractDictNode)
    assert isinstance(dict_node.child_nodes["e"].child_nodes["f"], AbstractValueNode)
    assert dict_node.child_nodes["e"].child_nodes["f"].config_data == "nested"


def test_render_config():
    config_data = {
        "a": 1,
        "b": "hello",
        "c": True,
        "d": [
            1,
            2,
            3,
        ],
        "e": {
            "f": "nested",
        },
    }

    abstract_config_builder = AbstractConfigBuilder()
    root_node = abstract_config_builder.build_config(
        some_var,
        config_data,
    )

    expected_output = """\
# some help for [dict]
some_var = {
    "a":
        # some help for [int]
        1,
    "b":
        # some help for [str]
        "hello",
    "c":
        # some help for [bool]
        True,
    "d":
        [
            # some help for [int]
            1,
            # some help for [int]
            2,
            # some help for [int]
            3,
        ],
    "e":
        {
            "f":
                # some help for [str]
                "nested",
        },
}
"""
    assert root_node.render_node() == expected_output


def test_render_multiline_annotation(monkeypatch):
    config_data = {
        "a": 1,
    }

    monkeypatch.setattr(
        primer_kernel.AbstractValueNode,
        "_get_annotation",
        lambda *_, **__: "multi-line\nannotation\n",
    )

    abstract_config_builder = AbstractConfigBuilder()
    root_node = abstract_config_builder.build_config(
        some_var,
        config_data,
    )

    expected_output = """\
# multi-line
# annotation
some_var = {
    "a":
        # multi-line
        # annotation
        1,
}
"""
    assert root_node.render_node() == expected_output


def test_render_node_generates_compilable_python():
    config_data = {
        "a": 1,
        "b": "hello",
        "c": True,
        "d": [
            1,
            2,
            3,
        ],
        "e": {
            "f": "nested",
        },
    }

    abstract_config_builder = AbstractConfigBuilder()
    root_node = abstract_config_builder.build_config(
        some_var,
        config_data,
    )

    effective_config = root_node.compile_effective_config()

    assert effective_config == config_data
