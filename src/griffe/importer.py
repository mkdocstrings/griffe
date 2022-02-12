"""This module contains utilities to dynamically import objects."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from importlib import import_module
from pathlib import Path
from typing import Any, Iterator


@contextmanager
def sys_path(*paths: str | Path) -> Iterator[None]:
    """Redefine `sys.path` temporarily.

    Parameters:
        *paths: The paths to use when importing modules.
            If no paths are given, keep `sys.path` untouched.

    Yields:
        Nothing.
    """
    if not paths:
        yield
        return
    old_path = sys.path
    sys.path = [str(path) for path in paths]
    try:
        yield
    finally:
        sys.path = old_path


def dynamic_import(import_path: str, import_paths: list[Path] | None = None) -> Any:  # noqa: WPS231
    """Dynamically import the specified object.

    It can be a module, class, method, function, attribute,
    nested arbitrarily.

    Parameters:
        import_path: The path of the object to import.
        import_paths: The paths to import the object from.

    Raises:
        ModuleNotFoundError: When the object's module could not be found.
        ImportError: When there was an import error or when couldn't get the attribute.

    Returns:
        The imported object.
    """
    module_parts: list[str] = import_path.split(".")
    object_parts: list[str] = []
    errors = []

    with sys_path(*(import_paths or ())):
        while True:
            module_path = ".".join(module_parts)
            try:  # noqa: WPS503 (false-positive)
                module = import_module(module_path)
            except ModuleNotFoundError as error:
                if len(module_parts) == 1:
                    raise
                errors.append(str(error))
                object_parts.insert(0, module_parts.pop(-1))
            else:
                break

    # Sometimes extra dependencies are not installed,
    # and therefore we aren't able to import the leaf module,
    # so we end up with its parent instead, on which we can't
    # get the attribute either. In that case we re-raise an
    # ImportError for consistency.
    # See https://github.com/mkdocstrings/mkdocstrings/issues/380

    value = module
    for part in object_parts:
        try:
            value = getattr(value, part)
        except AttributeError as error:  # noqa: WPS440
            raise ImportError("\n".join(errors)) from error
    return value
