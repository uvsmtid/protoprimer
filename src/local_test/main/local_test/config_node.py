from __future__ import annotations

from protoprimer.primer_kernel import (
    AbstractConfigNode,
    AbstractRootNode,
    ConfigBuilderVisitor,
)


class RequiredAnnotationBuilderVisitor(ConfigBuilderVisitor):
    """
    Builds a config node (recursively) and annotates each node.
    """

    def build_config_node(
        self,
        **kwargs,
    ) -> AbstractConfigNode:
        config_node: AbstractConfigNode = super().build_config_node(
            **kwargs,
        )
        self._annotate_node(config_node)
        return config_node

    def build_root_node(
        self,
        **kwargs,
    ) -> AbstractRootNode:
        root_node: AbstractRootNode = super().build_root_node(
            **kwargs,
        )
        self._annotate_node(root_node)
        return root_node

    @staticmethod
    def _annotate_node(
        config_node: AbstractConfigNode,
    ) -> None:
        # Set annotation only if the annotation is not set:
        if not config_node.note_text:
            config_node.note_text = f"some help for [{config_node.__class__.__name__}]"


def build_root_node(
    node_name: str,
    # expect `dict` as the root node:
    orig_data: dict,
) -> AbstractRootNode:
    return RequiredAnnotationBuilderVisitor().build_root_node(
        node_name=node_name,
        node_indent=0,
        orig_data=orig_data,
    )
