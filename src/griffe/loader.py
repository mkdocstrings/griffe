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
from contextlib import suppress
from pathlib import Path
from typing import Any, Iterator, Sequence, Tuple

from griffe.agents.extensions import Extensions
from griffe.agents.inspector import inspect
from griffe.agents.visitor import patch_ast, visit
from griffe.collections import LinesCollection, ModulesCollection
from griffe.dataclasses import Module, Object
from griffe.docstrings.parsers import Parser
from griffe.exceptions import AliasResolutionError, UnhandledPthFileError, UnimportableModuleError
from griffe.logger import get_logger

NamePartsType = Tuple[str, ...]
NamePartsAndPathType = Tuple[NamePartsType, Path]

logger = get_logger(__name__)


async def _read_async(path):
    async with aopen(path) as fd:
        return await fd.read()


async def _read_sync(path):
    return path.read_text()


try:
    from aiofiles import open as aopen
except ModuleNotFoundError:
    logger.warning("aiofiles is not installed, fallback to blocking read")
    read_async = _read_sync
else:
    read_async = _read_async


_builtin_modules: set[str] = set(sys.builtin_module_names)


class _BaseGriffeLoader:
    def __init__(
        self,
        extensions: Extensions | None = None,
        docstring_parser: Parser | None = None,
        docstring_options: dict[str, Any] | None = None,
        lines_collection: LinesCollection | None = None,
        modules_collection: ModulesCollection | None = None,
    ) -> None:
        """Initialize the loader.

        Parameters:
            extensions: The extensions to use.
            docstring_parser: The docstring parser to use. By default, no parsing is done.
            docstring_options: Additional docstring parsing options.
            lines_collection: A collection of source code lines.
            modules_collection: A collection of modules.
        """
        self.extensions: Extensions = extensions or Extensions()
        self.docstring_parser: Parser | None = docstring_parser
        self.docstring_options: dict[str, Any] = docstring_options or {}
        self.lines_collection: LinesCollection = lines_collection or LinesCollection()
        self.modules_collection: ModulesCollection = modules_collection or ModulesCollection()
        patch_ast()

    def _create_module(self, module_name: str, module_path: Path) -> Module:
        return Module(
            module_name,
            filepath=module_path,
            lines_collection=self.lines_collection,
            modules_collection=self.modules_collection,
        )

    def _visit_module(self, code: str, module_name: str, module_path: Path, parent: Module | None = None) -> Module:
        self.lines_collection[module_path] = code.splitlines(keepends=False)
        return visit(
            module_name,
            filepath=module_path,
            code=code,
            extensions=self.extensions,
            parent=parent,
            docstring_parser=self.docstring_parser,
            docstring_options=self.docstring_options,
            lines_collection=self.lines_collection,
            modules_collection=self.modules_collection,
        )

    def _inspect_module(self, module_name: str, filepath: Path | None = None, parent: Module | None = None) -> Module:
        return inspect(
            module_name,
            filepath=filepath,
            extensions=self.extensions,
            parent=parent,
            docstring_parser=self.docstring_parser,
            docstring_options=self.docstring_options,
            lines_collection=self.lines_collection,
        )

    def _member_parent(self, module: Module, subparts: NamePartsType, subpath: Path) -> Module:
        parent_parts = subparts[:-1]
        try:
            return module[parent_parts]
        except KeyError:
            if module.is_namespace_package or module.is_namespace_subpackage:
                member_parent = Module(
                    subparts[0],
                    filepath=subpath.parent,
                    lines_collection=self.lines_collection,
                    modules_collection=self.modules_collection,
                )
                module[parent_parts] = member_parent
                return member_parent
        raise UnimportableModuleError(f"{subpath} is not importable")


class GriffeLoader(_BaseGriffeLoader):
    """The Griffe loader, allowing to load data from modules."""

    def load_module(
        self,
        module: str | Path,
        submodules: bool = True,
        search_paths: Sequence[str | Path] | None = None,
    ) -> Module:
        """Load a module.

        Parameters:
            module: The module name or path.
            submodules: Whether to recurse on the submodules.
            search_paths: The paths to search into.

        Returns:
            A module.
        """
        if module in _builtin_modules:
            module_name = module
            top_module = self._inspect_module(module)  # type: ignore[arg-type]
        else:
            module_name, top_module_name, top_module_path = _top_name_and_path(module, search_paths)
            top_module = self._load_module_path(top_module_name, top_module_path, submodules=submodules)
        self.modules_collection[top_module.path] = top_module
        return self.modules_collection[module_name]  # type: ignore[index]

    def follow_aliases(self, obj: Object, only_exported: bool = True) -> bool:  # noqa: WPS231
        """Follow aliases: try to recursively resolve all found aliases.

        Parameters:
            obj: The object and its members to recurse on.
            only_exported: Only try to resolve an alias if it is explicitely exported.

        Returns:
            True if everything was resolved, False otherwise.
        """
        success = True
        for member in obj.members.values():
            if member.is_alias:
                if only_exported and not obj.member_is_exported(member, explicitely=True):
                    continue
                try:
                    member.resolve_target()  # type: ignore[union-attr]  # we know it's an alias
                except AliasResolutionError as error:
                    success = False
                    package = error.target_path.split(".", 1)[0]
                    if obj.package.path != package and package not in self.modules_collection:
                        with suppress(ModuleNotFoundError):
                            self.load_module(package)
            else:
                success &= self.follow_aliases(member)  # type: ignore[arg-type]  # we know it's an object
        return success

    def _load_module_path(
        self,
        module_name: str,
        module_path: Path,
        submodules: bool = True,
        parent: Module | None = None,
    ) -> Module:
        logger.debug(f"Loading path {module_path}")
        try:
            code = module_path.read_text()
        except OSError:
            module = self._create_module(module_name, module_path)
        else:
            module = self._visit_module(code, module_name, module_path, parent)
        if submodules:
            self._load_submodules(module)
        return module

    def _load_submodules(self, module: Module) -> None:
        for subparts, subpath in sorted(iter_submodules(module.filepath), key=_module_depth):
            self._load_submodule(module, subparts, subpath)

    def _load_submodule(self, module: Module, subparts: NamePartsType, subpath: Path) -> None:
        try:
            member_parent = self._member_parent(module, subparts, subpath)
        except UnimportableModuleError as error:
            logger.warning(f"{error}. Missing __init__ module?")
        else:
            member_parent[subparts[-1]] = self._load_module_path(
                subparts[-1], subpath, submodules=False, parent=member_parent
            )


class AsyncGriffeLoader(_BaseGriffeLoader):
    """The asynchronous Griffe loader, allowing to load data from modules."""

    async def load_module(
        self,
        module: str | Path,
        submodules: bool = True,
        search_paths: Sequence[str | Path] | None = None,
    ) -> Module:
        """Load a module.

        Parameters:
            module: The module name or path.
            submodules: Whether to recurse on the submodules.
            search_paths: The paths to search into.

        Returns:
            A module.
        """
        module_name, top_module_name, top_module_path = _top_name_and_path(module, search_paths)
        top_module = await self._load_module_path(top_module_name, top_module_path, submodules=submodules)
        self.modules_collection[top_module.path] = top_module
        return self.modules_collection[module_name]

    async def follow_aliases(self, obj: Object, only_exported: bool = True) -> bool:  # noqa: WPS231
        """Follow aliases: try to recursively resolve all found aliases.

        Parameters:
            obj: The object and its members to recurse on.
            only_exported: Only try to resolve an alias if it is explicitely exported.

        Returns:
            True if everything was resolved, False otherwise.
        """
        success = True
        for member in obj.members.values():
            if member.is_alias:
                if only_exported and not obj.member_is_exported(member, explicitely=True):
                    continue
                try:
                    member.resolve_target()  # type: ignore[union-attr]  # we know it's an alias
                except AliasResolutionError as error:
                    success = False
                    package = error.target_path.split(".", 1)[0]
                    if obj.package.path != package and package not in self.modules_collection:
                        with suppress(ModuleNotFoundError):
                            await self.load_module(package)
            else:
                success &= await self.follow_aliases(member)  # type: ignore[arg-type]  # we know it's an object
        return success

    async def _load_module_path(
        self,
        module_name: str,
        module_path: Path,
        submodules: bool = True,
        parent: Module | None = None,
    ) -> Module:
        logger.debug(f"Loading path {module_path}")
        try:
            code = await read_async(module_path)
        except OSError:
            module = self._create_module(module_name, module_path)
        else:
            module = self._visit_module(code, module_name, module_path, parent)
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
        try:
            member_parent = self._member_parent(module, subparts, subpath)
        except UnimportableModuleError as error:
            logger.debug(str(error))
        else:
            member_parent[subparts[-1]] = await self._load_module_path(
                subparts[-1], subpath, submodules=False, parent=member_parent
            )


def _top_name_and_path(
    module: str | Path,
    search_paths: Sequence[str | Path] | None = None,
) -> tuple[str, str, Path]:
    module_name, module_path = find_module_or_path(module, search_paths)
    module_parts = module_name.split(".")
    top_module_name = module_parts[0]
    top_module_path = module_path
    for _ in range(len(module_parts) - 1):
        top_module_path = top_module_path.parent
    return module_name, top_module_name, top_module_path


def find_module_or_path(
    module: str | Path,
    search_paths: Sequence[str | Path] | None = None,
) -> tuple[str, Path]:
    """Find the name and path of a module.

    If a Path is passed, only try to find the module as a file path.
    If a string is passed, first try to find the module as a file path,
    then look into the search paths.

    Parameters:
        module: The module name or path.
        search_paths: The paths to search into.

    Raises:
        FileNotFoundError: When a Path was passed and the module could not be found:

            - the directory has no `__init__.py` file in it
            - the path does not exist

        ModuleNotFoundError: When a string was passed and the module could not be found:

            - no `module/__init__.py`
            - no `module.py`
            - no `module.pth`
            - no `module` directory (namespace packages)
            - or unsupported .pth file

    Returns:
        The name of the module (or package) and its path.
    """
    if isinstance(module, Path):
        # programatically passed a Path, try only that
        module_name, module_path = _module_name_path(module)
    else:
        # passed a string (from CLI or Python code), try both
        try:
            module_name, module_path = _module_name_path(Path(module))
        except FileNotFoundError:
            module_name = module
            module_path = find_module(module_name, search_paths=search_paths)
    return module_name, module_path


def _module_name_path(path: Path) -> tuple[str, Path]:
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
def find_module(module_name: str, search_paths: Sequence[str | Path] | None = None) -> Path:  # noqa: WPS231
    """Find a module in a given list of paths or in `sys.path`.

    Parameters:
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

    # always search a .pth file first using the first part
    for path in search:
        top_pth = Path(f"{parts[0]}.pth")
        abs_top_pth = path / top_pth
        if abs_top_pth.exists():
            with suppress(UnhandledPthFileError):
                location = _handle_pth_file(abs_top_pth)
                if location.suffix == ".py":
                    location = location.parent
                search = [location.parent]
                # TODO: possible optimization
                # always break if exists?
                break

    # resume regular search
    filepaths = [
        Path(*parts, "__init__.py"),
        Path(*parts[:-1], f"{parts[-1]}.py"),
        Path(*parts[:-1], f"{parts[-1]}.pth"),
        Path(*parts),  # namespace packages, try last
    ]

    for path in search:  # noqa: WPS440
        for choice in filepaths:
            abs_path = path / choice
            # optimization: just check if the file exists,
            # not if it's an actual file
            if abs_path.exists():
                if abs_path.name.endswith(".pth"):
                    try:
                        return _handle_pth_file(abs_path)
                    except UnhandledPthFileError as error:
                        raise ModuleNotFoundError(module_name) from error
                return abs_path

    raise ModuleNotFoundError(module_name)


def _handle_pth_file(path):
    # support for .pth files pointing to a directory
    instructions = path.read_text().strip("\n").split(";")

    filepaths = [
        Path(instructions[0], path.stem, "__init__.py"),
        Path(instructions[0], path.stem),  # namespace packages, try last
    ]

    for choice in filepaths:
        if choice.exists():
            return choice

    # support for .pth files written by PDM, using editables
    module_name = path.stem
    if instructions[0] == f"import _{module_name}":
        editables_lines = path.with_name(f"_{module_name}.py").read_text().splitlines(keepends=False)
        # example line: F.map_module('griffe', '/media/data/dev/griffe/src/griffe/__init__.py')
        # TODO: write something more robust
        new_path = Path(editables_lines[-1].split("'")[3])
        if new_path.exists():
            return new_path

    raise UnhandledPthFileError(path)


def iter_submodules(path: Path) -> Iterator[NamePartsAndPathType]:  # noqa: WPS234
    """Iterate on a module's submodules, if any.

    Parameters:
        path: The module path.

    Yields:
        name_parts: The parts of a submodule name.
        filepath: A submodule filepath.
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


def _module_depth(name_parts_and_path: NamePartsAndPathType) -> int:
    return len(name_parts_and_path[0])
