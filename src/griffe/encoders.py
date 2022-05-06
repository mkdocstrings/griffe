"""This module contains data encoders/serializers and decoders/deserializers.

The available formats are:

- `JSON`: see the [`JSONEncoder`][griffe.encoders.JSONEncoder] and [`json_decoder`][griffe.encoders.json_decoder].
"""

from __future__ import annotations

import json
from pathlib import Path, PosixPath, WindowsPath
from typing import Any, Callable, Type

from griffe.dataclasses import (
    Alias,
    Attribute,
    Class,
    Decorator,
    Docstring,
    Function,
    Kind,
    Module,
    Object,
    Parameter,
    ParameterKind,
    Parameters,
)
from griffe.docstrings.dataclasses import DocstringSectionKind
from griffe.docstrings.parsers import Parser
from griffe.expressions import Expression, Name


def _enum_value(obj):
    return obj.value


_json_encoder_map: dict[Type, Callable[[Any], Any]] = {
    Path: str,
    PosixPath: str,
    WindowsPath: str,
    ParameterKind: _enum_value,
    Kind: _enum_value,
    DocstringSectionKind: _enum_value,
    set: sorted,
}


class JSONEncoder(json.JSONEncoder):
    """JSON encoder.

    JSON encoders can be used directly, or through
    the [`json.dump`][] or [`json.dumps`][] methods.

    Examples:
        >>> from griffe.encoders import JSONEncoder
        >>> JSONEncoder(full=True).encode(..., **kwargs)

        >>> import json
        >>> from griffe.encoders import JSONEncoder
        >>> json.dumps(..., cls=JSONEncoder, full=True, **kwargs)
    """

    def __init__(
        self,
        *args: Any,
        full: bool = False,
        docstring_parser: Parser | None = None,
        docstring_options: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the encoder.

        Parameters:
            *args: See [`json.JSONEncoder`][].
            full: Whether to dump full data or base data.
                If you plan to reload the data in Python memory
                using the [`json_decoder`][griffe.encoders.json_decoder],
                you don't need the full data as it can be infered again
                using the base data. If you want to feed a non-Python
                tool instead, dump the full data.
            docstring_parser: The docstring parser to use. By default, no parsing is done.
            docstring_options: Additional docstring parsing options.
            **kwargs: See [`json.JSONEncoder`][].
        """
        super().__init__(*args, **kwargs)
        self.full: bool = full
        self.docstring_parser: Parser | None = docstring_parser
        self.docstring_options: dict[str, Any] = docstring_options or {}

    def default(self, obj: Any) -> Any:  # noqa: WPS212
        """Return a serializable representation of the given object.

        Parameters:
            obj: The object to serialize.

        Returns:
            A serializable representation.
        """
        try:
            return obj.as_dict(full=self.full, docstring_parser=self.docstring_parser, **self.docstring_options)
        except AttributeError:
            return _json_encoder_map.get(type(obj), super().default)(obj)


def _load_docstring(obj_dict):
    if "docstring" in obj_dict:
        return Docstring(**obj_dict["docstring"])
    return None


def _load_decorators(obj_dict):
    return [Decorator(**dec) for dec in obj_dict.get("decorators", [])]


_annotation_loader_map = {
    str: lambda _: _,
    dict: lambda dct: Name(dct["source"], dct["full"]),
    list: lambda lst: Expression(*[_load_annotation(_) for _ in lst]),
}


def _load_annotation(annotation: str | dict | list) -> str | Name | Expression:
    if annotation is None:
        return None
    return _annotation_loader_map[type(annotation)](annotation)


def _load_parameter(obj_dict: dict[str, Any]) -> Parameter:
    return Parameter(
        obj_dict["name"],
        annotation=_load_annotation(obj_dict["annotation"]),
        kind=ParameterKind(obj_dict["kind"]),
        default=obj_dict["default"],
    )


def _load_module(obj_dict: dict[str, Any]) -> Module:
    module = Module(name=obj_dict["name"], filepath=Path(obj_dict["filepath"]), docstring=_load_docstring(obj_dict))
    for module_member in obj_dict.get("members", []):
        module[module_member.name] = module_member
    module.labels |= set(obj_dict.get("labels", ()))
    return module


def _load_class(obj_dict: dict[str, Any]) -> Class:
    class_ = Class(
        name=obj_dict["name"],
        lineno=obj_dict["lineno"],
        endlineno=obj_dict.get("endlineno", None),
        docstring=_load_docstring(obj_dict),
        decorators=_load_decorators(obj_dict),
        bases=[_load_annotation(_) for _ in obj_dict["bases"]],
    )
    for class_member in obj_dict.get("members", []):
        class_[class_member.name] = class_member
    class_.labels |= set(obj_dict.get("labels", ()))
    return class_


def _load_function(obj_dict: dict[str, Any]) -> Function:
    function = Function(
        name=obj_dict["name"],
        parameters=Parameters(*obj_dict["parameters"]),
        returns=_load_annotation(obj_dict["returns"]),
        decorators=_load_decorators(obj_dict),
        lineno=obj_dict["lineno"],
        endlineno=obj_dict.get("endlineno", None),
        docstring=_load_docstring(obj_dict),
    )
    function.labels |= set(obj_dict.get("labels", ()))
    return function


def _load_attribute(obj_dict: dict[str, Any]) -> Attribute:
    attribute = Attribute(
        name=obj_dict["name"],
        lineno=obj_dict["lineno"],
        endlineno=obj_dict.get("endlineno", None),
        docstring=_load_docstring(obj_dict),
        value=obj_dict.get("value", None),
        annotation=_load_annotation(obj_dict.get("annotation", None)),
    )
    attribute.labels |= set(obj_dict.get("labels", ()))
    return attribute


def _load_alias(obj_dict: dict[str, Any]) -> Alias:
    return Alias(
        name=obj_dict["name"],
        target=obj_dict["target_path"],
        lineno=obj_dict["lineno"],
        endlineno=obj_dict.get("endlineno", None),
    )


_loader_map: dict[Kind, Callable[[dict[str, Any]], Module | Class | Function | Attribute | Alias]] = {  # noqa: WPS234
    Kind.MODULE: _load_module,
    Kind.CLASS: _load_class,
    Kind.FUNCTION: _load_function,
    Kind.ATTRIBUTE: _load_attribute,
    Kind.ALIAS: _load_alias,
}


def json_decoder(obj_dict: dict[str, Any]) -> dict[str, Any] | Object | Alias | Parameter:  # noqa: WPS231
    """Decode dictionaries as data classes.

    The [`json.loads`][] method walks the tree from bottom to top.

    Examples:
        >>> import json
        >>> from griffe.encoders import json_decoder
        >>> json.loads(..., object_hook=json_decoder)

    Parameters:
        obj_dict: The dictionary to decode.

    Returns:
        An instance of a data class.
    """
    if "kind" in obj_dict:
        try:
            kind = Kind(obj_dict["kind"])
        except ValueError:
            return _load_parameter(obj_dict)
        return _loader_map[kind](obj_dict)
    return obj_dict
