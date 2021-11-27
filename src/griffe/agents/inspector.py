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

from inspect import Parameter as SignatureParameter
from inspect import Signature, getdoc
from inspect import signature as getsignature
from pathlib import Path
from typing import Any

from griffe.agents.base import BaseInspector
from griffe.agents.extensions import Extensions
from griffe.agents.nodes import ObjectKind, ObjectNode, get_annotation
from griffe.collections import LinesCollection
from griffe.dataclasses import Attribute, Class, Docstring, Function, Module, Parameter, ParameterKind, Parameters
from griffe.docstrings.parsers import Parser
from griffe.expressions import Expression, Name

empty = Signature.empty


def inspect(
    module_name: str,
    *,
    filepath: Path | None = None,
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
        extensions: The extensions to use when inspecting the module.
        parent: The optional parent of this module.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Additional docstring parsing options.
        lines_collection: A collection of source code lines.

    Returns:
        The module, with its members populated.
    """
    return Inspector(
        module_name,
        filepath,
        extensions or Extensions(),
        parent,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        lines_collection=lines_collection,
    ).get_module()


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

    def get_module(self) -> Module:
        """Build and return the object representing the module attached to this inspector.

        This method triggers a complete inspection of the module members.

        Returns:
            A module instance.
        """
        top_node = ObjectNode(__import__(self.module_name), self.module_name)
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
        super().generic_inspect(node)
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
        except ValueError:
            parameters = None
            returns = None
        else:
            parameters = Parameters(*[_convert_parameter(parameter) for parameter in signature.parameters.values()])
            return_annotation = signature.return_annotation
            if return_annotation is empty:
                returns = None
            else:
                returns = return_annotation and get_annotation(return_annotation, parent=self.current)

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
        # TODO
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

        value = repr(node.obj)
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


def _convert_parameter(parameter):
    name = parameter.name
    if parameter.annotation is empty:
        annotation = None
    else:
        annotation = parameter.annotation
    kind = _kind_map[parameter.kind]
    if parameter.default is empty:
        default = None
    else:
        default = parameter.default
    return Parameter(name, annotation=annotation, kind=kind, default=default)
