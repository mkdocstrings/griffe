"""General helpers for tests."""

from __future__ import annotations

import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from griffe.agents.inspector import inspect
from griffe.dataclasses import Module, Object
from tests import TESTS_DIR, TMP_DIR


@contextmanager
def temporary_pyfile(code: str) -> Iterator[tuple[str, Path]]:
    """Create a module.py file containing the given code in a temporary directory.

    Parameters:
        code: The code to write to the temporary file.

    Yields:
        module_name: The module name, as to dynamically import it.
        module_path: The module path.
    """
    with tempfile.TemporaryDirectory(dir=TMP_DIR) as tmpdir:
        tmpdirpath = Path(tmpdir).relative_to(TESTS_DIR.parent)
        tmpfile = tmpdirpath / "module.py"
        tmpfile.write_text(code)
        yield ".".join(tmpdirpath.parts) + ".module", tmpfile


@contextmanager
def temporary_inspected_module(code: str) -> Iterator[Module]:
    """Create and inspect a temporary module with the given code.

    Parameters:
        code: The code of the module.

    Yields:
        The inspected module.
    """
    with temporary_pyfile(code) as (name, path):
        yield inspect(name, filepath=path)


def vtree(*objects: Object, return_leaf: bool = False) -> Object:
    """Link objects together, vertically.

    Parameters:
        *objects: A sequence of objects. The first one is at the top of the tree.
        return_leaf: Whether to return the leaf instead of the root.

    Raises:
        ValueError: When no objects are provided.

    Returns:
        The top or leaf object.
    """
    if not objects:
        raise ValueError("At least one object must be provided")
    top = objects[0]
    leaf = top
    for obj in objects[1:]:
        leaf[obj.name] = obj
        leaf = obj
    return leaf if return_leaf else top


def htree(*objects: Object) -> Object:
    """Link objects together, horizontally.

    Parameters:
        *objects: A sequence of objects. All objects starting at the second become members of the first.

    Raises:
        ValueError: When no objects are provided.

    Returns:
        The first given object, with all the other objects as members of it.
    """
    if not objects:
        raise ValueError("At least one object must be provided")
    top = objects[0]
    for obj in objects[1:]:
        top[obj.name] = obj
    return top


def module_vtree(path, leaf_package: bool = True, return_leaf: bool = False) -> Module:
    """Link objects together, vertically.

    Parameters:
        path: The complete module path, like `"a.b.c.d"`.
        leaf_package: Whether the deepest module should also be a package.
        return_leaf: Whether to return the leaf instead of the root.

    Raises:
        ValueError: When no objects are provided.

    Returns:
        The top or leaf module.
    """
    parts = path.split(".")
    modules = [Module(name, filepath=Path(*parts[:index], "__init__.py")) for index, name in enumerate(parts)]
    if not leaf_package:
        try:
            filepath = modules[-1].filepath.with_stem(parts[-1])  # type: ignore[attr-defined]
        except AttributeError:  # TODO: remove once Python 3.8 is dropped
            filepath = modules[-1].filepath.with_name(f"{parts[-1]}.py")
        modules[-1]._filepath = filepath  # noqa: WPS437
    return vtree(*modules, return_leaf=return_leaf)  # type: ignore[return-value]
