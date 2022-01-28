"""This module defines introspection mechanisms.

Sometimes we cannot get the source code of a module or an object,
typically built-in modules like `itertools`. The only way to know
what they are made of is to actually import them and inspect their contents.

Sometimes, even if the source code is available, loading the object is desired
because it was created or modified dynamically, and our node visitor is not
powerful enough to infer all these dynamic modifications. In this case,
we always try to visit the code first, and only then we load the object
to update the data with introspection.

This module exposes a public function, [`inspect()`][griffe.agents.inspector.inspect],
which inspects the module using [`inspect.getmembers()`][inspect.getmembers],
and returns a new [`Module`][griffe.dataclasses.Module] instance,
populating its members recursively, by using a [`NodeVisitor`][ast.NodeVisitor]-like class.

The inspection agent works similarly to the regular "node visitor" agent,
in that it maintains a state with the current object being handled,
and recursively handle its members.
"""

from __future__ import annotations

import ast
import sys
from inspect import Parameter as SignatureParameter
from inspect import Signature, getdoc, getmodule, ismodule
from inspect import signature as getsignature
from pathlib import Path
from tokenize import TokenError
from typing import Any

from griffe.agents.base import BaseInspector
from griffe.agents.extensions import Extensions
from griffe.agents.nodes import ObjectKind, ObjectNode, get_annotation
from griffe.collections import LinesCollection
from griffe.dataclasses import (
    Alias,
    Attribute,
    Class,
    Docstring,
    Function,
    Module,
    Parameter,
    ParameterKind,
    Parameters,
)
from griffe.docstrings.parsers import Parser
from griffe.expressions import Expression, Name
from griffe.importer import dynamic_import

empty = Signature.empty


def inspect(
    module_name: str,
    *,
    filepath: Path | None = None,
    import_paths: list[Path] | None = None,
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
) -> Module:
    """Inspect a module.

    Parameters:
        module_name: The module name (as when importing [from] it).
        filepath: The module file path.
        import_paths: Paths to import the module from.
        extensions: The extensions to use when inspecting the module.
        parent: The optional parent of this module.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Additional docstring parsing options.
        lines_collection: A collection of source code lines.

    Returns:
        The module, with its members populated.
    """
    if not import_paths and filepath:
        import_paths = [filepath.parent]
    return Inspector(
        module_name,
        filepath,
        extensions or Extensions(),
        parent,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        lines_collection=lines_collection,
    ).get_module(import_paths)


_compiled_modules = {*sys.builtin_module_names, "_socket", "_struct"}


def _should_create_alias(parent: ObjectNode, child: ObjectNode, current_module_path: str) -> str | None:
    # the whole point of the following logic is to deal with these cases:
    # - parent object has a module member
    # - if this module is not a submodule of the parent, alias it
    # - but break special cycles coming from builtin modules
    #   like ast -> _ast -> ast (here we inspect _ast)
    #   or os -> posix/nt -> os (here we inspect posix/nt)

    child_module = getmodule(child.obj)

    if not child_module:
        return None

    if ismodule(parent.obj):
        # TODO: is this necessary to check if the parent is a module?
        # what happens for modules imported in class definitions?
        parent_module = parent.obj
        parent_module_name = parent_module.__name__
        child_module_name = child_module.__name__
        # special cases: inspect.getmodule does not return the real modules
        # for those, but rather the "user-facing" ones - we prevent that
        # and use the real parent module
        # TODO: if the list grows, it should probably be moved
        # in a separate function (also I don't like having to deal
        # with third-party libraries here directly...)
        trust_inspect = not (
            parent_module_name in {"posix", "nt"}
            and child_module_name == "os"
            or parent_module_name == "numpy.core._multiarray_umath"
            and child_module_name == "numpy.core.multiarray"
        )
        if not trust_inspect:
            child_module = parent_module

    child_module_path = child_module.__name__
    parent_name = parent.name

    is_submodule = child_module_path == current_module_path or child_module_path.startswith(current_module_path + ".")
    is_public_version_of_private_builtin_module = (
        parent_name.startswith("_") and parent_name[1:] == child_module_path and parent_name in _compiled_modules
    )
    if not is_public_version_of_private_builtin_module and not is_submodule:
        return child_module_path

    return None


class Inspector(BaseInspector):  # noqa: WPS338
    """This class is used to instantiate an inspector.

    Inspectors iterate on objects members to extract data from them.
    """

    def __init__(
        self,
        module_name: str,
        filepath: Path | None,
        extensions: Extensions,
        parent: Module | None = None,
        docstring_parser: Parser | None = None,
        docstring_options: dict[str, Any] | None = None,
        lines_collection: LinesCollection | None = None,
    ) -> None:
        """Initialize the inspector.

        Parameters:
            module_name: The module name.
            filepath: The optional filepath.
            extensions: Extensions to use when inspecting.
            parent: The module parent.
            docstring_parser: The docstring parser to use.
            docstring_options: The docstring parsing options.
            lines_collection: A collection of source code lines.
        """
        super().__init__()
        self.module_name: str = module_name
        self.filepath: Path | None = filepath
        self.extensions: Extensions = extensions.attach_inspector(self)
        self.parent: Module | None = parent
        self.current: Module | Class = None  # type: ignore[assignment]
        self.docstring_parser: Parser | None = docstring_parser
        self.docstring_options: dict[str, Any] = docstring_options or {}
        self.lines_collection: LinesCollection = lines_collection or LinesCollection()

    def _get_docstring(self, node: ObjectNode) -> Docstring | None:
        value = getdoc(node.obj)
        if value is None:
            return None
        return Docstring(
            value,
            parser=self.docstring_parser,
            parser_options=self.docstring_options,
        )

    def get_module(self, import_paths: list[Path] | None = None) -> Module:
        """Build and return the object representing the module attached to this inspector.

        This method triggers a complete inspection of the module members.

        Parameters:
            import_paths: Paths replacing `sys.path` to import the module.

        Returns:
            A module instance.
        """
        import_path = self.module_name
        if self.parent is not None:
            import_path = f"{self.parent.path}.{import_path}"
        value = dynamic_import(import_path, import_paths)
        top_node = ObjectNode(value, self.module_name)
        self.inspect(top_node)
        return self.current.module

    def inspect(self, node: ObjectNode) -> None:
        """Extend the base inspection with extensions.

        Parameters:
            node: The node to inspect.
        """
        for before_inspector in self.extensions.before_inspection:
            before_inspector.inspect(node)
        super().inspect(node)
        for after_inspector in self.extensions.after_inspection:
            after_inspector.inspect(node)

    def generic_inspect(self, node: ObjectNode) -> None:  # noqa: WPS231
        """Extend the base generic inspection with extensions.

        Parameters:
            node: The node to inspect.
        """
        for before_inspector in self.extensions.before_children_inspection:
            before_inspector.inspect(node)

        for child in node.children:
            child_module_path = _should_create_alias(node, child, self.current.module.path)
            if child_module_path:
                child_name = getattr(child.obj, "__name__", child.name)
                target_path = f"{child_module_path}.{child_name}"
                self.current[child.name] = Alias(child.name, target_path)
            else:
                self.inspect(child)

        for after_inspector in self.extensions.after_children_inspection:
            after_inspector.inspect(node)

    def inspect_module(self, node: ObjectNode) -> None:
        """Inspect a module.

        Parameters:
            node: The node to inspect.
        """
        self.current = Module(
            name=self.module_name,
            filepath=self.filepath,
            parent=self.parent,
            docstring=self._get_docstring(node),
            lines_collection=self.lines_collection,
        )
        self.generic_inspect(node)

    def inspect_class(self, node: ObjectNode) -> None:
        """Inspect a class.

        Parameters:
            node: The node to inspect.
        """
        bases = [base.__name__ for base in node.obj.__bases__ if base is not object]  # noqa: WPS609

        class_ = Class(
            name=node.name,
            docstring=self._get_docstring(node),
            bases=bases,
        )
        self.current[node.name] = class_
        self.current = class_
        self.generic_inspect(node)
        self.current = self.current.parent  # type: ignore[assignment]

    def inspect_staticmethod(self, node: ObjectNode) -> None:
        """Inspect a static method.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"classmethod"})

    def inspect_classmethod(self, node: ObjectNode) -> None:
        """Inspect a class method.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"staticmethod"})

    def inspect_method_descriptor(self, node: ObjectNode) -> None:
        """Inspect a method descriptor.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"method descriptor"})

    def inspect_builtin_method(self, node: ObjectNode) -> None:
        """Inspect a builtin method.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"builtin"})

    def inspect_method(self, node: ObjectNode) -> None:
        """Inspect a method.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node)

    def inspect_coroutine(self, node: ObjectNode) -> None:
        """Inspect a coroutine.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"async"})

    def inspect_builtin_function(self, node: ObjectNode) -> None:
        """Inspect a builtin function.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"builtin"})

    def inspect_function(self, node: ObjectNode) -> None:
        """Inspect a function.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node)

    def inspect_cached_property(self, node: ObjectNode) -> None:
        """Inspect a cached property.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"cached property"})

    def inspect_property(self, node: ObjectNode) -> None:
        """Inspect a property.

        Parameters:
            node: The node to inspect.
        """
        self.handle_function(node, {"property"})

    def handle_function(self, node: ObjectNode, labels: set | None = None):  # noqa: WPS231
        """Handle a function.

        Parameters:
            node: The node to inspect.
            labels: Labels to add to the data object.
        """
        try:
            signature = getsignature(node.obj)
        except (AttributeError, ValueError, TokenError, TypeError):
            parameters = None
            returns = None
        else:
            parameters = Parameters(
                *[_convert_parameter(parameter, parent=self.current) for parameter in signature.parameters.values()]
            )
            return_annotation = signature.return_annotation
            if return_annotation is empty:
                returns = None
            else:
                returns = _convert_object_to_annotation(return_annotation, parent=self.current)

        function = Function(
            name=node.name,
            parameters=parameters,
            returns=returns,
            docstring=self._get_docstring(node),
        )
        if labels:
            function.labels |= labels
        self.current[node.name] = function

    def inspect_attribute(self, node: ObjectNode) -> None:
        """Inspect an attribute.

        Parameters:
            node: The node to inspect.
        """
        self.handle_attribute(node)

    def handle_attribute(self, node: ObjectNode, annotation: str | Name | Expression | None = None):  # noqa: WPS231
        """Handle an attribute.

        Parameters:
            node: The node to inspect.
            annotation: A potentiel annotation.
        """
        # TODO: to improve
        parent = self.current
        labels: set[str] = set()

        if parent.kind is ObjectKind.MODULE:
            labels.add("module")
        elif parent.kind is ObjectKind.CLASS:
            labels.add("class")
        elif parent.kind is ObjectKind.FUNCTION:
            if parent.name != "__init__":
                return
            parent = parent.parent
            labels.add("instance")

        try:
            value = repr(node.obj)
        except Exception:  # could trigger anything
            value = None
        docstring = self._get_docstring(node)

        attribute = Attribute(
            name=node.name,
            value=value,
            annotation=annotation,
            # lineno=node.lineno,
            # endlineno=node.end_lineno,
            docstring=docstring,
        )
        attribute.labels |= labels
        parent[node.name] = attribute

        if node.name == "__all__":
            parent.exports = set(node.obj)


_kind_map = {
    SignatureParameter.POSITIONAL_ONLY: ParameterKind.positional_only,
    SignatureParameter.POSITIONAL_OR_KEYWORD: ParameterKind.positional_or_keyword,
    SignatureParameter.VAR_POSITIONAL: ParameterKind.var_positional,
    SignatureParameter.KEYWORD_ONLY: ParameterKind.keyword_only,
    SignatureParameter.VAR_KEYWORD: ParameterKind.var_keyword,
}


def _convert_parameter(parameter, parent):
    name = parameter.name
    if parameter.annotation is empty:
        annotation = None
    else:
        annotation = _convert_object_to_annotation(parameter.annotation, parent=parent)
    kind = _kind_map[parameter.kind]
    if parameter.default is empty:
        default = None
    else:
        default = repr(parameter.default)
    return Parameter(name, annotation=annotation, kind=kind, default=default)


def _convert_object_to_annotation(obj, parent):
    # even when *we* import future annotations,
    # the object from which we get a signature
    # can come from modules which did *not* import them,
    # so inspect.signature returns actual Python objects
    # that we must deal with
    if not isinstance(obj, str):
        if hasattr(obj, "__name__"):
            # simple types like int, str, custom classes, etc.
            obj = obj.__name__
        else:
            # other, more complex types: hope for the best
            obj = repr(obj)
    try:
        annotation_node = compile(obj, mode="eval", filename="<>", flags=ast.PyCF_ONLY_AST, optimize=2)
    except SyntaxError:
        return obj
    return get_annotation(annotation_node.body, parent=parent)
