"""This module contains data encoders/serializers and decoders/deserializers.

The available formats are:

- JSON: see the [encoder][griffe.encoders.Encoder] and [decoder][griffe.encoders.decoder].
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from griffe.dataclasses import Class, Data, Function, Kind, Module


class Encoder(json.JSONEncoder):
    """JSON encoder.

    JSON encoders are not used directly, but through
    the [`json.dump`][] or [`json.dumps`][] methods.

    Examples:
        >>> import json
        >>> from griffe.encoders import Encoder
        >>> json.dumps(..., cls=Encoder, full=True, **kwargs)
    """

    def __init__(self, *args, full=False, **kwargs) -> None:
        """Initialize the encoder.

        Arguments:
            *args: See [`json.JSONEncoder`][].
            full: Whether to dump full data or base data.
                If you plan to reload the data in Python memory
                using the [decoder][griffe.encoders.decoder],
                you don't need the full data as it can be infered again
                using the base data. If you want to feed a non-Python
                tool instead, dump the full data.
            **kwargs: See [`json.JSONEncoder`][].
        """
        super().__init__(*args, **kwargs)
        self.full = full

    def default(self, obj: Any) -> Any:
        """Return a serializable representation of the given object.

        Arguments:
            obj: The object to serialize.

        Returns:
            A serializable representation.
        """
        if hasattr(obj, "as_dict"):
            return obj.as_dict(self.full)
        if isinstance(obj, Kind):
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
            module = Module(obj_dict["name"], obj_dict["lineno"], obj_dict["endlineno"], Path(obj_dict["filepath"]))
            for module_member in obj_dict.get("members", []):
                module[module_member.name] = module_member
            return module
        elif kind == Kind.CLASS:
            class_ = Class(obj_dict["name"], obj_dict["lineno"], obj_dict["endlineno"])
            for class_member in obj_dict.get("members", []):
                class_[class_member.name] = class_member
            return class_
        elif kind == Kind.FUNCTION:
            return Function(obj_dict["name"], obj_dict["lineno"], obj_dict["endlineno"])
        elif kind == Kind.DATA:
            return Data(obj_dict["name"], obj_dict["lineno"], obj_dict["endlineno"])
    return obj_dict
