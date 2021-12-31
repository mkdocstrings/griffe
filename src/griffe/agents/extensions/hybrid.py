"""This extension provides an hybrid behavior while loading data."""

from __future__ import annotations

import ast
from typing import Any

from griffe.agents.extensions.base import InspectorExtension, VisitorExtension, When, load_extension
from griffe.agents.nodes import ObjectNode
from griffe.agents.visitor import Visitor
from griffe.exceptions import ExtensionError
from griffe.importer import dynamic_import
from griffe.logger import get_logger

logger = get_logger(__name__)


class HybridExtension(VisitorExtension):
    """Inspect during a visit.

    This extension accepts the name of another extension (an inspector)
    and runs it appropriately. It allows to inspect objects
    after having visited them, so as to extract more data.

    Indeed, during the visit, an object might be seen as a simple
    attribute (assignment), when in fact it's a function or a class
    dynamically constructed. In this case, inspecting it will
    provide the desired data.
    """

    when = When.after_all

    def __init__(self, extension: str | dict[str, Any]) -> None:
        """Initialize the extension.

        Parameters:
            extension: The name or configuration of another extension.

        Raises:
            ExtensionError: When the passed extension is not an inspector extension.
        """
        self._extension: InspectorExtension = load_extension(extension)  # type: ignore[assignment]
        if not isinstance(self._extension, InspectorExtension):
            raise ExtensionError(
                "the 'hybrid' extension only accepts inspector extensions. "
                "If you want to use a visitor extension, just add it normally "
                "to your extensions configuration, without using 'hybrid'."
            )
        super().__init__()

    def attach(self, visitor: Visitor) -> None:  # noqa: D102
        super().attach(visitor)
        self._extension.attach(visitor)  # type: ignore[arg-type]  # tolerate hybrid behavior

    def visit(self, node: ast.AST) -> None:  # noqa: D102
        try:
            just_visited = self.visitor.current[node.name]  # type: ignore[attr-defined]
        except (KeyError, AttributeError, TypeError):
            return
        if just_visited.is_alias:
            return
        try:
            value = dynamic_import(just_visited.path)
        except AttributeError:
            # can happen when an object is defined conditionally,
            # for example based on the Python version
            return
        object_node = ObjectNode(value, name=node.name)  # type: ignore[attr-defined]
        self._extension.inspect(object_node)


# make it available
Extension = HybridExtension
