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
from typing import Any, Sequence, cast
from warnings import warn

from griffe.agents.extensions import Extensions
from griffe.agents.inspector import inspect
from griffe.agents.visitor import patch_ast, visit
from griffe.collections import LinesCollection, ModulesCollection
from griffe.dataclasses import Alias, Kind, Module, Object
from griffe.docstrings.parsers import Parser
from griffe.exceptions import AliasResolutionError, CyclicAliasError, LoadingError, UnimportableModuleError
from griffe.expressions import Name
from griffe.finder import ModuleFinder, NamespacePackage, Package
from griffe.logger import get_logger
from griffe.merger import merge_stubs
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
            return path.read_text(encoding="utf8")

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
        allow_inspection: bool = True,
    ) -> None:
        """Initialize the loader.

        Parameters:
            extensions: The extensions to use.
            search_paths: The paths to search into.
            docstring_parser: The docstring parser to use. By default, no parsing is done.
            docstring_options: Additional docstring parsing options.
            lines_collection: A collection of source code lines.
            modules_collection: A collection of modules.
            allow_inspection: Whether to allow inspecting modules when visiting them is not possible.
        """
        self.extensions: Extensions = extensions or Extensions()
        self.docstring_parser: Parser | None = docstring_parser
        self.docstring_options: dict[str, Any] = docstring_options or {}
        self.lines_collection: LinesCollection = lines_collection or LinesCollection()
        self.modules_collection: ModulesCollection = modules_collection or ModulesCollection()
        self.allow_inspection: bool = allow_inspection
        self.finder: ModuleFinder = ModuleFinder(search_paths)
        self._time_stats: dict = {
            "time_spent_visiting": 0,
            "time_spent_inspecting": 0,
        }
        patch_ast()

    def load_module(  # noqa: WPS231
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
            ModuleNotFoundError: When a module was not found and inspection is disallowed.

        Returns:
            A module.
        """
        module_name: str
        if module in _builtin_modules:
            logger.debug(f"{module} is a builtin module")
            if self.allow_inspection:
                logger.debug(f"Inspecting {module}")
                module_name = module  # type: ignore[assignment]
                top_module = self._inspect_module(module)  # type: ignore[arg-type]
                self.modules_collection[top_module.path] = top_module
                return self.modules_collection[module_name]  # type: ignore[index]
            raise LoadingError("Cannot load builtin module without inspection")
        try:  # noqa: WPS503
            module_name, package = self.finder.find_spec(module, try_relative_path)
        except ModuleNotFoundError:
            logger.debug(f"Could not find {module}")
            if self.allow_inspection:
                logger.debug(f"Trying inspection on {module}")
                module_name = module  # type: ignore[assignment]
                top_module = self._inspect_module(module)  # type: ignore[arg-type]
                self.modules_collection[top_module.path] = top_module
            else:
                raise
        else:
            logger.debug(f"Found {module}: loading")
            try:  # noqa: WPS505
                top_module = self._load_package(package, submodules=submodules)
            except LoadingError as error:  # noqa: WPS440
                logger.error(str(error))
                raise
        return self.modules_collection[module_name]  # type: ignore[index]

    def resolve_aliases(  # noqa: WPS231
        self,
        *,
        implicit: bool | None = None,
        external: bool | None = None,
        max_iterations: int | None = None,
        only_exported: bool | None = None,
        only_known_modules: bool | None = None,
    ) -> tuple[set[str], int]:
        """Resolve aliases.

        Parameters:
            implicit: When false, only try to resolve an alias if it is explicitely exported.
            external: When false, don't try to load unspecified modules to resolve aliases.
            max_iterations: Maximum number of iterations on the loader modules collection.
            only_exported: Deprecated. Use the `implicit` parameter instead (inverting the value).
            only_known_modules: Deprecated. Use the `external` parameter instead (inverting the value).

        Returns:
            The unresolved aliases and the number of iterations done.
        """
        # TODO: remove deprecated params at some point
        if only_exported is not None and implicit is None:
            warn(
                "Parameter `only_exported` is deprecated, use `implicit` instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            implicit = not only_exported

        if only_known_modules is not None and external is None:
            warn(
                "Parameter `only_known_modules` is deprecated, use `external` instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            external = not only_known_modules

        # TODO: set as param defaults once deprecated params are dropped
        if implicit is None:
            implicit = False
        if external is None:
            external = False

        if max_iterations is None:
            max_iterations = float("inf")  # type: ignore[assignment]
        prev_unresolved: set[str] = set()
        unresolved: set[str] = set("0")  # init to enter loop
        iteration = 0
        collection = self.modules_collection.members
        for exports_module in list(collection.values()):
            self.expand_exports(exports_module)
        for wildcards_module in list(collection.values()):
            self.expand_wildcards(wildcards_module)
        load_failures: set[str] = set()
        while unresolved and unresolved != prev_unresolved and iteration < max_iterations:  # type: ignore[operator]
            prev_unresolved = unresolved - {"0"}
            unresolved = set()
            resolved: set[str] = set()
            iteration += 1
            for module_name in list(collection.keys()):
                module = collection[module_name]
                next_resolved, next_unresolved = self.resolve_module_aliases(
                    module,
                    implicit,
                    external,
                    load_failures=load_failures,
                )
                resolved |= next_resolved
                unresolved |= next_unresolved
            logger.debug(
                f"Iteration {iteration} finished, {len(resolved)} aliases resolved, still {len(unresolved)} to go"
            )
        return unresolved, iteration

    def expand_exports(self, module: Module, seen: set | None = None) -> None:  # noqa: WPS231
        """Expand exports: try to recursively expand all module exports.

        Parameters:
            module: The module to recurse on.
            seen: Used to avoid infinite recursion.
        """
        seen = seen or set()
        seen.add(module.path)
        if module.exports is None:
            return
        expanded = set()
        for export in module.exports:
            if isinstance(export, Name):
                module_path = export.full.rsplit(".", 1)[0]  # remove trailing .__all__
                try:
                    next_module = self.modules_collection[module_path]
                except KeyError:
                    logger.debug(f"Cannot expand '{export.full}', try pre-loading corresponding package")
                    continue
                if next_module.path not in seen:
                    self.expand_exports(next_module, seen)
                    try:
                        expanded |= next_module.exports
                    except TypeError:
                        logger.warning(f"Unsupported item in {module.path}.__all__: {export} (use strings only)")
            else:
                expanded.add(export)
        module.exports = expanded

    def expand_wildcards(  # noqa: WPS231
        self,
        obj: Object,
        external: bool = False,
        seen: set | None = None,
    ) -> None:
        """Expand wildcards: try to recursively expand all found wildcards.

        Parameters:
            obj: The object and its members to recurse on.
            external: When true, try to load unspecified modules to expand wildcards.
            seen: Used to avoid infinite recursion.
        """
        expanded = []
        to_remove = []
        seen = seen or set()
        seen.add(obj.path)

        for member in obj.members.values():
            if member.is_alias and member.wildcard:  # type: ignore[union-attr]  # we know it's an alias
                package = member.wildcard.split(".", 1)[0]  # type: ignore[union-attr]
                not_loaded = obj.package.path != package and package not in self.modules_collection
                if not_loaded:
                    if not external:
                        continue
                    try:
                        self.load_module(package, try_relative_path=False)
                    except ImportError as error:
                        logger.debug(f"Could not expand wildcard import {member.name} in {obj.path}: {error}")
                        continue
                target = self.modules_collection[member.target_path]  # type: ignore[union-attr]
                if target.path not in seen:
                    try:
                        self.expand_wildcards(target, external, seen)  # type: ignore[union-attr]
                    except (AliasResolutionError, CyclicAliasError) as error:  # noqa: WPS440
                        logger.debug(f"Could not expand wildcard import {member.name} in {obj.path}: {error}")
                        continue
                expanded.extend(self._expand_wildcard(member))  # type: ignore[arg-type]
                to_remove.append(member.name)
            elif not member.is_alias and member.is_module and member.path not in seen:
                self.expand_wildcards(member, external, seen)  # type: ignore[arg-type]

        for name in to_remove:
            del obj[name]  # noqa: WPS420

        for new_member, alias_lineno, alias_endlineno in expanded:
            overwrite = False
            already_present = new_member.name in obj.members
            self_alias = new_member.is_alias and cast(Alias, new_member).target_path == f"{obj.path}.{new_member.name}"
            if already_present:
                old_member = obj[new_member.name]
                old_lineno = getattr(old_member, "alias_lineno", old_member.lineno or 0)
                overwrite = alias_lineno > old_lineno  # type: ignore[operator]
            if not self_alias and (not already_present or overwrite):
                obj[new_member.name] = Alias(
                    new_member.name,
                    new_member,
                    lineno=alias_lineno,
                    endlineno=alias_endlineno,
                    parent=obj,  # type: ignore[arg-type]
                )

    def resolve_module_aliases(  # noqa: WPS231
        self,
        obj: Object,
        implicit: bool = False,
        external: bool = False,
        seen: set[str] | None = None,
        load_failures: set[str] | None = None,
    ) -> tuple[set[str], set[str]]:
        """Follow aliases: try to recursively resolve all found aliases.

        Parameters:
            obj: The object and its members to recurse on.
            implicit: When false, only try to resolve an alias if it is explicitely exported.
            external: When false, don't try to load unspecified modules to resolve aliases.
            seen: Used to avoid infinite recursion.
            load_failures: Set of external packages we failed to load (to prevent retries).

        Returns:
            Both sets of resolved and unresolved aliases.
        """
        resolved = set()
        unresolved = set()
        if load_failures is None:
            load_failures = set()
        seen = seen or set()
        seen.add(obj.path)

        for member in obj.members.values():  # noqa: WPS440
            if member.is_alias:
                if member.wildcard or member.resolved:  # type: ignore[union-attr]
                    continue
                if not implicit and not member.is_explicitely_exported:
                    continue
                try:
                    member.resolve_target()  # type: ignore[union-attr]
                except AliasResolutionError as error:  # noqa: WPS440
                    target = error.target_path  # type: ignore[union-attr]  # noqa: WPS437
                    unresolved.add(member.path)
                    package = target.split(".", 1)[0]
                    load_module = (
                        external
                        and package not in load_failures
                        and obj.package.path != package
                        and package not in self.modules_collection
                    )
                    if load_module:
                        logger.debug(f"Failed to resolve alias {member.path} -> {target}")
                        try:  # noqa: WPS505
                            self.load_module(package, try_relative_path=False)
                        except ImportError as error:  # noqa: WPS440
                            logger.debug(f"Could not follow alias {member.path}: {error}")
                            load_failures.add(package)
                except CyclicAliasError as error:
                    logger.debug(str(error))
                else:
                    logger.debug(f"Alias {member.path} was resolved to {member.target.path}")  # type: ignore[union-attr]
                    resolved.add(member.path)
            elif member.kind in {Kind.MODULE, Kind.CLASS} and member.path not in seen:
                sub_resolved, sub_unresolved = self.resolve_module_aliases(
                    member, implicit, external, seen, load_failures  # type: ignore[arg-type]
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

    def _load_package(self, package: Package | NamespacePackage, submodules: bool = True) -> Module:
        top_module = self._load_module(package.name, package.path, submodules=submodules)
        self.modules_collection[top_module.path] = top_module
        if isinstance(package, NamespacePackage):
            return top_module
        if package.stubs:
            self.expand_wildcards(top_module)
            stubs = self._load_module(package.name, package.stubs, submodules=False)
            return merge_stubs(top_module, stubs)
        return top_module

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
        elif module_path.suffix in {".py", ".pyi"}:
            code = module_path.read_text(encoding="utf8")
            module = self._visit_module(code, module_name, module_path, parent)
        elif self.allow_inspection:
            module = self._inspect_module(module_name, module_path, parent)
        else:
            raise LoadingError("Cannot load compiled module without inspection")
        if submodules:
            self._load_submodules(module)
        return module

    def _load_submodules(self, module: Module) -> None:
        for subparts, subpath in self.finder.submodules(module):
            self._load_submodule(module, subparts, subpath)

    def _load_submodule(self, module: Module, subparts: tuple[str, ...], subpath: Path) -> None:
        try:
            parent_module = self._get_or_create_parent_module(module, subparts, subpath)
        except UnimportableModuleError as error:
            # TODO: maybe add option to still load them
            # TODO: maybe increase level to WARNING
            logger.debug(f"{error}. Missing __init__ module?")
            return
        submodule_name = subparts[-1]
        if "." in submodule_name:
            logger.debug(f"Skip {subpath}, dots in filenames are not supported")
            return
        try:
            parent_module[submodule_name] = self._load_module(
                submodule_name, subpath, submodules=False, parent=parent_module
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

    def _get_or_create_parent_module(  # noqa: WPS231
        self,
        module: Module,
        subparts: tuple[str, ...],
        subpath: Path,
    ) -> Module:
        parent_parts = subparts[:-1]
        if not parent_parts:
            return module
        parent_module = module
        parents = list(subpath.parents)
        if subpath.stem == "__init__":
            parents.pop(0)
        for parent_offset, parent_part in enumerate(parent_parts, 2):
            module_filepath = parents[len(subparts) - parent_offset]
            try:
                parent_module = parent_module[parent_part]
            except KeyError:
                if parent_module.is_namespace_package or parent_module.is_namespace_subpackage:
                    next_parent_module = self._create_module(parent_part, [module_filepath])
                    parent_module[parent_part] = next_parent_module
                    parent_module = next_parent_module
                else:
                    raise UnimportableModuleError(f"Skip {subpath}, it is not importable")
            else:
                if parent_module.is_namespace_package or parent_module.is_namespace_subpackage:
                    if module_filepath not in parent_module.filepath:  # type: ignore[operator]
                        parent_module.filepath.append(module_filepath)  # type: ignore[union-attr]
        return parent_module

    def _expand_wildcard(self, wildcard_obj: Alias) -> list[tuple[Object | Alias, int | None, int | None]]:
        module = self.modules_collection[wildcard_obj.wildcard]  # type: ignore[index]  # we know it's a wildcard
        explicitely = "__all__" in module.members
        return [
            (imported_member, wildcard_obj.alias_lineno, wildcard_obj.alias_endlineno)
            for imported_member in module.members.values()
            if imported_member.is_exported(explicitely=explicitely)
        ]


def load(
    module: str | Path,
    submodules: bool = True,
    try_relative_path: bool = True,
    extensions: Extensions | None = None,
    search_paths: Sequence[str | Path] | None = None,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
    allow_inspection: bool = True,
) -> Module:
    """Load and return a module.

    Example:

    ```python
    import griffe

    module = griffe.load(...)
    ```

    This is a shortcut for:

    ```python
    from griffe.loader import GriffeLoader

    loader = GriffeLoader(...)
    module = loader.load_module(...)
    ```

    See the documentation for the loader: [`GriffeLoader`][griffe.loader.GriffeLoader].

    Parameters:
        module: The module name or path.
        submodules: Whether to recurse on the submodules.
        try_relative_path: Whether to try finding the module as a relative path.
        extensions: The extensions to use.
        search_paths: The paths to search into.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Additional docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.
        allow_inspection: Whether to allow inspecting modules when visiting them is not possible.

    Returns:
        A loaded module.
    """
    return GriffeLoader(
        extensions=extensions,
        search_paths=search_paths,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        lines_collection=lines_collection,
        modules_collection=modules_collection,
        allow_inspection=allow_inspection,
    ).load_module(
        module=module,
        submodules=submodules,
        try_relative_path=try_relative_path,
    )
