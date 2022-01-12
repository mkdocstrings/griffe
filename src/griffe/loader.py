"""This module contains the code allowing to find module and load their data.

This is the entrypoint to use griffe programatically:

```python
from griffe.loader import GriffeLoader

griffe = GriffeLoader()
fastapi = griffe.load_module("fastapi")
```
"""

from __future__ import annotations

import os
import sys
from contextlib import suppress
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator, Sequence, Tuple

from griffe.agents.extensions import Extensions
from griffe.agents.inspector import inspect
from griffe.agents.visitor import patch_ast, visit
from griffe.collections import LinesCollection, ModulesCollection
from griffe.dataclasses import Alias, Kind, Module, Object
from griffe.docstrings.parsers import Parser
from griffe.exceptions import AliasResolutionError, CyclicAliasError, UnhandledPthFileError, UnimportableModuleError
from griffe.logger import get_logger
from griffe.stats import stats

NamePartsType = Tuple[str, ...]
NamePartsAndPathType = Tuple[NamePartsType, Path]

logger = get_logger(__name__)

_accepted_py_module_extensions = [".py", ".pyc", ".pyo", ".pyd", ".so"]
_extensions_set = set(_accepted_py_module_extensions)
_ignored_modules = {"debugpy", "_pydev"}

# TODO: namespace packages can span multiple locations! we must support it.
# ideally: find all locations, sort them, then reverse-merge their file lists
# (sure about sorting? yes: https://github.com/python/cpython/blob/3.10/Lib/pkgutil.py#L155,
# and we could say "but it's locale-dependent!", but it's not an issue since our process
# will use the same locale anyway, so the behavior will be as expected)
# when iterating on multiple locations, if one has an __init__ module,
# just return this one, as it takes precedence as a regular package


@lru_cache(maxsize=1)
def _get_async_reader():
    try:  # noqa: WPS503 (false-positive)
        from aiofiles import open as aopen
    except ModuleNotFoundError:
        logger.warning("aiofiles is not installed, fallback to blocking read")

        async def _read_async(path):  # noqa: WPS430
            return path.read_text()

    else:

        async def _read_async(path):  # noqa: WPS430,WPS440
            async with aopen(path) as fd:
                return await fd.read()

    return _read_async


_builtin_modules: set[str] = set(sys.builtin_module_names)


class GriffeLoader:
    """The Griffe loader, allowing to load data from modules."""

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
        self._time_stats: dict = {
            "time_spent_visiting": 0,
            "time_spent_inspecting": 0,
        }
        patch_ast()

    def load_module(
        self,
        module: str | Path,
        submodules: bool = True,
        search_paths: Sequence[str | Path] | None = None,
        try_relative_path: bool = True,
    ) -> Module:
        """Load a module.

        Parameters:
            module: The module name or path.
            submodules: Whether to recurse on the submodules.
            search_paths: The paths to search into.
            try_relative_path: Whether to try finding the module as a relative path.

        Returns:
            A module.
        """
        if module in _builtin_modules:
            logger.debug(f"{module} is a builtin module: inspecting")
            module_name = module
            top_module = self._inspect_module(module)  # type: ignore[arg-type]
        else:
            try:
                module_name, top_module_name, top_module_path = _top_name_and_path(
                    module, search_paths, try_relative_path
                )
            except ModuleNotFoundError:
                logger.debug(f"Could not find {module}: trying inspection")
                module_name = module
                top_module = self._inspect_module(module)  # type: ignore[arg-type]
            else:
                logger.debug(f"Found {module}: visiting")
                top_module = self._load_module_path(top_module_name, top_module_path, submodules=submodules)
        self.modules_collection[top_module.path] = top_module
        return self.modules_collection[module_name]  # type: ignore[index]

    def resolve_aliases(  # noqa: WPS231
        self,
        only_exported: bool = True,
        only_known_modules: bool = True,
        max_iterations: int | None = None,
    ) -> tuple[set[str], int]:
        """Resolve aliases.

        Parameters:
            only_exported: When true, only try to resolve an alias if it is explicitely exported.
            only_known_modules: When true, don't try to load unspecified modules to resolve aliases.
            max_iterations: Maximum number of iterations on the loader modules collection.

        Returns:
            The unresolved aliases and the number of iterations done.
        """
        if max_iterations is None:
            max_iterations = float("inf")  # type: ignore[assignment]
        prev_unresolved: set[str] = set()
        unresolved: set[str] = set("0")  # init to enter loop
        iteration = 0
        collection = self.modules_collection.members
        while unresolved and unresolved != prev_unresolved and iteration < max_iterations:  # type: ignore[operator]
            prev_unresolved = unresolved - {"0"}
            unresolved = set()
            resolved: set[str] = set()
            iteration += 1
            for module_name in list(collection.keys()):
                module = collection[module_name]
                next_resolved, next_unresolved = self.resolve_module_aliases(module, only_exported, only_known_modules)
                resolved |= next_resolved
                unresolved |= next_unresolved
            logger.debug(
                f"Iteration {iteration} finished, {len(resolved)} aliases resolved, still {len(unresolved)} to go"
            )
        return unresolved, iteration

    def resolve_module_aliases(  # noqa: WPS231
        self,
        obj: Object,
        only_exported: bool = True,
        only_known_modules: bool = True,
        seen: set | None = None,
    ) -> tuple[set[str], set[str]]:
        """Follow aliases: try to recursively resolve all found aliases.

        Parameters:
            obj: The object and its members to recurse on.
            only_exported: When true, only try to resolve an alias if it is explicitely exported.
            only_known_modules: When true, don't try to load unspecified modules to resolve aliases.
            seen: Used to avoid infinite recursion.

        Returns:
            Both sets of resolved and unresolved aliases.
        """
        resolved = set()
        unresolved = set()
        expanded = {}
        to_remove = []
        seen = seen or set()
        seen.add(obj.path)

        # iterate a first time to expand wildcards
        for member in obj.members.values():
            if member.is_alias and member.wildcard:  # type: ignore[union-attr]  # we know it's an alias
                package = member.wildcard.split(".", 1)[0]  # type: ignore[union-attr]
                if obj.package.path != package and package not in self.modules_collection:
                    try:
                        self.load_module(package, try_relative_path=False)
                    except ImportError as error:
                        logger.debug(f"Could not expand wildcard import {member.name} in {obj.path}: {error}")
                    else:
                        expanded.update(self._expand_wildcard(member))  # type: ignore[arg-type]
                        to_remove.append(member.name)

        for name in to_remove:
            del obj[name]  # noqa: WPS420
        for new_member in expanded.values():
            if new_member.is_alias and not new_member.wildcard:  # type: ignore[union-attr]
                try:
                    alias = Alias(new_member.name, new_member.target)  # type: ignore[union-attr]
                except AliasResolutionError:
                    alias = new_member  # type: ignore[assignment]  # noqa: WPS437
                except CyclicAliasError as error:  # noqa: WPS440
                    logger.debug(str(error))
            else:
                alias = Alias(new_member.name, new_member)
            obj[new_member.name] = alias

        # iterate a second time to resolve aliases and recurse
        for member in obj.members.values():  # noqa: WPS440
            if member.is_alias:
                if member.wildcard or member.resolved:  # type: ignore[union-attr]
                    continue
                if only_exported and not member.is_explicitely_exported:
                    continue
                try:
                    member.resolve_target()  # type: ignore[union-attr]
                except AliasResolutionError as error:  # noqa: WPS440
                    path = member.path
                    target = error.target_path  # type: ignore[union-attr]  # noqa: WPS437
                    logger.debug(f"Alias resolution error for {path} -> {target}")
                    unresolved.add(path)
                    package = target.split(".", 1)[0]
                    load_module = (
                        not only_known_modules
                        and obj.package.path != package
                        and package not in self.modules_collection
                    )
                    if load_module:
                        try:  # noqa: WPS505
                            self.load_module(package, try_relative_path=False)
                        except ImportError as error:  # noqa: WPS440
                            logger.debug(f"Could not follow alias {member.path}: {error}")
                except CyclicAliasError as error:
                    logger.debug(str(error))
                else:
                    logger.debug(f"Alias {member.path} was resolved to {member.target.path}")  # type: ignore[union-attr]
                    resolved.add(member.path)
            elif member.kind in {Kind.MODULE, Kind.CLASS} and member.path not in seen:
                sub_resolved, sub_unresolved = self.resolve_module_aliases(
                    member, only_exported, only_known_modules, seen  # type: ignore[arg-type]
                )
                resolved |= sub_resolved
                unresolved |= sub_unresolved

        return resolved, unresolved

    def stats(self) -> dict:
        """Compute some statistics.

        Returns:
            Some statistics.
        """
        return {**stats(self), **self._time_stats}

    def _load_module_path(
        self,
        module_name: str,
        module_path: Path,
        submodules: bool = True,
        parent: Module | None = None,
    ) -> Module:
        logger.debug(f"Loading path {module_path}")
        if module_path.is_dir():
            module = self._create_module(module_name, module_path)
        elif module_path.suffix == ".py":
            code = module_path.read_text()
            module = self._visit_module(code, module_name, module_path, parent)
        else:
            module = self._inspect_module(module_name, module_path, parent)
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
            logger.debug(f"{error}. Missing __init__ module?")
            return
        try:  # noqa: WPS225
            member_parent[subparts[-1]] = self._load_module_path(
                subparts[-1], subpath, submodules=False, parent=member_parent
            )
        except SyntaxError as error:  # noqa: WPS440
            logger.debug(f"Syntax error: {error}")
        except ImportError as error:  # noqa: WPS440
            logger.debug(f"Import error: {error}")
        except UnicodeDecodeError as error:  # noqa: WPS440
            logger.debug(f"UnicodeDecodeError when loading {subpath}: {error}")
        except OSError as error:  # noqa: WPS440
            logger.debug(f"OSError when loading {subpath}: {error}")

    def _create_module(self, module_name: str, module_path: Path) -> Module:
        return Module(
            module_name,
            filepath=module_path,
            lines_collection=self.lines_collection,
            modules_collection=self.modules_collection,
        )

    def _visit_module(self, code: str, module_name: str, module_path: Path, parent: Module | None = None) -> Module:
        self.lines_collection[module_path] = code.splitlines(keepends=False)
        start = datetime.now()
        module = visit(
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
        elapsed = datetime.now() - start
        self._time_stats["time_spent_visiting"] += elapsed.microseconds
        return module

    def _inspect_module(self, module_name: str, filepath: Path | None = None, parent: Module | None = None) -> Module:
        for prefix in _ignored_modules:
            if module_name.startswith(prefix):
                raise ImportError(f"Ignored module '{module_name}'")
        start = datetime.now()
        try:
            module = inspect(
                module_name,
                filepath=filepath,
                extensions=self.extensions,
                parent=parent,
                docstring_parser=self.docstring_parser,
                docstring_options=self.docstring_options,
                lines_collection=self.lines_collection,
            )
        except SystemExit as error:
            raise ImportError(f"Importing '{module_name}' raised a system exit") from error
        elapsed = datetime.now() - start
        self._time_stats["time_spent_inspecting"] += elapsed.microseconds
        return module

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

    def _expand_wildcard(self, wildcard_obj: Alias) -> dict[str, Object | Alias]:
        module = self.modules_collection[wildcard_obj.wildcard]  # type: ignore[index]  # we know it's a wildcard
        explicitely = "__all__" in module.members
        return {
            name: imported_member
            for name, imported_member in module.members.items()
            if imported_member.is_exported(explicitely=explicitely)
        }


def _top_name_and_path(
    module: str | Path,
    search_paths: Sequence[str | Path] | None = None,
    try_relative_path: bool = True,
) -> tuple[str, str, Path]:
    module_name, module_path = find_module_or_path(module, search_paths, try_relative_path)
    module_parts = module_name.split(".")
    top_module_name = module_parts[0]
    top_module_path = module_path
    for _ in range(len(module_parts) - 1):
        top_module_path = top_module_path.parent
    return module_name, top_module_name, top_module_path


def find_module_or_path(
    module: str | Path,
    search_paths: Sequence[str | Path] | None = None,
    try_relative_path: bool = True,
) -> tuple[str, Path]:
    """Find the name and path of a module.

    If a Path is passed, only try to find the module as a file path.
    If a string is passed, first try to find the module as a file path,
    then look into the search paths.

    Parameters:
        module: The module name or path.
        search_paths: The paths to search into.
        try_relative_path: Whether to try finding the module as a relative path,
            when the given module is not already a path.

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
    elif try_relative_path:
        # passed a string (from CLI or Python code), try both
        try:
            module_name, module_path = _module_name_path(Path(module))
        except FileNotFoundError:
            module_name = module
            module_path = find_module(module_name, search_paths=search_paths)
    else:
        module_name = module
        module_path = find_module(module_name, search_paths=search_paths)
    return module_name, module_path


def _module_name_path(path: Path) -> tuple[str, Path]:  # noqa: WPS231
    if path.is_dir():
        for ext in _accepted_py_module_extensions:
            module_path = path / f"__init__{ext}"
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
                if location.suffix:
                    location = location.parent
                search = [location.parent]
                # TODO: possible optimization
                # always break if exists?
                break

    # resume regular search
    filepaths = [
        # TODO: handle .py[cod] and .so files?
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
        # TODO: handle .py[cod] and .so files?
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


def _filter_py_modules(path: Path) -> Iterator[Path]:
    for root, dirs, files in os.walk(path, topdown=True):
        # optimization: modify dirs in-place to exclude __pycache__ directories
        dirs[:] = [dir for dir in dirs if dir != "__pycache__"]  # noqa: WPS362
        for relfile in files:
            if os.path.splitext(relfile)[1] in _extensions_set:
                yield Path(root, relfile)


def iter_submodules(path: Path) -> Iterator[NamePartsAndPathType]:  # noqa: WPS231,WPS234
    """Iterate on a module's submodules, if any.

    Parameters:
        path: The module path.

    Yields:
        name_parts (tuple[str, ...]): The parts of a submodule name.
        filepath (Path): A submodule filepath.
    """
    if path.stem == "__init__":
        path = path.parent
    # optimization: just check if the file name ends with .py
    # (to distinguish it from a directory),
    # not if it's an actual file
    elif path.suffix in _extensions_set:
        return

    for subpath in _filter_py_modules(path):
        rel_subpath = subpath.relative_to(path)
        py_file = rel_subpath.suffix == ".py"
        stem = rel_subpath.stem
        if not py_file:
            # .py[cod] and .so files look like `name.cpython-38-x86_64-linux-gnu.ext`
            stem = stem.split(".", 1)[0]
        if stem == "__init__":
            # optimization: since it's a relative path,
            # if it has only one part and is named __init__,
            # it means it's the starting path
            # (no need to compare it against starting path)
            if len(rel_subpath.parts) == 1:
                continue
            yield rel_subpath.parts[:-1], subpath
        elif py_file:
            yield rel_subpath.with_suffix("").parts, subpath
        else:
            yield rel_subpath.with_name(stem).parts, subpath


def _module_depth(name_parts_and_path: NamePartsAndPathType) -> int:
    return len(name_parts_and_path[0])
