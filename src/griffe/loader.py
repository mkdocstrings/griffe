"""This module contains the code allowing to load modules data.

This is the entrypoint to use griffe programatically:

```python
from griffe.loader import GriffeLoader

griffe = GriffeLoader()
fastapi = griffe.load_module("fastapi")
```
"""

from __future__ import annotations

import sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

from griffe.agents.extensions import Extensions
from griffe.agents.inspector import inspect
from griffe.agents.visitor import patch_ast, visit
from griffe.collections import LinesCollection, ModulesCollection
from griffe.dataclasses import Alias, Kind, Module, Object
from griffe.docstrings.parsers import Parser
from griffe.exceptions import AliasResolutionError, CyclicAliasError, LoadingError, UnimportableModuleError
from griffe.finder import ModuleFinder
from griffe.logger import get_logger
from griffe.stats import stats

logger = get_logger(__name__)


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

    ignored_modules = {"debugpy", "_pydev"}

    def __init__(
        self,
        extensions: Extensions | None = None,
        search_paths: Sequence[str | Path] | None = None,
        docstring_parser: Parser | None = None,
        docstring_options: dict[str, Any] | None = None,
        lines_collection: LinesCollection | None = None,
        modules_collection: ModulesCollection | None = None,
    ) -> None:
        """Initialize the loader.

        Parameters:
            extensions: The extensions to use.
            search_paths: The paths to search into.
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
        self.finder: ModuleFinder = ModuleFinder(search_paths)
        self._time_stats: dict = {
            "time_spent_visiting": 0,
            "time_spent_inspecting": 0,
        }
        patch_ast()

    def load_module(
        self,
        module: str | Path,
        submodules: bool = True,
        try_relative_path: bool = True,
    ) -> Module:
        """Load a module.

        Parameters:
            module: The module name or path.
            submodules: Whether to recurse on the submodules.
            try_relative_path: Whether to try finding the module as a relative path.

        Raises:
            LoadingError: When loading a module failed for various reasons.

        Returns:
            A module.
        """
        module_name: str
        if module in _builtin_modules:
            logger.debug(f"{module} is a builtin module: inspecting")
            module_name = module  # type: ignore[assignment]
            top_module = self._inspect_module(module)  # type: ignore[arg-type]
            return self._store_and_return(module_name, top_module)

        try:
            module_name, package = self.finder.find_spec(module, try_relative_path)
        except ModuleNotFoundError:
            logger.debug(f"Could not find {module}: trying inspection")
            module_name = module  # type: ignore[assignment]
            top_module = self._inspect_module(module)  # type: ignore[arg-type]
        else:
            logger.debug(f"Found {module}: loading")
            try:  # noqa: WPS505
                top_module = self._load_module(package.name, package.path, submodules=submodules)
            except LoadingError as error:  # noqa: WPS440
                logger.error(str(error))
                raise
        return self._store_and_return(module_name, top_module)

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

    def _store_and_return(self, name: str, module: Module) -> Module:
        self.modules_collection[module.path] = module
        return self.modules_collection[name]  # type: ignore[index]

    def _load_module(  # noqa: WPS238
        self,
        module_name: str,
        module_path: Path | list[Path],
        submodules: bool = True,
        parent: Module | None = None,
    ) -> Module:
        try:  # noqa: WPS225
            return self._load_module_path(module_name, module_path, submodules, parent)
        except SyntaxError as error:  # noqa: WPS440
            raise LoadingError(f"Syntax error: {error}") from error
        except ImportError as error:  # noqa: WPS440
            raise LoadingError(f"Import error: {error}") from error
        except UnicodeDecodeError as error:  # noqa: WPS440
            raise LoadingError(f"UnicodeDecodeError when loading {module_path}: {error}") from error
        except OSError as error:  # noqa: WPS440
            raise LoadingError(f"OSError when loading {module_path}: {error}") from error

    def _load_module_path(
        self,
        module_name: str,
        module_path: Path | list[Path],
        submodules: bool = True,
        parent: Module | None = None,
    ) -> Module:
        logger.debug(f"Loading path {module_path}")
        if isinstance(module_path, list):
            module = self._create_module(module_name, module_path)
        elif module_path.suffix == ".py":
            code = module_path.read_text(encoding="utf8")
            module = self._visit_module(code, module_name, module_path, parent)
        else:
            module = self._inspect_module(module_name, module_path, parent)
        if submodules:
            self._load_submodules(module)
        return module

    def _load_submodules(self, module: Module) -> None:
        for subparts, subpath in self.finder.submodules(module):
            self._load_submodule(module, subparts, subpath)

    def _load_submodule(self, module: Module, subparts: tuple[str, ...], subpath: Path) -> None:
        try:
            member_parent = self._member_parent(module, subparts, subpath)
        except UnimportableModuleError as error:
            # TODO: maybe add option to still load them
            # TODO: maybe increase level to WARNING
            logger.debug(f"{error}. Missing __init__ module?")
            return
        try:
            member_parent[subparts[-1]] = self._load_module(
                subparts[-1], subpath, submodules=False, parent=member_parent
            )
        except LoadingError as error:  # noqa: WPS440
            logger.debug(str(error))

    def _create_module(self, module_name: str, module_path: Path | list[Path]) -> Module:
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
        for prefix in self.ignored_modules:
            if module_name.startswith(prefix):
                raise ImportError(f"Ignored module '{module_name}'")
        start = datetime.now()
        try:
            module = inspect(
                module_name,
                filepath=filepath,
                import_paths=self.finder.search_paths,
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

    def _member_parent(self, module: Module, subparts: tuple[str, ...], subpath: Path) -> Module:
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
