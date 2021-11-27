"""This module contains the base classes for dealing with extensions."""

from __future__ import annotations

import enum
from collections import defaultdict
from inspect import isclass
from types import ModuleType
from typing import TYPE_CHECKING, Any, Sequence, Type, Union

from griffe.agents.base import BaseVisitor

if TYPE_CHECKING:
    from griffe.agents.visitor import Visitor
class When(enum.Enum):
    """This enumeration contains the different times at which an extension is used.

    Attributes:
        before_all: For each node, before the visit/inspection.
        before_children: For each node, after the visit has started, and before the children visit/inspection.
        after_children: For each node, after the children have been visited/inspected, and before finishing the visit/inspection.
        after_all: For each node, after the visit/inspection.
    """

    before_all: int = 1
    before_children: int = 2
    after_children: int = 3
    after_all: int = 4


class VisitorExtension(BaseVisitor):
    """The node visitor extension base class, to inherit from."""

    when: When

    def __init__(self) -> None:
        """Initialize the visitor extension."""
        super().__init__()
        self.visitor: Visitor = None  # type: ignore[assignment]

    def attach(self, visitor: Visitor) -> None:
        """Attach the parent visitor to this extension.

        Parameters:
            visitor: The parent visitor.
        """
        self.visitor = visitor


Extension = Union[VisitorExtension]


class Extensions:
    """This class helps iterating on extensions that should run at different times."""

    def __init__(self, *extensions: Extension) -> None:
        """Initialize the extensions container.

        Parameters:
            *extensions: The extensions to add.
        """
        self._visitors: dict[When, list[VisitorExtension]] = defaultdict(list)
        self.add(*extensions)

    def add(self, *extensions: Extension) -> None:
        """Add extensions to this container.

        Parameters:
            *extensions: The extensions to add.
        """
        for extension in extensions:
            if isinstance(extension, VisitorExtension):
                self._visitors[extension.when].append(extension)

    def attach_visitor(self, parent_visitor: Visitor) -> Extensions:
        """Attach a parent visitor to the visitor extensions.

        Parameters:
            parent_visitor: The parent visitor, leading the visit.

        Returns:
            Self, conveniently.
        """
        for when in self._visitors.keys():
            for visitor in self._visitors[when]:
                visitor.attach(parent_visitor)
        return self

    @property
    def before_visit(self) -> list[VisitorExtension]:
        """Return the visitors that run before the visit.

        Returns:
            Visitors.
        """
        return self._visitors[When.before_all]

    @property
    def before_children_visit(self) -> list[VisitorExtension]:
        """Return the visitors that run before the children visit.

        Returns:
            Visitors.
        """
        return self._visitors[When.before_children]

    @property
    def after_children_visit(self) -> list[VisitorExtension]:
        """Return the visitors that run after the children visit.

        Returns:
            Visitors.
        """
        return self._visitors[When.after_children]

    @property
    def after_visit(self) -> list[VisitorExtension]:
        """Return the visitors that run after the visit.

        Returns:
            Visitors.
        """
        return self._visitors[When.after_all]

builtin_extensions: dict[str, ModuleType] = {}


def load_extensions(exts: Sequence[str | dict[str, Any] | Extension | Type[Extension]]) -> Extensions:  # noqa: WPS231
    """Load configured extensions.

    Parameters:
        exts: A sequence of extension, with potential configuration options.

    Returns:
        An extensions container.
    """
    extensions = Extensions()

    for extension in exts:
        if isinstance(extension, (str, dict)):
            if isinstance(extension, str):
                if extension in builtin_extensions:
                    ext_module = builtin_extensions[extension]
                else:
                    ext_module = __import__(extension)
                options = {}
            elif isinstance(extension, dict):
                import_path = next(extension.keys())  # type: ignore[arg-type,call-overload]
                if import_path in builtin_extensions:
                    ext_module = builtin_extensions[import_path]
                else:
                    ext_module = __import__(import_path)
                options = next(extension.values())  # type: ignore[arg-type,call-overload]

            # TODO: handle AttributeError
            extensions.add(ext_module.Extension(**options))  # type: ignore[attr-defined]

        elif isinstance(extension, (VisitorExtension,)):
            extensions.add(extension)

        elif isclass(extension) and issubclass(extension, (VisitorExtension,)):
            extensions.add(extension())

    return extensions
