"""This module contains the code allowing to find modules."""

from __future__ import annotations

import os
import re
import sys
from contextlib import suppress
from pathlib import Path
from typing import Iterator, Sequence, Tuple

from griffe.dataclasses import Module
from griffe.exceptions import UnhandledEditableModuleError
from griffe.logger import get_logger

NamePartsType = Tuple[str, ...]
NamePartsAndPathType = Tuple[NamePartsType, Path]
logger = get_logger(__name__)


class Package:
    """This class is a simple placeholder used during the process of finding packages."""

    def __init__(self, name: str, path: Path, stubs: Path | None = None) -> None:
        """Initialize the package.

        Parameters:
            name: The package name.
            path: The package path(s).
            stubs: An optional path to the related stubs file (.pyi).
        """
        self.name: str = name
        self.path: Path = path
        self.stubs: Path | None = stubs


class NamespacePackage:
    """This class is a simple placeholder used during the process of finding packages."""

    def __init__(self, name: str, path: list[Path]) -> None:
        """Initialize the namespace package.

        Parameters:
            name: The package name.
            path: The package paths.
        """
        self.name: str = name
        self.path: list[Path] = path


class ModuleFinder:
    """The Griffe finder, allowing to find modules on the file system."""

    accepted_py_module_extensions = [".py", ".pyc", ".pyo", ".pyd", ".pyi", ".so"]
    extensions_set = set(accepted_py_module_extensions)

    def __init__(self, search_paths: Sequence[str | Path] | None = None) -> None:
        """Initialize the finder.

        Parameters:
            search_paths: Optional paths to search into.
        """
        self._paths_contents: dict[Path, list[Path]] = {}
        # optimization: pre-compute Paths to relieve CPU when joining paths
        self.search_paths = [path if isinstance(path, Path) else Path(path) for path in search_paths or sys.path]
        if bool(search_paths):
            # without custom search paths, sys.path is used, and is already extended from .pth files
            self._extend_from_pth_files()
        self._extend_from_editable_modules()

    def find_spec(
        self,
        module: str | Path,
        try_relative_path: bool = True,
    ) -> tuple[str, Package | NamespacePackage]:
        """Find the top module of a module.

        If a Path is passed, only try to find the module as a file path.
        If a string is passed, first try to find the module as a file path,
        then look into the search paths.

        Parameters:
            module: The module name or path.
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
            The name of the module, and an instance representing its (namespace) package.
        """
        module_path: Path | list[Path]
        if isinstance(module, Path):
            module_name, module_path = self._module_name_path(module)  # type: ignore[arg-type]
            top_module_name = self._top_module_name(module_path)
        elif try_relative_path:
            try:
                module_name, module_path = self._module_name_path(Path(module))
            except FileNotFoundError:
                module_name = module  # type: ignore[assignment]
                top_module_name = module.split(".", 1)[0]  # type: ignore[union-attr]
            else:
                top_module_name = self._top_module_name(module_path)
        else:
            module_name = module
            top_module_name = module.split(".", 1)[0]
        return module_name, self.find_package(top_module_name)

    def find_package(self, module_name: str) -> Package | NamespacePackage:  # noqa: WPS231
        """Find a package or namespace package.

        Parameters:
            module_name: The module name.

        Raises:
            ModuleNotFoundError: When the module cannot be found.

        Returns:
            A package or namespace package wrapper.
        """
        filepaths = [
            Path(module_name),
            # TODO: handle .py[cod] and .so files?
            Path(f"{module_name}.py"),
        ]

        namespace_dirs = []
        for path in self.search_paths:  # noqa: WPS440
            path_contents = self._contents(path)
            if path_contents:
                for choice in filepaths:
                    abs_path = path / choice
                    if abs_path in path_contents:
                        if abs_path.suffix:
                            stubs = abs_path.with_suffix(".pyi")
                            return Package(module_name, abs_path, stubs if stubs.exists() else None)
                        else:
                            init_module = abs_path / "__init__.py"
                            if init_module.exists() and not _is_pkg_style_namespace(init_module):
                                stubs = init_module.with_suffix(".pyi")
                                return Package(module_name, init_module, stubs if stubs.exists() else None)
                            namespace_dirs.append(abs_path)

        if namespace_dirs:
            return NamespacePackage(module_name, namespace_dirs)

        raise ModuleNotFoundError(module_name)

    def iter_submodules(  # noqa: WPS231,WPS234
        self,
        path: Path | list[Path],
        seen: set | None = None,
    ) -> Iterator[NamePartsAndPathType]:
        """Iterate on a module's submodules, if any.

        Parameters:
            path: The module path.
            seen: If not none, this set is used to skip some files.
                The goal is to replicate the behavior of Python by
                only using the first packages (with `__init__` modules)
                of the same name found in different namespace packages.
                As soon as we find an `__init__` module, we add its parent
                path to the `seen` set, which will be reused when scanning
                the next namespace packages.

        Yields:
            name_parts (tuple[str, ...]): The parts of a submodule name.
            filepath (Path): A submodule filepath.
        """
        if isinstance(path, list):
            seen = set()
            for path_elem in path:
                yield from self.iter_submodules(path_elem, seen)
            return

        if path.stem == "__init__":
            path = path.parent
        # optimization: just check if the file name ends with .py[icod]/.so
        # (to distinguish it from a directory),
        # not if it's an actual file
        elif path.suffix in self.extensions_set:
            return

        skip = set(seen) if seen else set()
        for subpath in self._filter_py_modules(path):
            rel_subpath = subpath.relative_to(path)
            if rel_subpath.parent in skip:
                logger.debug(f"Skip {subpath}, another module took precedence")
                continue
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
                if seen is not None:
                    seen.add(rel_subpath.parent)
            elif py_file:
                yield rel_subpath.with_suffix("").parts, subpath
            else:
                yield rel_subpath.with_name(stem).parts, subpath

    def submodules(self, module: Module) -> list[NamePartsAndPathType]:
        """Return the list of a module's submodules.

        Parameters:
            module: The parent module.

        Returns:
            A list of tuples containing the parts of the submodule name and its path.
        """
        return sorted(self.iter_submodules(module.filepath), key=_module_depth)

    def _module_name_path(self, path: Path) -> tuple[str, Path]:  # noqa: WPS231
        if path.is_dir():
            for ext in self.accepted_py_module_extensions:
                module_path = path / f"__init__{ext}"
                if module_path.exists():
                    return path.name, module_path
            return path.name, path
        if path.exists():
            if path.stem == "__init__":
                if path.parent.is_absolute():
                    return path.parent.name, path
                return path.parent.resolve().name, path
            return path.stem, path
        raise FileNotFoundError

    def _contents(self, path: Path) -> list[Path]:
        if path not in self._paths_contents:
            try:
                self._paths_contents[path] = list(path.iterdir())
            except (FileNotFoundError, NotADirectoryError):
                self._paths_contents[path] = []
        return self._paths_contents[path]

    def _append_search_path(self, path: Path) -> None:
        if path not in self.search_paths:
            self.search_paths.append(path)

    def _extend_from_pth_files(self):
        for path in self.search_paths:
            for item in self._contents(path):
                if item.suffix == ".pth":
                    for directory in _handle_pth_file(item):
                        self._append_search_path(directory)

    def _extend_from_editable_modules(self):
        for path in self.search_paths:  # noqa: WPS440
            for item in self._contents(path):
                if item.stem.startswith(("__editables_", "__editable__")) and item.suffix == ".py":
                    with suppress(UnhandledEditableModuleError):
                        self._append_search_path(_handle_editable_module(item))

    def _filter_py_modules(self, path: Path) -> Iterator[Path]:
        for root, dirs, files in os.walk(path, topdown=True):
            # optimization: modify dirs in-place to exclude __pycache__ directories
            dirs[:] = [dir for dir in dirs if dir != "__pycache__"]  # noqa: WPS362
            for relfile in files:
                if os.path.splitext(relfile)[1] in self.extensions_set:
                    yield Path(root, relfile)

    def _top_module_name(self, path: Path) -> str:
        # first find if a parent is in search paths
        parent_path = path if path.is_dir() else path.parent
        for search_path in self.search_paths:
            with suppress(ValueError):
                # TODO: it does not work when parent_path is relative and search_path absolute
                rel_path = parent_path.relative_to(search_path)
                top_path = search_path / rel_path.parts[0]
                return top_path.name
        # if not, get the highest directory with an __init__ module,
        # add its parent to search paths and return it
        while parent_path.parent != parent_path and (parent_path.parent / "__init__.py").exists():
            parent_path = parent_path.parent
        self.search_paths.insert(0, parent_path.parent)
        return parent_path.name


_re_pkgresources = re.compile(r"(?:__import__\([\"']pkg_resources[\"']\).declare_namespace\(__name__\))")
_re_pkgutil = re.compile(r"(?:__path__ = __import__\([\"']pkgutil[\"']\).extend_path\(__path__, __name__\))")
_re_import_line = re.compile(r"^import[ \t]")
_re_mapping_line = re.compile(r"^MAPPING = \{['\"].+['\"]: +['\"](.+)['\"]\}")


# TODO: for better robustness, we should load and minify the AST
# to search for particular call statements
def _is_pkg_style_namespace(init_module: Path) -> bool:
    code = init_module.read_text(encoding="utf8")
    return bool(_re_pkgresources.search(code) or _re_pkgutil.search(code))


def _module_depth(name_parts_and_path: NamePartsAndPathType) -> int:
    return len(name_parts_and_path[0])


def _handle_pth_file(path) -> list[Path]:  # noqa: WPS231
    # Support for .pth files pointing to directories.
    # From https://docs.python.org/3/library/site.html:
    # A path configuration file is a file whose name has the form name.pth
    # and exists in one of the four directories mentioned above;
    # its contents are additional items (one per line) to be added to sys.path.
    # Non-existing items are never added to sys.path,
    # and no check is made that the item refers to a directory rather than a file.
    # No item is added to sys.path more than once.
    # Blank lines and lines beginning with # are skipped.
    # Lines starting with import (followed by space or tab) are executed.
    directories = []
    for line in path.read_text(encoding="utf8").strip().splitlines(keepends=False):
        line = line.strip()
        if line and not line.startswith("#") and not _re_import_line.search(line):
            if os.path.exists(line):
                directories.append(Path(line))
    return directories


def _handle_editable_module(path: Path):  # noqa: WPS231
    try:
        editable_lines = path.read_text(encoding="utf8").splitlines(keepends=False)
    except FileNotFoundError:
        raise UnhandledEditableModuleError(path)
    if path.name.startswith("__editables_"):
        # support for how 'editables' writes these files:
        # example line: F.map_module('griffe', '/media/data/dev/griffe/src/griffe/__init__.py')
        new_path = Path(editable_lines[-1].split("'")[3])
        if new_path.exists():  # TODO: could remove existence check
            if new_path.name.startswith("__init__"):
                return new_path.parent.parent
            return new_path
    elif path.name.startswith("__editable__"):
        # support for how 'setuptools' writes these files:
        # example line: MAPPING = {'griffe': '/media/data/dev/griffe/src/griffe'}
        for line in editable_lines:
            match = _re_mapping_line.match(line)
            if match:
                new_path = Path(match.group(1))
                if new_path.exists():  # TODO: could remove existence check
                    return new_path.parent
                break
    raise UnhandledEditableModuleError(path)
