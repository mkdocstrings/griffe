"""This module contains the code allowing to find module and load their data.

This is the entrypoint to use griffe programatically:

```python
from griffe.loader import GriffeLoader

griffe = GriffeLoader()
fastapi = griffe.load_module("fastapi")
```
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

from griffe.collections import lines_collection
from griffe.dataclasses import Module
from griffe.extensions import Extensions
from griffe.logger import get_logger
from griffe.visitor import visit

logger = get_logger(__name__)


class GriffeLoader:
    """The griffe loader, allowing to load data from modules.

    Attributes:
        extensions: The extensions to use.
    """

    def __init__(self, extensions: Extensions | None = None) -> None:
        """Initialize the loader.

        Arguments:
            extensions: The extensions to use.
        """
        self.extensions = extensions or Extensions()

    def load_module(
        self,
        module: str | Path,
        recursive: bool = True,
        search_paths: list[str | Path] | None = None,
    ) -> Module:
        """Load a module.

        Arguments:
            module: The module name or path.
            recursive: Whether to recurse on the submodules.
            search_paths: The paths to search into.

        Returns:
            A module.
        """
        if isinstance(module, Path):
            # programatically passed a Path, try only that
            module_name, module_path = module_name_path(module)
        else:
            # passed a string (from CLI or Python code), try both
            try:
                module_name, module_path = module_name_path(Path(module))
            except FileNotFoundError:
                module_name = module
                module_path = find_module(module_name, search_paths=search_paths)
        return self._load_module_path(module_name, module_path, recursive=recursive)

    def _load_module_path(self, module_name, module_path, recursive=True):
        logger.debug(f"Loading path {module_path}")
        code = module_path.read_text()
        lines_collection[module_path] = code.splitlines(keepends=False)
        module = visit(
            module_name,
            filepath=module_path,
            code=code,
            extensions=self.extensions,
        )
        if recursive:
            for subparts, subpath in sorted(iter_submodules(module_path), key=_module_depth):
                parent_parts = subparts[:-1]
                try:
                    member_parent = module[parent_parts]
                except KeyError:
                    logger.debug(f"Skipping (not importable) {subpath}")
                    continue
                member_parent[subparts[-1]] = self._load_module_path(subparts[-1], subpath, recursive=False)
        return module


def _module_depth(name_parts_and_path):
    return len(name_parts_and_path[0])


def module_name_path(path: Path) -> tuple[str, Path]:
    """Get the module name and path from a path.

    Arguments:
        path: A directory or file path. Paths to `__init__.py` files
            will be resolved to their parent directory.

    Raises:
        FileNotFoundError: When:

            - the directory has no `__init__.py` file in it
            - the path does not exist

    Returns:
        The name of the module (or package) and its path.
    """
    if path.is_dir():
        module_path = path / "__init__.py"
        if module_path.exists():
            return path.name, module_path
        raise FileNotFoundError
    if path.exists():
        if path.stem == "__init__":
            return path.parent.resolve().name, path
        return path.stem, path
    raise FileNotFoundError


# credits to @NiklasRosenstein and the docspec project
def find_module(module_name: str, search_paths: list[str | Path] | None = None) -> Path:
    """Find a module in a given list of paths or in `sys.path`.

    Arguments:
        module_name: The module name.
        search_paths: The paths to search into.

    Raises:
        ModuleNotFoundError: When the module cannot be found.

    Returns:
        The module file path.
    """
    # optimization: pre-compute Paths to relieve CPU when joining paths
    search = [path if isinstance(path, Path) else Path(path) for path in search_paths or sys.path]
    parts = module_name.split(".")

    filenames = [
        Path(*parts, "__init__.py"),
        Path(*parts[:-1], f"{parts[-1]}.py"),
    ]

    for path in search:
        for choice in filenames:
            abs_path = path / choice
            # optimization: just check if the file exists,
            # not if it's an actual file
            if abs_path.exists():
                return abs_path

    raise ModuleNotFoundError(module_name)


def iter_submodules(path) -> Iterator[tuple[list[str], Path]]:  # noqa: WPS234
    """Iterate on a module's submodules, if any.

    Arguments:
        path: The module path.

    Yields:
        This generator yields tuples containing the parts
        of the submodule name as well as its filepath.
    """
    if path.name == "__init__.py":
        path = path.parent
    # optimization: just check if the file name ends with .py
    # (to distinguish it from a directory),
    # not if it's an actual file
    elif path.suffix == ".py":
        return

    for subpath in path.rglob("*.py"):
        rel_subpath = subpath.relative_to(path)
        if rel_subpath.name == "__init__.py":
            # optimization: since it's a relative path,
            # if it has only one part and is named __init__.py,
            # it means it's the starting path
            # (no need to compare it against starting path)
            if len(rel_subpath.parts) == 1:
                continue
            yield rel_subpath.parts[:-1], subpath
        else:
            yield rel_subpath.with_suffix("").parts, subpath
