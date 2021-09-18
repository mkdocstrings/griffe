"""This module contains the code allowing to find module and load their data.

This is the entrypoint to use griffe programatically:

```python
from griffe.loader import GriffeLoader

griffe = GriffeLoader()
fastapi = griffe.load_module("fastapi")
```
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Iterator, Tuple

from griffe.collections import lines_collection
from griffe.dataclasses import Module
from griffe.extensions import Extensions
from griffe.logger import get_logger
from griffe.visitor import visit

NamePartsType = Tuple[str, ...]
NamePartsAndPathType = Tuple[NamePartsType, Path]

logger = get_logger(__name__)


async def _read_async(path):
    async with aopen(path) as fd:
        return await fd.read()


async def _fallback_read_async(path):
    logger.warning("aiofiles is not installed, fallback to blocking read")
    return path.read_text()


try:
    from aiofiles import open as aopen  # type: ignore
except ModuleNotFoundError:
    read_async = _fallback_read_async
else:
    read_async = _read_async


class _BaseGriffeLoader:
    def __init__(self, extensions: Extensions | None = None) -> None:
        """Initialize the loader.

        Arguments:
            extensions: The extensions to use.
        """
        self.extensions = extensions or Extensions()

    def _module_name_and_path(
        self,
        module: str | Path,
        search_paths: list[str | Path] | None = None,
    ) -> tuple[str, Path]:
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
        return module_name, module_path


class GriffeLoader(_BaseGriffeLoader):
    """The Griffe loader, allowing to load data from modules.

    Attributes:
        extensions: The extensions to use.
    """

    def load_module(
        self,
        module: str | Path,
        submodules: bool = True,
        search_paths: list[str | Path] | None = None,
    ) -> Module:
        """Load a module.

        Arguments:
            module: The module name or path.
            submodules: Whether to recurse on the submodules.
            search_paths: The paths to search into.

        Returns:
            A module.
        """
        module_name, module_path = self._module_name_and_path(module, search_paths)
        return self._load_module_path(module_name, module_path, submodules=submodules)

    def _load_module_path(self, module_name: str, module_path: Path, submodules: bool = True) -> Module:
        logger.debug(f"Loading path {module_path}")
        code = module_path.read_text()
        lines_collection[module_path] = code.splitlines(keepends=False)
        module = visit(
            module_name,
            filepath=module_path,
            code=code,
            extensions=self.extensions,
        )
        if submodules:
            self._load_submodules(module)
        return module

    def _load_submodules(self, module: Module) -> None:
        for subparts, subpath in sorted(iter_submodules(module.filepath), key=_module_depth):
            self._load_submodule(module, subparts, subpath)

    def _load_submodule(self, module: Module, subparts: NamePartsType, subpath: Path) -> None:
        parent_parts = subparts[:-1]
        try:
            member_parent = module[parent_parts]
        except KeyError:
            logger.debug(f"Skipping (not importable) {subpath}")
        else:
            member_parent[subparts[-1]] = self._load_module_path(subparts[-1], subpath, submodules=False)


class AsyncGriffeLoader(_BaseGriffeLoader):
    """The asynchronous Griffe loader, allowing to load data from modules.

    Attributes:
        extensions: The extensions to use.
    """

    async def load_module(
        self,
        module: str | Path,
        submodules: bool = True,
        search_paths: list[str | Path] | None = None,
    ) -> Module:
        """Load a module.

        Arguments:
            module: The module name or path.
            submodules: Whether to recurse on the submodules.
            search_paths: The paths to search into.

        Returns:
            A module.
        """
        module_name, module_path = self._module_name_and_path(module, search_paths)
        return await self._load_module_path(module_name, module_path, submodules=submodules)

    async def _load_module_path(self, module_name: str, module_path: Path, submodules: bool = True) -> Module:
        logger.debug(f"Loading path {module_path}")
        code = await read_async(module_path)
        lines_collection[module_path] = code.splitlines(keepends=False)
        module = visit(
            module_name,
            filepath=module_path,
            code=code,
            extensions=self.extensions,
        )
        if submodules:
            await self._load_submodules(module)
        return module

    async def _load_submodules(self, module: Module) -> None:
        await asyncio.gather(
            *[
                self._load_submodule(module, subparts, subpath)
                for subparts, subpath in sorted(iter_submodules(module.filepath), key=_module_depth)
            ]
        )

    async def _load_submodule(self, module: Module, subparts: NamePartsType, subpath: Path) -> None:
        parent_parts = subparts[:-1]
        try:
            member_parent = module[parent_parts]
        except KeyError:
            logger.debug(f"Skipping (not importable) {subpath}")
        else:
            member_parent[subparts[-1]] = await self._load_module_path(subparts[-1], subpath, submodules=False)


def _module_depth(name_parts_and_path: NamePartsAndPathType) -> int:
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
            if path.parent.is_absolute():
                return path.parent.name, path
            return path.parent.resolve().name, path
        return path.stem, path
    raise FileNotFoundError


# credits to @NiklasRosenstein and the docspec project
# TODO: possible optimization by caching elements of search directories
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


def iter_submodules(path: Path) -> Iterator[NamePartsAndPathType]:  # noqa: WPS234
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
