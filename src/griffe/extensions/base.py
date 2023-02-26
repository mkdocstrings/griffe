"""This module contains the base classes for dealing with extensions."""

from __future__ import annotations

import enum
import os
import sys
from collections import defaultdict
from importlib.util import module_from_spec, spec_from_file_location
from inspect import isclass
from typing import TYPE_CHECKING, Any, Sequence, Union

from griffe.agents.base import BaseInspector, BaseVisitor
from griffe.exceptions import ExtensionNotLoadedError
from griffe.importer import dynamic_import

if TYPE_CHECKING:
    import ast
    from types import ModuleType

    from griffe.agents.inspector import Inspector
    from griffe.agents.nodes import ObjectNode
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

    when: When = When.after_all

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

    def visit(self, node: ast.AST) -> None:
        """Visit a node.

        Parameters:
            node: The node to visit.
        """
        getattr(self, f"visit_{node.kind}", lambda _: None)(node)  # type: ignore[attr-defined]


class InspectorExtension(BaseInspector):
    """The object inspector extension base class, to inherit from."""

    when: When = When.after_all

    def __init__(self) -> None:
        """Initialize the inspector extension."""
        super().__init__()
        self.inspector: Inspector = None  # type: ignore[assignment]

    def attach(self, inspector: Inspector) -> None:
        """Attach the parent inspector to this extension.

        Parameters:
            inspector: The parent inspector.
        """
        self.inspector = inspector

    def inspect(self, node: ObjectNode) -> None:
        """Inspect a node.

        Parameters:
            node: The node to inspect.
        """
        getattr(self, f"inspect_{node.kind}", lambda _: None)(node)


Extension = Union[VisitorExtension, InspectorExtension]


class Extensions:
    """This class helps iterating on extensions that should run at different times."""

    def __init__(self, *extensions: Extension) -> None:
        """Initialize the extensions container.

        Parameters:
            *extensions: The extensions to add.
        """
        self._visitors: dict[When, list[VisitorExtension]] = defaultdict(list)
        self._inspectors: dict[When, list[InspectorExtension]] = defaultdict(list)
        self.add(*extensions)

    def add(self, *extensions: Extension) -> None:
        """Add extensions to this container.

        Parameters:
            *extensions: The extensions to add.
        """
        for extension in extensions:
            if isinstance(extension, VisitorExtension):
                self._visitors[extension.when].append(extension)
            else:
                self._inspectors[extension.when].append(extension)

    def attach_visitor(self, parent_visitor: Visitor) -> Extensions:
        """Attach a parent visitor to the visitor extensions.

        Parameters:
            parent_visitor: The parent visitor, leading the visit.

        Returns:
            Self, conveniently.
        """
        for when in self._visitors:
            for visitor in self._visitors[when]:
                visitor.attach(parent_visitor)
        return self

    def attach_inspector(self, parent_inspector: Inspector) -> Extensions:
        """Attach a parent inspector to the inspector extensions.

        Parameters:
            parent_inspector: The parent inspector, leading the inspection.

        Returns:
            Self, conveniently.
        """
        for when in self._inspectors:
            for inspector in self._inspectors[when]:
                inspector.attach(parent_inspector)
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

    @property
    def before_inspection(self) -> list[InspectorExtension]:
        """Return the inspectors that run before the inspection.

        Returns:
            Inspectors.
        """
        return self._inspectors[When.before_all]

    @property
    def before_children_inspection(self) -> list[InspectorExtension]:
        """Return the inspectors that run before the children inspection.

        Returns:
            Inspectors.
        """
        return self._inspectors[When.before_children]

    @property
    def after_children_inspection(self) -> list[InspectorExtension]:
        """Return the inspectors that run after the children inspection.

        Returns:
            Inspectors.
        """
        return self._inspectors[When.after_children]

    @property
    def after_inspection(self) -> list[InspectorExtension]:
        """Return the inspectors that run after the inspection.

        Returns:
            Inspectors.
        """
        return self._inspectors[When.after_all]


builtin_extensions: set[str] = {
    "hybrid",
}


def _load_extension_path(path: str) -> ModuleType:
    module_name = os.path.basename(path).rsplit(".", 1)[0]
    spec = spec_from_file_location(module_name, path)
    if not spec:
        raise ExtensionNotLoadedError(f"Could not import module from path '{path}'")
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def load_extension(extension: str | dict[str, Any] | Extension | type[Extension]) -> Extension:
    """Load a configured extension.

    Parameters:
        extension: An extension, with potential configuration options.

    Raises:
        ExtensionNotLoadedError: When the extension cannot be loaded,
            either because the module is not found, or because it does not expose
            the Extension attribute. ImportError will bubble up so users can see
            the traceback.

    Returns:
        An extension instance.
    """
    ext_object = None

    if isinstance(extension, (VisitorExtension, InspectorExtension)):
        return extension

    if isclass(extension) and issubclass(extension, (VisitorExtension, InspectorExtension)):  # type: ignore[arg-type]
        return extension()  # type: ignore[operator]

    if isinstance(extension, dict):
        import_path, options = next(iter(extension.items()))

    else:  # we consider it's a string
        import_path = str(extension)
        options = {}

    if import_path in builtin_extensions:
        import_path = f"griffe.extensions.{import_path}"
    elif os.path.exists(import_path):
        try:
            ext_object = _load_extension_path(import_path)
        except ImportError as error:
            raise ExtensionNotLoadedError(f"Extension module '{import_path}' could not be found") from error

    if not ext_object:
        try:
            ext_object = dynamic_import(import_path)
        except ModuleNotFoundError as error:
            raise ExtensionNotLoadedError(f"Extension module '{import_path}' could not be found") from error
        except ImportError as error:
            raise ExtensionNotLoadedError(f"Error while importing extension '{import_path}': {error}") from error

    if isclass(ext_object) and issubclass(ext_object, (VisitorExtension, InspectorExtension)):
        return ext_object(**options)  # type: ignore[misc]

    try:
        return ext_object.Extension(**options)  # type: ignore[union-attr]
    except AttributeError as error:
        raise ExtensionNotLoadedError(f"Extension module '{import_path}' has no 'Extension' attribute") from error


def load_extensions(exts: Sequence[str | dict[str, Any] | Extension | type[Extension]]) -> Extensions:
    """Load configured extensions.

    Parameters:
        exts: A sequence of extension, with potential configuration options.

    Returns:
        An extensions container.
    """
    extensions = Extensions()
    for extension in exts:
        extensions.add(load_extension(extension))
    return extensions
