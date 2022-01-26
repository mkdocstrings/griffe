"""This module contains utilities to dynamically import objects."""

from __future__ import annotations

from importlib import import_module
from typing import Any


def dynamic_import(import_path: str) -> Any:  # noqa: WPS231
    """Dynamically import the specified object.

    It can be a module, class, method, function, attribute,
    nested arbitrarily.

    Parameters:
        import_path: The path of the object to import.

    Raises:
        ModuleNotFoundError: When the object's module could not be found.

    Returns:
        The imported object.
    """
    module_parts: list[str] = import_path.split(".")
    object_parts: list[str] = []

    while True:
        module_path = ".".join(module_parts)
        try:  # noqa: WPS503 (false-positive)
            module = import_module(module_path)
        except ModuleNotFoundError:
            if len(module_parts) == 1:
                raise
            object_parts.insert(0, module_parts.pop(-1))
        else:
            break

    value = module
    for part in object_parts:
        value = getattr(value, part)
    return value
