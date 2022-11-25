"""General helpers for tests."""

from __future__ import annotations

import sys
import tempfile
from collections import namedtuple
from contextlib import contextmanager
from importlib import invalidate_caches
from pathlib import Path
from textwrap import dedent
from typing import Iterator

from griffe.agents.inspector import inspect
from griffe.agents.visitor import visit
from griffe.dataclasses import Module, Object

TMPDIR_PREFIX = "griffe_"


@contextmanager
def temporary_pyfile(code: str) -> Iterator[tuple[str, Path]]:
    """Create a module.py file containing the given code in a temporary directory.

    Parameters:
        code: The code to write to the temporary file.

    Yields:
        module_name: The module name, as to dynamically import it.
        module_path: The module path.
    """
    with tempfile.TemporaryDirectory(prefix=TMPDIR_PREFIX) as tmpdir:
        tmpfile = Path(tmpdir) / "module.py"
        tmpfile.write_text(dedent(code))
        yield "module", tmpfile


TmpPackage = namedtuple("TmpPackage", "tmpdir name path")


@contextmanager
def temporary_pypackage(package: str, modules: list[str] | None = None, init: bool = True) -> Iterator[TmpPackage]:
    """Create a module.py file containing the given code in a temporary directory.

    Parameters:
        package: The package name. Example: `"a"` gives
            a package named `a`, while `"a/b"` gives a namespace package
            named `a` with a package inside named `b`.
            If `init` is false, then `b` is also a namespace package.
        modules: Additional modules to create in the package,
            like '["b.py", "c/d.py", "e/f"]`.
        init: Whether to create an `__init__` module in the leaf package.

    Yields:
        tmp_dir: The temporary directory containing the package.
        package_name: The package name, as to dynamically import it.
        package_path: The package path.
    """
    modules = modules or []
    mkdir_kwargs = {"parents": True, "exist_ok": True}
    with tempfile.TemporaryDirectory(prefix=TMPDIR_PREFIX) as tmpdir:
        tmpdirpath = Path(tmpdir)
        package_name = ".".join(Path(package).parts)
        package_path = tmpdirpath / package
        package_path.mkdir(**mkdir_kwargs)
        if init:
            package_path.joinpath("__init__.py").touch()
        for module in modules:
            current_path = package_path
            for part in Path(module).parts:
                if part.endswith(".py") or part.endswith(".pyi"):
                    current_path.joinpath(part).touch()
                else:
                    current_path /= part
                    current_path.mkdir(**mkdir_kwargs)
                    current_path.joinpath("__init__.py").touch()
        yield TmpPackage(tmpdirpath, package_name, package_path)


@contextmanager
def temporary_visited_module(code: str) -> Iterator[Module]:
    """Create and visit a temporary module with the given code.

    Parameters:
        code: The code of the module.

    Yields:
        The visited module.
    """
    yield visit("module", filepath=Path("/fake/module.py"), code=dedent(code))


@contextmanager
def temporary_inspected_module(code: str) -> Iterator[Module]:
    """Create and inspect a temporary module with the given code.

    Parameters:
        code: The code of the module.

    Yields:
        The inspected module.
    """
    with temporary_pyfile(code) as (name, path):
        try:
            yield inspect(name, filepath=path)
        finally:
            del sys.modules["module"]  # noqa: WPS420
            invalidate_caches()


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
            filepath = modules[-1].filepath.with_stem(parts[-1])  # type: ignore[attr-defined,union-attr]
        except AttributeError:  # TODO: remove once Python 3.8 is dropped
            filepath = modules[-1].filepath.with_name(f"{parts[-1]}.py")  # type: ignore[union-attr]
        modules[-1]._filepath = filepath  # noqa: WPS437
    return vtree(*modules, return_leaf=return_leaf)  # type: ignore[return-value]
