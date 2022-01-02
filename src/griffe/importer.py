"""This module contains utilities to dynamically import objects."""

from typing import Any


def dynamic_import(import_path: str) -> Any:
    """Dynamically import the specified object.

    It can be a module, class, method, function, attribute,
    nested arbitrarily.

    Parameters:
        import_path: The path of the object to import.

    Raises:
        ImportError: When there was an error during import.

    Returns:
        The imported object.
    """
    try:
        module = __import__(import_path, level=0)
    except Exception as error:
        raise ImportError(f"Error while importing '{import_path}': {error}") from error
    attr_parts = import_path.split(".")[1:]
    value = module
    for part in attr_parts:
        value = getattr(value, part)
    return value
