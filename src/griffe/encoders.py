"""This module contains data encoders/serializers and decoders/deserializers.

The available formats are:

- JSON: see the [encoder][griffe.encoders.Encoder] and [decoder][griffe.encoders.decoder].
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any

from griffe.dataclasses import Class, Data, Function, Kind, Module, ParameterKind
from griffe.docstrings.parsers import Parser


class Encoder(json.JSONEncoder):
    """JSON encoder.

    JSON encoders are not used directly, but through
    the [`json.dump`][] or [`json.dumps`][] methods.

    Examples:
        >>> import json
        >>> from griffe.encoders import Encoder
        >>> json.dumps(..., cls=Encoder, full=True, **kwargs)
    """

    def __init__(
        self,
        *args,
        full: bool = False,
        docstring_parser: Parser = Parser.google,
        docstring_options: dict[str, Any] = None,
        **kwargs
    ) -> None:
        """Initialize the encoder.

        Arguments:
            *args: See [`json.JSONEncoder`][].
            full: Whether to dump full data or base data.
                If you plan to reload the data in Python memory
                using the [decoder][griffe.encoders.decoder],
                you don't need the full data as it can be infered again
                using the base data. If you want to feed a non-Python
                tool instead, dump the full data.
            docstring_parser: The docstring parser to use.
            docstring_options: Additional docstring parsing options.
            **kwargs: See [`json.JSONEncoder`][].
        """
        super().__init__(*args, **kwargs)
        self.full: bool = full
        self.docstring_parser: Parser = docstring_parser
        self.docstring_options: dict[str, Any] = docstring_options or {}

    def default(self, obj: Any) -> Any:  # noqa: WPS212
        """Return a serializable representation of the given object.

        Arguments:
            obj: The object to serialize.

        Returns:
            A serializable representation.
        """
        if hasattr(obj, "as_dict"):
            return obj.as_dict(full=self.full, docstring_parser=self.docstring_parser, **self.docstring_options)
        if isinstance(obj, (Path, ParameterKind)):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


def decoder(obj_dict) -> Module | Class | Function | Data:  # noqa: WPS231
    """Decode dictionaries as data classes.

    The [`json.loads`] method walks the tree from bottom to top.

    Arguments:
        obj_dict: The dictionary to decode.

    Returns:
        An instance of a data class.
    """
    if "kind" in obj_dict:
        kind = Kind(obj_dict["kind"])
        if kind == Kind.MODULE:
            module = Module(name=obj_dict["name"], filepath=Path(obj_dict["filepath"]))
            for module_member in obj_dict.get("members", []):
                module[module_member.name] = module_member
            return module
        elif kind == Kind.CLASS:
            class_ = Class(name=obj_dict["name"], lineno=obj_dict["lineno"], endlineno=obj_dict["endlineno"])
            for class_member in obj_dict.get("members", []):
                class_[class_member.name] = class_member
            return class_
        elif kind == Kind.FUNCTION:
            return Function(name=obj_dict["name"], lineno=obj_dict["lineno"], endlineno=obj_dict["endlineno"])
        elif kind == Kind.DATA:
            return Data(name=obj_dict["name"], lineno=obj_dict["lineno"], endlineno=obj_dict["endlineno"])
    return obj_dict
