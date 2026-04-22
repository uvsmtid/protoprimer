from __future__ import annotations

import enum
import json
import logging
import os
from types import CodeType
from typing import (
    Any,
    Generic,
)

from protoprimer.primer_kernel import (
    AbstractCachingStateNode,
    ConfConstClient,
    ConfConstEnv,
    ConfConstGeneral,
    ConfConstInput,
    ConfField,
    ConfLeap,
    EnvContext,
    EnvState,
    ExecMode,
    missing_conf_file_message,
    PathName,
    read_json_file,
    SelectorFunc,
    SyntaxArg,
    TermColor,
    trivial_factory,
    ValueType,
    VenvDriverType,
    warn_once_at_state_stride,
)


########################################################################################################################
# Visitors for config nodes.
# See: FT_19_44_42_19.effective_config.md


class AbstractConfigVisitor:
    """
    Implements the visitor pattern for classed derived from `AbstractConfigNode`.
    """

    def visit_dict(
        self,
        dict_node: "AbstractDictNode",
        **kwargs,
    ) -> None:
        pass

    def visit_list(
        self,
        list_node: "AbstractListNode",
        **kwargs,
    ) -> None:
        pass

    def visit_value(
        self,
        value_node: "AbstractValueNode",
        **kwargs,
    ) -> None:
        pass

    def visit_root(
        self,
        root_node: "AbstractRootNode",
        **kwargs,
    ) -> None:
        pass


class RenderConfigVisitor(AbstractConfigVisitor):
    """
    Render a JSON-like data structure into data coded in `python` (with annotations as comments).

    It renders loaded config as: FT_19_44_42_19.effective_config.md
    """

    def __init__(
        self,
        is_quiet: bool = False,
    ):
        self.is_quiet: bool = is_quiet
        self.rendered_value: str = ""

    def render_node(
        self,
        config_node: "AbstractConfigNode",
    ) -> str:
        s: str = ""
        if not self.is_quiet:
            s += " " * config_node.node_indent + os.linesep
        s += self._render_node_annotation(config_node)

        rendered_value: str = self._render_node_value(config_node)
        if config_node.is_present:
            s += rendered_value
        else:
            s += self._comment_with_indent(
                rendered_value,
                config_node,
            )
        return s

    def _render_node_annotation(
        self,
        config_node: "AbstractConfigNode",
    ) -> str:
        if self.is_quiet:
            return ""
        note_text = config_node.note_text
        if len(note_text.strip()) == 0:
            return ""
        annotation_lines = note_text.splitlines()
        s = ""
        for annotation_line in annotation_lines:
            s += (
                " " * config_node.node_indent
                + f"{config_node.note_color.value}# {annotation_line}{TermColor.reset_style.value}"
                + os.linesep
                #
            )
        return s

    @staticmethod
    def _render_node_name(
        config_node: "AbstractConfigNode",
    ) -> str:
        if config_node.node_name is None:
            return ""
        return f"{json.dumps(config_node.node_name)}: "

    def _render_node_value(
        self,
        config_node: "AbstractConfigNode",
    ) -> str:
        config_node.accept_visitor(self)
        return self.rendered_value

    def _comment_with_indent(
        self,
        rendered_text: str,
        config_node: "AbstractConfigNode",
    ) -> str:
        if self.is_quiet:
            return ""
        deactivated_lines = []
        rendered_lines = rendered_text.splitlines()
        for rendered_line in rendered_lines:
            deactivated_lines.append(
                rendered_line[: config_node.node_indent]
                + f"{config_node.note_color.value}# "
                + rendered_line[config_node.node_indent :]
                + f"{TermColor.reset_style.value}"
                #
            )
        return os.linesep.join(deactivated_lines)

    def visit_dict(
        self,
        dict_node: "AbstractDictNode",
        **kwargs,
    ):
        s: str = ""
        s += (
            " " * dict_node.node_indent
            + self._render_node_name(dict_node)
            + "{"
            + os.linesep
            #
        )
        for child_name, child_node in dict_node.child_nodes.items():
            rendered_child = self.render_node(child_node)
            s += rendered_child
            if rendered_child or not self.is_quiet:
                s += os.linesep
        s += " " * dict_node.node_indent + "},"
        self.rendered_value = s

    def visit_list(
        self,
        list_node: "AbstractListNode",
        **kwargs,
    ):
        s: str = ""
        s += (
            " " * list_node.node_indent
            + self._render_node_name(list_node)
            + "["
            + os.linesep
            #
        )
        for child_node in list_node.child_nodes:
            rendered_child = self.render_node(child_node)
            s += rendered_child
            if rendered_child or not self.is_quiet:
                s += os.linesep
        s += " " * list_node.node_indent + "],"
        self.rendered_value = s

    def visit_value(
        self,
        value_node: "AbstractValueNode",
        **kwargs,
    ):
        s: str = ""
        if isinstance(value_node.orig_data, str):
            s += (
                " " * value_node.node_indent
                + self._render_node_name(value_node)
                # Use double-quote for `str`:
                + f"{json.dumps(value_node.orig_data)}"
                + ","
                #
            )
        else:
            s += (
                " " * value_node.node_indent
                + self._render_node_name(value_node)
                + f"{repr(value_node.orig_data)}"
                + ","
                #
            )
        self.rendered_value = s

    def visit_root(
        self,
        root_node: "AbstractRootNode",
        **kwargs,
    ):
        # Remove the last char (which is supposed to be `,`):
        rendered_child: str = self.render_node(root_node.child_node)[:-1]
        s: str = ""
        s += " " * root_node.node_indent + f"{root_node.node_name} = (" + os.linesep
        s += rendered_child + os.linesep
        s += " " * root_node.node_indent + ")"
        self.rendered_value = s


class ConfigBuilderVisitor(AbstractConfigVisitor):
    """
    Builds a config node and visits it to build children config nodes.
    """

    def build_config_node(
        self,
        orig_data: Any,
        **kwargs,
    ) -> "AbstractConfigNode":
        if isinstance(orig_data, dict):
            return self.build_dict_node(
                orig_data=orig_data,
                **kwargs,
            )
        elif isinstance(orig_data, list):
            return self.build_list_node(
                orig_data=orig_data,
                **kwargs,
            )
        else:
            return self.build_value_node(
                orig_data=orig_data,
                **kwargs,
            )

    def build_dict_node(
        self,
        **kwargs,
    ) -> "AbstractDictNode":
        kwargs.pop("is_present", None)
        return AbstractDictNode(
            is_present=True,
            child_builder=self,
            **kwargs,
        )

    def build_list_node(
        self,
        **kwargs,
    ) -> "AbstractListNode":
        kwargs.pop("is_present", None)
        return AbstractListNode(
            is_present=True,
            child_builder=self,
            **kwargs,
        )

    def build_value_node(
        self,
        **kwargs,
    ) -> "AbstractValueNode":
        kwargs.pop("is_present", None)
        return AbstractValueNode(
            is_present=True,
            **kwargs,
        )

    def build_root_node(
        self,
        **kwargs,
    ) -> "AbstractRootNode":
        kwargs.pop("is_present", None)
        return AbstractRootNode(
            is_present=True,
            child_builder=self,
            **kwargs,
        )

    def visit_dict(
        self,
        dict_node: "AbstractDictNode",
        **kwargs,
    ) -> None:
        if dict_node.orig_data is None:
            return
        kwargs.pop("node_name", None)
        kwargs.pop("node_indent", None)
        kwargs.pop("orig_data", None)
        for field_name, field_value in dict_node.orig_data.items():
            child_node = self.build_config_node(
                node_name=field_name,
                node_indent=dict_node.node_indent + AbstractConfigNode.indent_size,
                orig_data=field_value,
                **kwargs,
            )
            dict_node.child_nodes[field_name] = child_node

    def visit_list(
        self,
        list_node: "AbstractListNode",
        **kwargs,
    ) -> None:
        if list_node.orig_data is None:
            return
        kwargs.pop("node_name", None)
        kwargs.pop("node_indent", None)
        kwargs.pop("orig_data", None)
        for list_item in list_node.orig_data:
            child_node = self.build_config_node(
                node_name=None,
                node_indent=list_node.node_indent + AbstractConfigNode.indent_size,
                orig_data=list_item,
                **kwargs,
            )
            list_node.child_nodes.append(child_node)

    def visit_value(
        self,
        value_node: "AbstractValueNode",
        **kwargs,
    ) -> None:
        # Value nodes have no children.
        pass

    def visit_root(
        self,
        root_node: "AbstractRootNode",
        **kwargs,
    ) -> None:
        if root_node.orig_data is None:
            return
        kwargs.pop("node_name", None)
        kwargs.pop("node_indent", None)
        kwargs.pop("orig_data", None)
        root_node.child_node = self.build_config_node(
            node_name=None,
            node_indent=root_node.node_indent + AbstractConfigNode.indent_size,
            orig_data=root_node.orig_data,
            **kwargs,
        )


class AnnotateUnusedVisitor(AbstractConfigVisitor):
    """
    Annotates a config node as unused (not recursively).
    """

    def visit_dict(
        self,
        dict_node: "AbstractDictNode",
        **kwargs,
    ) -> None:
        dict_node.note_text = f"This `dict` is not used by the `{ConfConstGeneral.name_protoprimer_package}`."
        dict_node.note_color = TermColor.config_unused

    def visit_list(
        self,
        list_node: "AbstractListNode",
        **kwargs,
    ) -> None:
        list_node.note_text = f"This `list` is not used by the `{ConfConstGeneral.name_protoprimer_package}`."
        list_node.note_color = TermColor.config_unused

    def visit_value(
        self,
        value_node: "AbstractValueNode",
        **kwargs,
    ) -> None:
        value_node.note_text = f"This value is not used by the `{ConfConstGeneral.name_protoprimer_package}`."
        value_node.note_color = TermColor.config_unused

    def visit_root(
        self,
        root_node: "AbstractRootNode",
        **kwargs,
    ) -> None:
        root_node.note_text = f"This config is not used by the `{ConfConstGeneral.name_protoprimer_package}`."
        root_node.note_color = TermColor.config_unused


class UnusedConfigBuilderVisitor(ConfigBuilderVisitor):
    """
    Builds a config node (recursively) and annotates that top-level node as unused.
    """

    def __init__(
        self,
    ):
        self.recursion_level: int = 0

    def build_config_node(
        self,
        orig_data: Any,
        **kwargs,
    ) -> "AbstractConfigNode":
        self.recursion_level += 1
        config_node: AbstractConfigNode = super().build_config_node(
            orig_data=orig_data,
            **kwargs,
        )
        self.recursion_level -= 1
        if self.recursion_level == 0:
            # Set annotation only for the top-level node:
            config_node.accept_visitor(AnnotateUnusedVisitor())
        return config_node


########################################################################################################################
# Abstract config node types.
# See: FT_19_44_42_19.effective_config.md


class AbstractConfigNode(Generic[ValueType]):
    """
    Models a node in a JSON-like (nested) data structure.

    It loads config from: FT_48_62_07_98.config_format.md
    """

    indent_size: int = 4

    def __init__(
        self,
        node_name: str | None,
        node_indent: int,
        is_present: bool,
        orig_data: ValueType | None,
        **kwargs,
    ):
        self.node_name: str | None = node_name
        self.node_indent: int = node_indent

        # Unlike simply setting `orig_data` to `None`, setting `is_present` to `False`
        # allows distinguishing between (A) a valid `None` value and (B) a missing value.
        self.is_present: bool = is_present

        self.orig_data: ValueType | None = orig_data

        self.note_text: str = ""
        self.note_color: TermColor = TermColor.config_comment if is_present else TermColor.config_missing

    def accept_visitor(
        self,
        visitor: AbstractConfigVisitor,
        **kwargs,
    ) -> None:
        """
        Accept a `AbstractConfigVisitor`.
        """
        raise NotImplementedError()


class AbstractDictNode(AbstractConfigNode[dict]):
    """
    Models `{ ... }` JSON-like `dict`.
    """

    def __init__(
        self,
        child_builder: ConfigBuilderVisitor,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.child_nodes: dict[str, AbstractConfigNode] = {}
        self.accept_visitor(
            child_builder,
            **kwargs,
        )

    def accept_visitor(
        self,
        visitor: AbstractConfigVisitor,
        **kwargs,
    ) -> None:
        visitor.visit_dict(
            self,
            **kwargs,
        )


class AbstractListNode(AbstractConfigNode[list]):
    """
    Models `[ ... ]` JSON-like `list`.
    """

    def __init__(
        self,
        child_builder: ConfigBuilderVisitor,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.child_nodes: list[AbstractConfigNode] = []
        self.accept_visitor(
            child_builder,
            **kwargs,
        )

    def accept_visitor(
        self,
        visitor: AbstractConfigVisitor,
        **kwargs,
    ) -> None:
        visitor.visit_list(
            self,
            **kwargs,
        )


class AbstractValueNode(AbstractConfigNode[ValueType]):
    """
    Models any simple value in JSON-like data structure (neither `list` nor `dict`).
    """

    def __init__(
        self,
        orig_data: ValueType | None,
        **kwargs,
    ):
        super().__init__(
            orig_data=orig_data,
            **kwargs,
        )
        assert not isinstance(orig_data, list)
        assert not isinstance(orig_data, dict)

    def accept_visitor(
        self,
        visitor: AbstractConfigVisitor,
        **kwargs,
    ) -> None:
        visitor.visit_value(
            self,
            **kwargs,
        )


class AbstractRootNode(AbstractConfigNode[ValueType]):
    """
    Wraps any given `child_node` as `node_name = ( child_node )`.

    Syntactically, it represents an assignment to the `node_name` var and
    allows accessing the assigned data via `compile_effective_config`.
    """

    def __init__(
        self,
        child_builder: ConfigBuilderVisitor,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.child_node: AbstractConfigNode | None = None
        self.accept_visitor(
            child_builder,
            **kwargs,
        )

    def accept_visitor(
        self,
        visitor: AbstractConfigVisitor,
        **kwargs,
    ) -> None:
        visitor.visit_root(
            self,
            **kwargs,
        )

    def compile_effective_config(
        self,
    ) -> Any:
        """
        Produces rendered config and compiles it to access data.
        """
        generated_code = RenderConfigVisitor().render_node(self)
        # TODO: Instead, maybe configure rendering without colors?
        generated_code = self._erase_annotation_colors(generated_code)
        compiled_code: CodeType = compile(generated_code, "<string>", "exec")
        exec_namespace = {}
        exec(compiled_code, exec_namespace)
        return exec_namespace[self.node_name]

    @staticmethod
    def _erase_annotation_colors(
        generated_code: str,
    ):
        for term_color in [
            TermColor.config_comment,
            TermColor.config_missing,
            TermColor.config_unused,
            TermColor.reset_style,
        ]:
            generated_code = generated_code.replace(term_color.value, "")
        return generated_code


class AbstractConfLeapRootNode(AbstractRootNode):
    """
    Base implementation for all `ConfLeap.*`.
    """

    def __init__(
        self,
        conf_leap: ConfLeap,
        child_builder: ConfigBuilderVisitor,
        **kwargs,
    ):
        super().__init__(
            node_name=conf_leap.name,
            is_present=True,
            child_builder=child_builder,
            **kwargs,
        )


class AbstractConfLeapNodeBuilder(ConfigBuilderVisitor):

    @staticmethod
    def _create_used_dict_field(
        dict_node: AbstractDictNode,
        field_name: str,
        node_class: type,
        conf_leap: ConfLeap,
        **kwargs,
    ) -> AbstractDictNode:
        field_name = field_name
        kwargs.pop("is_present", None)
        kwargs.pop("orig_data", None)
        kwargs.pop("node_name", None)
        kwargs.pop("node_indent", None)
        field_node: AbstractConfigNode = node_class(
            node_name=field_name,
            node_indent=dict_node.node_indent + AbstractConfigNode.indent_size,
            is_present=(field_name in dict_node.orig_data),
            orig_data=dict_node.orig_data.get(field_name, None),
            conf_leap=conf_leap,
            **kwargs,
        )
        dict_node.child_nodes[field_name] = field_node
        return field_node

    def _create_common_fields(
        self,
        dict_node: AbstractDictNode,
        conf_leap: ConfLeap,
    ):
        # Common overridable `global` and `local` fields: FT_23_37_64_44.global_vs_local.md

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_required_python_version.value,
            node_class=Node_field_required_python_version,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_python_selector_file_rel_path.value,
            node_class=Node_field_python_selector_file_rel_path,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_local_venv_dir_rel_path.value,
            node_class=Node_field_local_venv_dir_rel_path,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_local_log_dir_rel_path.value,
            node_class=Node_field_local_log_dir_rel_path,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_local_tmp_dir_rel_path.value,
            node_class=Node_field_local_tmp_dir_rel_path,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_local_cache_dir_rel_path.value,
            node_class=Node_field_local_cache_dir_rel_path,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_venv_driver.value,
            node_class=Node_field_venv_driver,
            conf_leap=conf_leap,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_project_descriptors.value,
            node_class=Node_field_project_descriptors,
            conf_leap=conf_leap,
        )

    @staticmethod
    def _create_unused_dict_fields(
        dict_node: AbstractDictNode,
    ):
        for field_name, field_value in dict_node.orig_data.items():

            if field_name not in dict_node.child_nodes:
                dict_node.child_nodes[field_name] = UnusedConfigBuilderVisitor().build_config_node(
                    node_name=field_name,
                    node_indent=dict_node.node_indent + AbstractConfigNode.indent_size,
                    orig_data=field_value,
                )


########################################################################################################################
# `ConfLeap.leap_input` node types.
# See: FT_19_44_42_19.effective_config.md


# noinspection PyPep8Naming
class Builder_RootNode_input(AbstractConfLeapNodeBuilder):

    def visit_dict(
        self,
        dict_node: AbstractDictNode,
        **kwargs,
    ) -> None:

        conf_leap = ConfLeap.leap_input

        field_node: AbstractConfigNode

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_proto_code_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = (
            f"Value `{EnvState.state_proto_code_file_abs_path_inited.name}` is an absolute path to `{ConfConstGeneral.name_proto_code}`.\n"
            f"It allows resolving all other relative paths (via `{PathName.path_ref_root.value}` - see field `{ConfField.field_ref_root_dir_rel_path.value}`).\n"
            #
        )

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_primer_conf_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        # TODO: Link to `ConfLeap.leap_derived` fields.
        field_node.note_text = (
            f"Value `{EnvState.state_primer_conf_file_abs_path_inited.name}` is an absolute path to `{ConfLeap.leap_primer}` config file.\n"
            f"The config file is selected from the list of possible candidates (whichever is found first, replacing extension to `.{ConfConstInput.conf_file_ext}`):\n"
            f"*   basename of the entry script,\n"
            f"*   basename of the `{ConfConstGeneral.name_proto_code}` file,\n"
            f"*   default `{ConfConstInput.default_file_basename_conf_primer}`.\n"
            f"Note that the selected config file basename is subsequently re-used for others:\n"
            f"*   see `{EnvState.state_global_conf_file_abs_path_inited.name}` for `{ConfLeap.leap_client.name}`,\n"
            f"*   see `{EnvState.state_local_conf_file_abs_path_inited.name}` for `{ConfLeap.leap_env.name}`.\n"
            #
        )

        self._create_unused_dict_fields(dict_node)


# noinspection PyPep8Naming
class RootNode_input(AbstractConfLeapRootNode):
    """
    Root node for `ConfLeap.leap_input`.
    """

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(
            conf_leap=ConfLeap.leap_input,
            child_builder=Builder_RootNode_input(),
            **kwargs,
        )
        self.note_text = (
            f"The `{ConfLeap.leap_input.name}` data is taken from the `{ConfConstGeneral.name_proto_code}` process input (not configured in files):\n"
            f"*   CLI args, environment variables, current directory, ...\n"
            f"*   combination of the above with applied defaults.\n"
            #
        )


########################################################################################################################
# `ConfLeap.leap_primer` node types.
# See: FT_19_44_42_19.effective_config.md


# noinspection PyPep8Naming
class Builder_RootNode_primer(AbstractConfLeapNodeBuilder):

    def __init__(
        self,
        state_primer_conf_file_abs_path_inited: str,
    ):
        self.state_primer_conf_file_abs_path_inited: str = state_primer_conf_file_abs_path_inited

    def visit_dict(
        self,
        dict_node: AbstractDictNode,
        **kwargs,
    ) -> None:
        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_ref_root_dir_rel_path.value,
            node_class=Node_field_ref_root_dir_rel_path,
            state_primer_conf_file_abs_path_inited=self.state_primer_conf_file_abs_path_inited,
            conf_leap=ConfLeap.leap_primer,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_global_conf_dir_rel_path.value,
            node_class=Node_field_global_conf_dir_rel_path,
            state_primer_conf_file_abs_path_inited=self.state_primer_conf_file_abs_path_inited,
            conf_leap=ConfLeap.leap_primer,
        )

        self._create_unused_dict_fields(dict_node)


# noinspection PyPep8Naming
class RootNode_primer(AbstractConfLeapRootNode):
    """
    Root node for `ConfLeap.leap_primer`.
    """

    def __init__(
        self,
        state_primer_conf_file_abs_path_inited: str,
        **kwargs,
    ):
        super().__init__(
            conf_leap=ConfLeap.leap_primer,
            child_builder=Builder_RootNode_primer(
                state_primer_conf_file_abs_path_inited=state_primer_conf_file_abs_path_inited,
            ),
            **kwargs,
        )
        self.state_primer_conf_file_abs_path_inited: str = state_primer_conf_file_abs_path_inited
        self.note_text = f"The `{ConfLeap.leap_primer.name}` data is loaded from the [{self.state_primer_conf_file_abs_path_inited}] file."


# noinspection PyPep8Naming
class Node_field_ref_root_dir_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        state_primer_conf_file_abs_path_inited: str,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.state_primer_conf_file_abs_path_inited: str = state_primer_conf_file_abs_path_inited
        self.note_text = (
            f"Field `{ConfField.field_ref_root_dir_rel_path.value}` points to the dir called `{PathName.path_ref_root.value}`.\n"
            f"The path is relative to the `{ConfConstGeneral.name_proto_code}` file [{self.state_primer_conf_file_abs_path_inited}].\n"
            f"Normally, the `{PathName.path_ref_root.value}` dir is the client repo root, but it can be anything.\n"
            f"See `{EnvState.state_ref_root_dir_abs_path_inited.name}` in `{ConfLeap.leap_derived.name}` -\n"
            f"the derived abs path is the base path for all the configured relative paths (except for this field itself, obviously).\n"
            #
        )


# noinspection PyPep8Naming
class Node_field_global_conf_dir_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        state_primer_conf_file_abs_path_inited: str,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.state_primer_conf_file_abs_path_inited: str = state_primer_conf_file_abs_path_inited
        self.note_text = (
            f"Field `{ConfField.field_global_conf_dir_rel_path.value}` points to the global config dir (as opposed to local config dir `{ConfField.field_local_conf_symlink_rel_path.value}`).\n"
            f"{ConfConstGeneral.relative_path_field_note}\n"
            f"See `{EnvState.state_global_conf_dir_abs_path_inited.name}` in `{ConfLeap.leap_derived.name}` -\n"
            f"normally, the resolved global config dir contains all other global client config files.\n"
            #
        )


########################################################################################################################
# `ConfLeap.leap_client` node types.
# See: FT_19_44_42_19.effective_config.md


# noinspection PyPep8Naming
class Builder_RootNode_client(AbstractConfLeapNodeBuilder):

    def visit_dict(
        self,
        dict_node: AbstractDictNode,
        **kwargs,
    ) -> None:

        conf_leap = ConfLeap.leap_client

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_local_conf_symlink_rel_path.value,
            node_class=Node_field_local_conf_symlink_rel_path,
            conf_leap=conf_leap,
            **kwargs,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_default_env_dir_rel_path.value,
            node_class=Node_field_default_env_dir_rel_path,
            conf_leap=conf_leap,
            **kwargs,
        )

        self._create_common_fields(
            dict_node=dict_node,
            conf_leap=conf_leap,
        )

        self._create_unused_dict_fields(dict_node)


# noinspection PyPep8Naming
class RootNode_client(AbstractConfLeapRootNode):
    """
    Root node for `ConfLeap.leap_client`.
    """

    def __init__(
        self,
        state_global_conf_file_abs_path_inited: str,
        **kwargs,
    ):
        super().__init__(
            conf_leap=ConfLeap.leap_client,
            child_builder=Builder_RootNode_client(),
            **kwargs,
        )
        self.state_global_conf_file_abs_path_inited: str = state_global_conf_file_abs_path_inited
        self.note_text = f"The `{ConfLeap.leap_client.name}` data is loaded from the [{self.state_global_conf_file_abs_path_inited}] file."


# noinspection PyPep8Naming
class Node_field_local_conf_symlink_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.note_text = (
            f"Field `{ConfField.field_local_conf_symlink_rel_path.value}` points to local config dir (as opposed to the global config dir `{ConfField.field_global_conf_dir_rel_path.value}`).\n"
            f"{ConfConstGeneral.relative_path_field_note}\n"
            f"The basename of this path is a symlink set to the actual dir with environment-specific config.\n"
            f"If the symlink does not exist yet, its target is set from:\n"
            f"*   either field `{ConfField.field_default_env_dir_rel_path.value}`,\n"
            f"*   or arg `{SyntaxArg.arg_env}` which can also be used to re-set the symlink target to a new path.\n"
            f"See `{EnvState.state_global_conf_dir_abs_path_inited.name}` in `{ConfLeap.leap_derived.name}` -\n"
            f"normally, the resolved local config dir contains all local environment-specific config files.\n"
            #
        )


# noinspection PyPep8Naming
class Node_field_default_env_dir_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.note_text = (
            f"Field `{ConfField.field_default_env_dir_rel_path.value}` is the default path where `{ConfField.field_local_conf_symlink_rel_path.value}` symlink can point to.\n"
            f"{ConfConstGeneral.relative_path_field_note}\n"
            f"The path is ignored when the `{ConfField.field_local_conf_symlink_rel_path.value}` symlink already exists.\n"
            f"Arg `{SyntaxArg.arg_env}` overrides this `{ConfField.field_default_env_dir_rel_path.value}` field.\n"
            #
        )


# noinspection PyPep8Naming
class Node_field_required_python_version(AbstractValueNode[str]):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_required_python_version.value}` selects `python` version.\n"
                f'The value specifies the version of `python` interpreter which is used to create `venv` (e.g. "{ConfConstEnv.latest_known_python_version}").\n'
                f"{ConfConstGeneral.common_field_global_note}\n"
                #
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


# noinspection PyPep8Naming
class Node_field_python_selector_file_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_python_selector_file_rel_path.value}` specifies rel path to `python` selector.\n"
                f"The selector is a standalone script written in `python` which must implement `{SelectorFunc.select_python_file_abs_path.value}` function.\n"
                f"{ConfConstGeneral.common_field_global_note}\n"
                #
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


# noinspection PyPep8Naming
class Node_field_local_venv_dir_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_local_venv_dir_rel_path.value}` points to the dir where `venv` (`python` virtual environment) is created.\n"
                f"{ConfConstGeneral.relative_path_field_note}\n"
                f"{ConfConstGeneral.common_field_global_note}\n"
                #
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


# noinspection PyPep8Naming
class Node_field_local_log_dir_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_local_log_dir_rel_path.value}` points to the dir with log files created for each script execution.\n"
                f"{ConfConstGeneral.relative_path_field_note}\n"
                f"{ConfConstGeneral.common_field_global_note}\n"
                #
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


# noinspection PyPep8Naming
class Node_field_local_tmp_dir_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_local_tmp_dir_rel_path.value}` points to the dir with temporary files created for some commands.\n"
                f"{ConfConstGeneral.relative_path_field_note}\n"
                f"{ConfConstGeneral.common_field_global_note}\n"
                #
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


# noinspection PyPep8Naming
class Node_field_local_cache_dir_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_local_cache_dir_rel_path.value}` points to the dir with cached files created for some commands.\n"
                f"{ConfConstGeneral.relative_path_field_note}\n"
                f"{ConfConstGeneral.common_field_global_note}\n"
                #
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


# noinspection PyPep8Naming
class Node_field_venv_driver(AbstractValueNode[str]):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_venv_driver.value}` selects a tool to manage packages:\n"
                f'*   specify "{VenvDriverType.venv_pip.name}" to use native `pip`,\n'
                f'*   specify "{VenvDriverType.venv_uv.name}" to use fast `uv`.\n'
                f"{ConfConstGeneral.common_field_global_note}\n"
                #
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"


# noinspection PyPep8Naming
class Builder_Node_field_project_descriptors(AbstractConfLeapNodeBuilder):

    def build_dict_node(
        self,
        node_name: str | None,
        node_indent: int,
        orig_data: dict,
        conf_leap: ConfLeap,
        **kwargs,
    ) -> "AbstractDictNode":
        return Node_project_descriptor(
            node_indent=node_indent,
            orig_data=orig_data,
            conf_leap=conf_leap,
            **kwargs,
        )


# noinspection PyPep8Naming
class Node_field_project_descriptors(AbstractListNode):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            conf_leap=conf_leap,
            child_builder=Builder_Node_field_project_descriptors(),
            **kwargs,
        )
        if conf_leap == ConfLeap.leap_client:
            self.note_text = (
                f"Field `{ConfField.field_project_descriptors.value}` lists `python` projects and their installation details.\n"
                f"{ConfConstGeneral.common_field_global_note}\n"
                # See: UC_78_58_06_54.no_stray_packages.md:
                f"Note that the `{ConfConstGeneral.name_protoprimer_package}` does not manage package dependencies itself.\n"
                f"Instead, the `{ConfConstGeneral.name_protoprimer_package}` relies on `{ConfConstClient.default_pyproject_toml_basename}` file per `python` project to specify these dependencies.\n"
                f"See `{EnvState.state_project_descriptors_inited.name}` in `{ConfLeap.leap_derived.name}`.\n"
            )
        elif conf_leap == ConfLeap.leap_env:
            self.note_text = f"{ConfConstGeneral.common_field_local_note}\n"
        elif conf_leap == ConfLeap.leap_derived:
            self.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_project_descriptors.value)}\n"


# noinspection PyPep8Naming
class Builder_Node_project_descriptor(AbstractConfLeapNodeBuilder):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        self.conf_leap: ConfLeap = conf_leap

    def visit_dict(
        self,
        dict_node: AbstractDictNode,
        **kwargs,
    ) -> None:
        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_build_root_dir_rel_path.value,
            node_class=Node_field_build_root_dir_rel_path,
            conf_leap=self.conf_leap,
            **kwargs,
        )

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=ConfField.field_install_extras.value,
            node_class=Node_field_install_extras,
            conf_leap=self.conf_leap,
            **kwargs,
        )

        self._create_unused_dict_fields(dict_node)


# noinspection PyPep8Naming
class Node_project_descriptor(AbstractDictNode):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        kwargs.pop("node_name", None)
        kwargs.pop("is_present", None)
        super().__init__(
            node_name=None,
            is_present=True,
            child_builder=Builder_Node_project_descriptor(
                conf_leap=conf_leap,
            ),
            **kwargs,
        )


# noinspection PyPep8Naming
class Node_field_build_root_dir_rel_path(AbstractValueNode[str]):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
        )
        if conf_leap in [
            ConfLeap.leap_client,
            ConfLeap.leap_derived,
        ]:
            self.note_text = (
                f"This is similar to specifying the dir of `{ConfConstClient.default_pyproject_toml_basename}` for `pip`:\n"
                f"pip install path/to/project\n"
                f"{ConfConstGeneral.relative_path_field_note}\n"
                #
            )


# noinspection PyPep8Naming
class Node_field_install_extras(AbstractListNode):

    def __init__(
        self,
        conf_leap: ConfLeap,
        **kwargs,
    ):
        super().__init__(
            child_builder=ConfigBuilderVisitor(),
            **kwargs,
        )
        if conf_leap in [
            ConfLeap.leap_client,
            ConfLeap.leap_derived,
        ]:
            self.note_text = (
                f"This is similar to specifying a list of `extra_item`-s per `path/to/project` for `pip`:\n"
                f"pip install path/to/project[extra_item_1,extra_item_2,...]\n"
                #
            )


########################################################################################################################
# `ConfLeap.leap_env` node types.
# See: FT_19_44_42_19.effective_config.md


# noinspection PyPep8Naming
class Builder_RootNode_env(AbstractConfLeapNodeBuilder):

    def visit_dict(
        self,
        dict_node: AbstractDictNode,
        **kwargs,
    ) -> None:

        self._create_common_fields(
            dict_node=dict_node,
            conf_leap=ConfLeap.leap_env,
        )

        self._create_unused_dict_fields(dict_node)


# noinspection PyPep8Naming
class RootNode_env(AbstractConfLeapRootNode):
    """
    Root node for `ConfLeap.leap_env`.
    """

    def __init__(
        self,
        state_local_conf_file_abs_path_inited: str,
        **kwargs,
    ):
        super().__init__(
            conf_leap=ConfLeap.leap_env,
            child_builder=Builder_RootNode_env(),
            **kwargs,
        )
        self.state_local_conf_file_abs_path_inited: str = state_local_conf_file_abs_path_inited
        self.note_text = f"The `{ConfLeap.leap_env.name}` data is loaded from the [{self.state_local_conf_file_abs_path_inited}] file."


########################################################################################################################
# `ConfLeap.leap_derived` node types.
# See: FT_19_44_42_19.effective_config.md


# noinspection PyPep8Naming
class Builder_RootNode_derived(AbstractConfLeapNodeBuilder):

    def visit_dict(
        self,
        dict_node: AbstractDictNode,
        **kwargs,
    ) -> None:

        conf_leap = ConfLeap.leap_derived

        field_node: AbstractConfigNode

        # ===
        # `ConfLeap.leap_input`

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_proto_code_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(EnvState.state_proto_code_file_abs_path_inited.name, ConfLeap.leap_input)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_primer_conf_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(EnvState.state_primer_conf_file_abs_path_inited.name, ConfLeap.leap_input)}\n"

        # ===
        # `ConfLeap.leap_primer`

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_ref_root_dir_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(ConfField.field_ref_root_dir_rel_path.value, ConfLeap.leap_primer)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_global_conf_dir_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(ConfField.field_global_conf_dir_rel_path.value, ConfLeap.leap_primer)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_global_conf_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = (
            # TODO: It is not derived from just this:
            #       *   dirname is from `field_global_conf_dir_rel_path`
            #       *   basename is from `state_primer_conf_file_abs_path_inited`
            f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(EnvState.state_primer_conf_file_abs_path_inited.name, ConfLeap.leap_input)}\n"
        )

        # ===
        # `ConfLeap.leap_client`

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_selected_env_dir_rel_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = (
            # TODO: Either default or --env arg:
            f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(ConfField.field_default_env_dir_rel_path.value, ConfLeap.leap_client)}\n"
        )

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_local_conf_symlink_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(ConfField.field_local_conf_symlink_rel_path.value, ConfLeap.leap_client)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_local_conf_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = (
            # TODO: It is not derived from just this:
            #       *   dirname is from `field_local_conf_symlink_rel_path`
            #       *   basename is from `state_primer_conf_file_abs_path_inited`
            f"{ConfConstGeneral.func_note_derived_based_on_conf_leap_field(EnvState.state_primer_conf_file_abs_path_inited.name, ConfLeap.leap_input)}\n"
        )

        # ===
        # `ConfLeap.leap_env`
        # nothing specific

        # ===
        # `ConfLeap.leap_derived`

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_required_python_version_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_required_python_version.value)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_python_selector_file_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_python_selector_file_rel_path.value)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_local_venv_dir_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_local_venv_dir_rel_path.value)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_local_log_dir_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_local_log_dir_rel_path.value)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_local_tmp_dir_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_local_tmp_dir_rel_path.value)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_local_cache_dir_abs_path_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_local_cache_dir_rel_path.value)}\n"

        field_node = self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_venv_driver_inited.name,
            node_class=AbstractValueNode,
            conf_leap=conf_leap,
            **kwargs,
        )
        field_node.note_text = f"{ConfConstGeneral.func_note_derived_based_on_common(ConfField.field_venv_driver.value)}\n"

        self._create_used_dict_field(
            dict_node=dict_node,
            field_name=EnvState.state_project_descriptors_inited.name,
            node_class=Node_field_project_descriptors,
            conf_leap=conf_leap,
            **kwargs,
        )

        self._create_unused_dict_fields(dict_node)


# noinspection PyPep8Naming
class RootNode_derived(AbstractConfLeapRootNode):
    """
    Root node for `ConfLeap.leap_derived`.
    """

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(
            conf_leap=ConfLeap.leap_derived,
            child_builder=Builder_RootNode_derived(),
            **kwargs,
        )
        self.note_text = (
            f"The `{ConfLeap.leap_derived.name}` data is derived from other data - it is computed by:\n"
            f"*   applying defaults to missing field values\n"
            f"*   combining with other field values\n"
            f"Effectively, this is what ultimately used by the `{ConfConstGeneral.name_protoprimer_package}`.\n"
            #
        )


class RendererState(enum.Enum):
    """
    Names for the rendered versions of the states.
    """

    state_primer_conf_file_data_loaded_rendered = enum.auto()
    state_client_conf_file_data_loaded_rendered = enum.auto()
    state_env_conf_file_data_loaded_rendered = enum.auto()
    state_derived_conf_data_loaded_rendered = enum.auto()
    state_all_conf_data_rendered = enum.auto()


####################################################################################################################


def can_render_effective_config(
    state_node,
) -> bool:
    """
    Like `can_print_effective_config` but for `ExecMode.mode_boot` and without the `StateStride` restriction.
    The rendered `Bootstrapper_*` only run when the venv module is imported (later `StateStride`).
    """
    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       With access to config, this will change from DAG to simple access of config via `custom_main`.
    state_input_exec_mode_arg_loaded: ExecMode = state_node.eval_parent_state(EnvState.state_input_exec_mode_arg_loaded.name)
    return state_input_exec_mode_arg_loaded == ExecMode.mode_boot


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_primer_conf_file_data_loaded_rendered(AbstractCachingStateNode[dict]):
    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       With access to config, this will change from DAG to simple access of config via `custom_main`.

    _parent_states = staticmethod(
        lambda: [
            EnvState.state_stride_src_updated_reached.name,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_primer_conf_file_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: RendererState.state_primer_conf_file_data_loaded_rendered.name)

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_proto_code_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_proto_code_file_abs_path_inited.name)
        state_primer_conf_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_primer_conf_file_abs_path_inited.name)

        file_data: dict
        if os.path.exists(state_primer_conf_file_abs_path_inited):
            file_data = read_json_file(state_primer_conf_file_abs_path_inited)
        else:
            # TODO: Be able to detect min scenario and avoid warning:
            warn_once_at_state_stride(
                missing_conf_file_message(state_primer_conf_file_abs_path_inited),
                self.env_ctx.get_stride(),
            )
            file_data = {}

        if can_render_effective_config(self):

            state_input_stderr_log_level_eval_finalized: int = self.eval_parent_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

            # Print `ConfLeap.leap_input` data together:
            # ===
            # `ConfLeap.leap_input`:
            conf_input = RootNode_input(
                node_indent=0,
                orig_data={
                    EnvState.state_proto_code_file_abs_path_inited.name: state_proto_code_file_abs_path_inited,
                    EnvState.state_primer_conf_file_abs_path_inited.name: state_primer_conf_file_abs_path_inited,
                },
            )
            print(RenderConfigVisitor().render_node(conf_input))

            # ===
            # `ConfLeap.leap_primer`:
            conf_primer = RootNode_primer(
                node_indent=0,
                orig_data=file_data,
                state_primer_conf_file_abs_path_inited=state_primer_conf_file_abs_path_inited,
            )
            print(RenderConfigVisitor().render_node(conf_primer))

        return file_data


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_client_conf_file_data_loaded_rendered(AbstractCachingStateNode[dict]):
    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       With access to config, this will change from DAG to simple access of config via `custom_main`.

    _parent_states = staticmethod(
        lambda: [
            RendererState.state_primer_conf_file_data_loaded_rendered.name,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_global_conf_file_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: RendererState.state_client_conf_file_data_loaded_rendered.name)

    def _eval_state_once(
        self,
    ) -> ValueType:

        state_global_conf_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_global_conf_file_abs_path_inited.name)

        file_data: dict
        if os.path.exists(state_global_conf_file_abs_path_inited):
            file_data = read_json_file(state_global_conf_file_abs_path_inited)
        else:
            # TODO: Be able to detect min scenario and avoid warning:
            warn_once_at_state_stride(
                missing_conf_file_message(state_global_conf_file_abs_path_inited),
                self.env_ctx.get_stride(),
            )
            file_data = {}

        if can_render_effective_config(self):
            state_input_stderr_log_level_eval_finalized: int = self.eval_parent_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

            conf_client = RootNode_client(
                node_indent=0,
                orig_data=file_data,
                state_global_conf_file_abs_path_inited=state_global_conf_file_abs_path_inited,
            )
            print(RenderConfigVisitor().render_node(conf_client))

        return file_data


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_env_conf_file_data_loaded_rendered(AbstractCachingStateNode[dict]):
    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       With access to config, this will change from DAG to simple access of config via `custom_main`.

    _parent_states = staticmethod(
        lambda: [
            RendererState.state_client_conf_file_data_loaded_rendered.name,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_local_conf_file_abs_path_inited.name,
        ]
    )
    _state_name = staticmethod(lambda: RendererState.state_env_conf_file_data_loaded_rendered.name)

    def _eval_state_once(
        self,
    ) -> ValueType:
        state_local_conf_file_abs_path_inited: str = self.eval_parent_state(EnvState.state_local_conf_file_abs_path_inited.name)

        file_data: dict
        if os.path.exists(state_local_conf_file_abs_path_inited):
            file_data = read_json_file(state_local_conf_file_abs_path_inited)
        else:
            # TODO: Be able to detect min scenario and avoid warning:
            # TODO: Still warn when required for some fields:
            if False:
                # noinspection PyUnreachableCode
                warn_once_at_state_stride(
                    missing_conf_file_message(state_local_conf_file_abs_path_inited),
                    self.env_ctx.get_stride(),
                )
            file_data = {}

        if can_render_effective_config(self):
            state_input_stderr_log_level_eval_finalized: int = self.eval_parent_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

            conf_env = RootNode_env(
                node_indent=0,
                orig_data=file_data,
                state_local_conf_file_abs_path_inited=state_local_conf_file_abs_path_inited,
            )
            print(RenderConfigVisitor().render_node(conf_env))

        return file_data


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_derived_conf_data_loaded_rendered(AbstractCachingStateNode[dict]):
    """
    Implements: FT_00_22_19_59.derived_config.md
    """

    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       With access to config, this will change from DAG to simple access of config via `custom_main`.

    _state_name = staticmethod(lambda: RendererState.state_derived_conf_data_loaded_rendered.name)

    def __init__(
        self,
        env_ctx: EnvContext,
    ):
        self.derived_data_env_states: list[str] = [
            # ===
            # `ConfLeap.leap_input`
            EnvState.state_proto_code_file_abs_path_inited.name,
            EnvState.state_primer_conf_file_abs_path_inited.name,
            # ===
            # `ConfLeap.leap_primer`
            EnvState.state_ref_root_dir_abs_path_inited.name,
            EnvState.state_global_conf_dir_abs_path_inited.name,
            EnvState.state_global_conf_file_abs_path_inited.name,
            # ===
            # `ConfLeap.leap_client`
            EnvState.state_selected_env_dir_rel_path_inited.name,
            EnvState.state_local_conf_symlink_abs_path_inited.name,
            EnvState.state_local_conf_file_abs_path_inited.name,
            # ===
            # `ConfLeap.leap_env`
            # nothing specific
            # ===
            # `ConfLeap.leap_derived`
            EnvState.state_required_python_version_inited.name,
            EnvState.state_selected_python_file_abs_path_inited.name,
            EnvState.state_local_venv_dir_abs_path_inited.name,
            EnvState.state_local_log_dir_abs_path_inited.name,
            EnvState.state_local_tmp_dir_abs_path_inited.name,
            EnvState.state_local_cache_dir_abs_path_inited.name,
            EnvState.state_venv_driver_inited.name,
            EnvState.state_project_descriptors_inited.name,
        ]

        # TODO: Is this needed given the list of dependencies in `derived_data_env_states`?
        parent_states = [
            RendererState.state_env_conf_file_data_loaded_rendered.name,
            EnvState.state_input_exec_mode_arg_loaded.name,
            EnvState.state_input_stderr_log_level_eval_finalized.name,
            *self.derived_data_env_states,
        ]

        # The list parent states sorted by their definition order in `EnvState` and `RendererState`:
        enum_names = [enum_item.name for enum_item in EnvState] + [enum_item.name for enum_item in RendererState]
        parent_states.sort(
            key=lambda parent_state: enum_names.index(parent_state),
        )

        self._parent_states = lambda: parent_states
        super().__init__(env_ctx=env_ctx)

    def _eval_state_once(
        self,
    ) -> ValueType:

        config_data_derived = {}
        for derived_data_env_state in self.derived_data_env_states:
            evaluated_value = self.eval_parent_state(derived_data_env_state)
            if isinstance(evaluated_value, enum.Enum):
                config_data_derived[derived_data_env_state] = evaluated_value.name
            else:
                config_data_derived[derived_data_env_state] = evaluated_value

        if can_render_effective_config(self):
            state_input_stderr_log_level_eval_finalized: int = self.eval_parent_state(EnvState.state_input_stderr_log_level_eval_finalized.name)

            conf_derived = RootNode_derived(
                node_indent=0,
                orig_data=config_data_derived,
            )
            print(RenderConfigVisitor().render_node(conf_derived))

        return config_data_derived


# noinspection PyPep8Naming
@trivial_factory
class Bootstrapper_state_all_conf_data_rendered(AbstractCachingStateNode[int]):
    # TODO: TODO_28_48_19_20.api_to_traverse_config_when_primed.md:
    #       With access to config, this will change from DAG to simple access of config via `custom_main`.

    _parent_states = staticmethod(
        lambda: [
            RendererState.state_derived_conf_data_loaded_rendered.name,
        ]
    )
    _state_name = staticmethod(lambda: RendererState.state_all_conf_data_rendered.name)

    def _eval_state_once(
        self,
    ) -> ValueType:
        return 0
