from __future__ import annotations

import copy

from local_test.config_node import build_root_node
from protoprimer import primer_kernel
from protoprimer.primer_kernel import (
    AbstractDictNode,
    AbstractListNode,
    AbstractRootNode,
    AbstractValueNode,
    RenderConfigVisitor,
    TermColor,
)

some_var: str = "some_var"

common_sample = {
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
    "f": [
        4,
        5,
        [
            6,
            7,
        ],
        8,
    ],
}


def test_build_config_graph():
    config_data = copy.deepcopy(common_sample)

    root_node = build_root_node(
        some_var,
        config_data,
    )

    assert isinstance(root_node, AbstractRootNode)
    dict_node = root_node.child_node
    assert isinstance(dict_node, AbstractDictNode)

    assert isinstance(dict_node.child_nodes["a"], AbstractValueNode)
    assert dict_node.child_nodes["a"].orig_data == 1

    assert isinstance(dict_node.child_nodes["b"], AbstractValueNode)
    assert dict_node.child_nodes["b"].orig_data == "hello"

    assert isinstance(dict_node.child_nodes["c"], AbstractValueNode)
    assert dict_node.child_nodes["c"].orig_data is True

    d_node = dict_node.child_nodes["d"]
    assert isinstance(d_node, AbstractListNode)
    assert isinstance(d_node.child_nodes[0], AbstractValueNode)
    assert d_node.child_nodes[0].orig_data == 1

    e_node = dict_node.child_nodes["e"]
    assert isinstance(e_node, AbstractDictNode)
    assert isinstance(e_node.child_nodes["f"], AbstractValueNode)
    assert e_node.child_nodes["f"].orig_data == "nested"

    f_node = dict_node.child_nodes["f"]
    assert isinstance(f_node, AbstractListNode)
    assert isinstance(f_node.child_nodes[0], AbstractValueNode)
    assert f_node.child_nodes[0].orig_data == 4
    assert isinstance(f_node.child_nodes[1], AbstractValueNode)
    assert f_node.child_nodes[1].orig_data == 5

    f_node_child_2 = f_node.child_nodes[2]
    assert isinstance(f_node_child_2, AbstractListNode)
    assert isinstance(f_node_child_2.child_nodes[0], AbstractValueNode)
    assert f_node_child_2.child_nodes[0].orig_data == 6
    assert isinstance(f_node_child_2.child_nodes[1], AbstractValueNode)
    assert f_node_child_2.child_nodes[1].orig_data == 7
    assert isinstance(f_node.child_nodes[3], AbstractValueNode)
    assert f_node.child_nodes[3].orig_data == 8


def test_render_config():
    config_data = copy.deepcopy(common_sample)

    root_node = build_root_node(
        some_var,
        config_data,
    )

    expected_output = f"""
{TermColor.config_comment.value}# some help for [AbstractRootNode]{TermColor.reset_style.value}
some_var = (
    \n\
    {TermColor.config_comment.value}# some help for [AbstractDictNode]{TermColor.reset_style.value}
    {{
        \n\
        {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
        "a": 1,
        \n\
        {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
        "b": "hello",
        \n\
        {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
        "c": True,
        \n\
        {TermColor.config_comment.value}# some help for [AbstractListNode]{TermColor.reset_style.value}
        "d": [
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            1,
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            2,
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            3,
        ],
        \n\
        {TermColor.config_comment.value}# some help for [AbstractDictNode]{TermColor.reset_style.value}
        "e": {{
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            "f": "nested",
        }},
        \n\
        {TermColor.config_comment.value}# some help for [AbstractListNode]{TermColor.reset_style.value}
        "f": [
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            4,
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            5,
            \n\
            {TermColor.config_comment.value}# some help for [AbstractListNode]{TermColor.reset_style.value}
            [
                \n\
                {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
                6,
                \n\
                {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
                7,
            ],
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            8,
        ],
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output


def test_render_node_generates_compilable_python():
    config_data = copy.deepcopy(common_sample)

    root_node = build_root_node(
        some_var,
        config_data,
    )

    effective_config = root_node.compile_effective_config()

    assert effective_config == config_data


def test_render_config_not_present():
    config_data = copy.deepcopy(common_sample)

    root_node = build_root_node(
        some_var,
        config_data,
    )

    assert isinstance(root_node.child_node, AbstractDictNode)
    # Set "c" to not present
    root_node.child_node.child_nodes["c"].is_present = False

    expected_output = f"""
{TermColor.config_comment.value}# some help for [AbstractRootNode]{TermColor.reset_style.value}
some_var = (
    \n\
    {TermColor.config_comment.value}# some help for [AbstractDictNode]{TermColor.reset_style.value}
    {{
        \n\
        {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
        "a": 1,
        \n\
        {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
        "b": "hello",
        \n\
        {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
        {TermColor.config_comment.value}# "c": True,{TermColor.reset_style.value}
        \n\
        {TermColor.config_comment.value}# some help for [AbstractListNode]{TermColor.reset_style.value}
        "d": [
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            1,
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            2,
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            3,
        ],
        \n\
        {TermColor.config_comment.value}# some help for [AbstractDictNode]{TermColor.reset_style.value}
        "e": {{
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            "f": "nested",
        }},
        \n\
        {TermColor.config_comment.value}# some help for [AbstractListNode]{TermColor.reset_style.value}
        "f": [
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            4,
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            5,
            \n\
            {TermColor.config_comment.value}# some help for [AbstractListNode]{TermColor.reset_style.value}
            [
                \n\
                {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
                6,
                \n\
                {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
                7,
            ],
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            8,
        ],
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output


def test_render_multiline_annotation(monkeypatch):
    config_data = {
        "a": 1,
    }

    root_node = build_root_node(
        some_var,
        config_data,
    )

    assert isinstance(root_node.child_node, AbstractDictNode)
    value_node = root_node.child_node.child_nodes["a"]
    value_node.note_text = """\
multi-line
annotation
"""

    expected_output = f"""
{TermColor.config_comment.value}# some help for [AbstractRootNode]{TermColor.reset_style.value}
some_var = (
    \n\
    {TermColor.config_comment.value}# some help for [AbstractDictNode]{TermColor.reset_style.value}
    {{
        \n\
        {TermColor.config_comment.value}# multi-line{TermColor.reset_style.value}
        {TermColor.config_comment.value}# annotation{TermColor.reset_style.value}
        "a": 1,
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output


def test_render_config_nested_dict_not_present():
    config_data = {
        "a": 1,
        "l1": {
            "l2": {
                "l3": {
                    "l4": "nested",
                },
            },
        },
        "b": 2,
    }

    root_node = build_root_node(
        some_var,
        config_data,
    )

    assert isinstance(root_node.child_node, AbstractDictNode)
    # Set "l2": (a dict) to not present
    l1_node = root_node.child_node.child_nodes["l1"]
    assert isinstance(l1_node, AbstractDictNode)
    l1_node.child_nodes["l2"].is_present = False

    expected_output = f"""
{TermColor.config_comment.value}# some help for [AbstractRootNode]{TermColor.reset_style.value}
some_var = (
    \n\
    {TermColor.config_comment.value}# some help for [AbstractDictNode]{TermColor.reset_style.value}
    {{
        \n\
        {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
        "a": 1,
        \n\
        {TermColor.config_comment.value}# some help for [AbstractDictNode]{TermColor.reset_style.value}
        "l1": {{
            \n\
            {TermColor.config_comment.value}# some help for [AbstractDictNode]{TermColor.reset_style.value}
            {TermColor.config_comment.value}# "l2": {{{TermColor.reset_style.value}
            {TermColor.config_comment.value}#     {TermColor.reset_style.value}
            {TermColor.config_comment.value}#     {TermColor.config_comment.value}# some help for [AbstractDictNode]{TermColor.reset_style.value}{TermColor.reset_style.value}
            {TermColor.config_comment.value}#     "l3": {{{TermColor.reset_style.value}
            {TermColor.config_comment.value}#         {TermColor.reset_style.value}
            {TermColor.config_comment.value}#         {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}{TermColor.reset_style.value}
            {TermColor.config_comment.value}#         "l4": "nested",{TermColor.reset_style.value}
            {TermColor.config_comment.value}#     }},{TermColor.reset_style.value}
            {TermColor.config_comment.value}# }},{TermColor.reset_style.value}
        }},
        \n\
        {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
        "b": 2,
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output


def test_render_config_nested_list_not_present():
    config_data = {
        "a": 1,
        "f": [
            4,
            5,
            [
                6,
                7,
            ],
            8,
        ],
        "b": 2,
    }

    root_node = build_root_node(
        some_var,
        config_data,
    )

    assert isinstance(root_node.child_node, AbstractDictNode)
    # Set the nested list to not present
    f_node = root_node.child_node.child_nodes["f"]
    assert isinstance(f_node, AbstractListNode)
    nested_list_node = f_node.child_nodes[2]
    nested_list_node.is_present = False

    expected_output = f"""
{TermColor.config_comment.value}# some help for [AbstractRootNode]{TermColor.reset_style.value}
some_var = (
    \n\
    {TermColor.config_comment.value}# some help for [AbstractDictNode]{TermColor.reset_style.value}
    {{
        \n\
        {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
        "a": 1,
        \n\
        {TermColor.config_comment.value}# some help for [AbstractListNode]{TermColor.reset_style.value}
        "f": [
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            4,
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            5,
            \n\
            {TermColor.config_comment.value}# some help for [AbstractListNode]{TermColor.reset_style.value}
            {TermColor.config_comment.value}# [{TermColor.reset_style.value}
            {TermColor.config_comment.value}#     {TermColor.reset_style.value}
            {TermColor.config_comment.value}#     {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}{TermColor.reset_style.value}
            {TermColor.config_comment.value}#     6,{TermColor.reset_style.value}
            {TermColor.config_comment.value}#     {TermColor.reset_style.value}
            {TermColor.config_comment.value}#     {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}{TermColor.reset_style.value}
            {TermColor.config_comment.value}#     7,{TermColor.reset_style.value}
            {TermColor.config_comment.value}# ],{TermColor.reset_style.value}
            \n\
            {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
            8,
        ],
        \n\
        {TermColor.config_comment.value}# some help for [AbstractValueNode]{TermColor.reset_style.value}
        "b": 2,
    }}
)\
"""
    assert RenderConfigVisitor().render_node(root_node) == expected_output


def test_render_config_quiet():
    config_data = copy.deepcopy(common_sample)

    root_node = build_root_node(
        some_var,
        config_data,
    )

    expected_output = f"""some_var = (
    {{
        "a": 1,
        "b": "hello",
        "c": True,
        "d": [
            1,
            2,
            3,
        ],
        "e": {{
            "f": "nested",
        }},
        "f": [
            4,
            5,
            [
                6,
                7,
            ],
            8,
        ],
    }}
)"""
    assert RenderConfigVisitor(is_quiet=True).render_node(root_node) == expected_output


def test_abstract_config_visitor():
    # Create an instance of the visitor
    visitor = primer_kernel.AbstractConfigVisitor()

    # Create a sample config structure
    config_data = copy.deepcopy(common_sample)
    root_node = build_root_node(some_var, config_data)

    # Test visit_root
    assert visitor.visit_root(root_node) is None

    dict_node = root_node.child_node
    # Test visit_dict
    assert visitor.visit_dict(dict_node) is None

    value_node = dict_node.child_nodes["a"]
    # Test visit_value
    assert visitor.visit_value(value_node) is None

    list_node = dict_node.child_nodes["d"]
    # Test visit_list
    assert visitor.visit_list(list_node) is None
