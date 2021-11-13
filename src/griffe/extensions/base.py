"""This module contains the base classes for dealing with extensions."""

from __future__ import annotations

import ast
import enum
from types import ModuleType
from typing import TYPE_CHECKING, Any, Sequence, Type

if TYPE_CHECKING:
    from griffe.visitor import _MainVisitor as MainVisitor  # noqa: WPS450


class When(enum.Enum):
    """This enumeration contains the different times at which an extension is used.

    Attributes:
        visit_starts: For each node, before starting the visit.
        children_visit_starts: For each node, after the visit has started, and before starting to visit children.
        children_visit_stops: For each node, after the children have been visited, and before finishing the visit.
        visit_stops: For each node, after finishing the visit.
    """

    visit_starts: int = 1
    children_visit_starts: int = 2
    children_visit_stops: int = 3
    visit_stops: int = 4


class _BaseVisitor:
    def visit(self, node: ast.AST, parent: ast.AST | None = None) -> None:
        self._visit(node, parent=parent)

    def generic_visit(self, node: ast.AST) -> None:  # noqa: WPS231
        # optimization: got rid of the two generators iter_fields and iter_child_nodes
        for field_name in node._fields:  # noqa: WPS437
            try:
                field = getattr(node, field_name)
            except AttributeError:
                continue
            if isinstance(field, ast.AST):
                self.visit(field, parent=node)
            elif isinstance(field, list):
                for child in field:
                    if isinstance(child, ast.AST):
                        self.visit(child, parent=node)

    def _run_specific_or_generic(self, node):
        # optimization: no extra variable, f-string instead of concatenation
        getattr(self, f"visit_{node.__class__.__name__}", self.generic_visit)(node)

    def _visit(self, node: ast.AST, parent: ast.AST | None = None) -> None:
        return self._run_specific_or_generic(node)


class Extension(_BaseVisitor):
    """The node visitor extension base class, to inherit from."""

    when: When

    def __init__(self, main_visitor: MainVisitor) -> None:
        """Initialize the visitor extension.

        Parameters:
            main_visitor: The main visitor.
        """
        super().__init__()
        self.visitor = main_visitor


class Extensions:
    """This class helps iterating on extensions that should run at different times."""

    def __init__(self, *extensions_classes: Type[Extension]) -> None:
        """Initialize the extensions container.

        Parameters:
            *extensions_classes: The extensions to add.
        """
        self._classes: list[Type[Extension]] = list(extensions_classes)
        self._instances: dict[When, list[Extension]] = {}

    @property
    def when_visit_starts(self) -> list[Extension]:
        """Return the visitors that run when the visit starts.

        Returns:
            Visitors.
        """
        return self._instances[When.visit_starts]

    @property
    def when_children_visit_starts(self) -> list[Extension]:
        """Return the visitors that run when the children visit starts.

        Returns:
            Visitors.
        """
        return self._instances[When.children_visit_starts]

    @property
    def when_children_visit_stops(self) -> list[Extension]:
        """Return the visitors that run when the children visit stops.

        Returns:
            Visitors.
        """
        return self._instances[When.children_visit_stops]

    @property
    def when_visit_stops(self) -> list[Extension]:
        """Return the visitors that run when the visit stops.

        Returns:
            Visitors.
        """
        return self._instances[When.visit_stops]

    def when(self, when: When) -> list[Extension]:
        """Return the visitors that run at the given time.

        Parameters:
            when: The selected time.

        Returns:
            Visitors.
        """
        return self._instances[when]

    def add(self, *extensions_classes: Type[Extension]) -> None:
        """Add visitor extensions to this container.

        Parameters:
            *extensions_classes: The extensions to add.
        """
        self._classes.extend(extensions_classes)

    def instantiate(self, main_visitor: MainVisitor) -> Extensions:
        """Clear and instantiate the visitor classes.

        Parameters:
            main_visitor: The main visitor, leading the visit.

        Returns:
            Self, conveniently.
        """
        # clear instances
        for when in When:
            self._instances[when] = []
        # create instances
        for visitor_class in self._classes:
            self._instances[visitor_class.when].append(visitor_class(main_visitor))
        return self


builtin_extensions: dict[str, ModuleType] = {}


def load_extensions(exts: Sequence[str | dict[str, Any] | Type[Extension]]) -> Extensions:  # noqa: WPS231
    """Load configured extensions.

    Parameters:
        exts: A sequence of extension, with potential configuration options.

    Returns:
        An extensions container.
    """
    extensions = Extensions()

    for extension_item in exts:
        if issubclass(extension_item, Extension):  # type: ignore
            extensions.add(extension_item)  # type: ignore
            continue

        if isinstance(extension_item, str):
            if extension_item in builtin_extensions:
                ext_module = builtin_extensions[extension_item]
            else:
                ext_module = __import__(extension_item)
            options = {}
        elif isinstance(extension_item, dict):
            import_path = next(extension_item.keys())  # type: ignore
            if import_path in builtin_extensions:
                ext_module = builtin_extensions[import_path]
            else:
                ext_module = __import__(import_path)
            options = next(extension_item.values())  # type: ignore

        # TODO: handle AttributeError
        extension = ext_module.get_extension(**options)  # type: ignore
        extensions.add(extension)

    return extensions
