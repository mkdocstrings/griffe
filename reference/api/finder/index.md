# Finder

## **Advanced API**

## ModuleFinder

```
ModuleFinder(
    search_paths: Sequence[str | Path] | None = None,
)
```

The Griffe finder, allowing to find modules on the file system.

The module finder is generally not used directly. Each GriffeLoader instance creates its own module finder instance. The finder can be configured when instantiating the loader thanks to the loader's `search_paths` parameter.

Parameters:

- ### **`search_paths`**

  (`Sequence[str | Path] | None`, default: `None` ) – Optional paths to search into.

Methods:

- **`append_search_path`** – Append a search path.
- **`find_package`** – Find a package or namespace package.
- **`find_spec`** – Find the top-level parent module of a module.
- **`insert_search_path`** – Insert a search path at the given position.
- **`iter_submodules`** – Iterate on a module's submodules, if any.
- **`submodules`** – Return the list of a module's submodules.

Attributes:

- **`accepted_py_module_extensions`** (`list[str]`) – List of extensions supported by the finder.
- **`extensions_set`** (`set[str]`) – Set of extensions supported by the finder.
- **`search_paths`** (`list[Path]`) – The finder search paths.

Source code in `packages/griffelib/src/griffe/_internal/finder.py`

```
def __init__(self, search_paths: Sequence[str | Path] | None = None) -> None:
    """Initialize the finder.

    Parameters:
        search_paths: Optional paths to search into.
    """
    self._paths_contents: dict[Path, list[Path]] = {}
    self.search_paths: list[Path] = []
    """The finder search paths."""

    # Optimization: pre-compute Paths to relieve CPU when joining paths.
    for path in search_paths or sys.path:
        self.append_search_path(Path(path))

    self._always_scan_for: dict[str, list[Path]] = defaultdict(list)
    self._extend_from_pth_files()
```

### accepted_py_module_extensions

```
accepted_py_module_extensions: list[str] = [
    ".py",
    ".pyc",
    ".pyo",
    ".pyd",
    ".pyi",
    ".so",
]
```

List of extensions supported by the finder.

### extensions_set

```
extensions_set: set[str] = set(
    accepted_py_module_extensions
)
```

Set of extensions supported by the finder.

### search_paths

```
search_paths: list[Path] = []
```

The finder search paths.

### append_search_path

```
append_search_path(path: Path) -> None
```

Append a search path.

The path will be resolved (absolute, normalized). The path won't be appended if it is already in the search paths list.

Parameters:

- #### **`path`**

  (`Path`) – The path to append.

Source code in `packages/griffelib/src/griffe/_internal/finder.py`

```
def append_search_path(self, path: Path) -> None:
    """Append a search path.

    The path will be resolved (absolute, normalized).
    The path won't be appended if it is already in the search paths list.

    Parameters:
        path: The path to append.
    """
    self._append_search_path(path.resolve())
```

### find_package

```
find_package(
    module_name: str,
) -> Package | NamespacePackage
```

Find a package or namespace package.

Parameters:

- #### **`module_name`**

  (`str`) – The module name.

Raises:

- `ModuleNotFoundError` – When the module cannot be found.

Returns:

- `Package | NamespacePackage` – A package or namespace package wrapper.

Source code in `packages/griffelib/src/griffe/_internal/finder.py`

```
def find_package(self, module_name: str) -> Package | NamespacePackage:
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
        # TODO: Handle .py[cod] and .so files?
        # This would be needed for package that are composed
        # solely of a file with such an extension.
        Path(f"{module_name}.py"),
    ]

    real_module_name = module_name
    real_module_name = real_module_name.removesuffix("-stubs")
    namespace_dirs = []
    for path in self.search_paths:
        path_contents = self._contents(path)
        if path_contents:
            for choice in filepaths:
                abs_path = path / choice
                if abs_path in path_contents:
                    if abs_path.suffix:
                        stubs = abs_path.with_suffix(".pyi")
                        return Package(real_module_name, abs_path, stubs if stubs.exists() else None)
                    init_module = abs_path / "__init__.py"
                    if init_module.exists() and not _is_pkg_style_namespace(init_module):
                        stubs = init_module.with_suffix(".pyi")
                        return Package(real_module_name, init_module, stubs if stubs.exists() else None)
                    init_module = abs_path / "__init__.pyi"
                    if init_module.exists():
                        # Stubs package.
                        return Package(real_module_name, init_module, None)
                    namespace_dirs.append(abs_path)

    if namespace_dirs:
        return NamespacePackage(module_name, namespace_dirs)

    raise ModuleNotFoundError(module_name)
```

### find_spec

```
find_spec(
    module: str | Path,
    *,
    try_relative_path: bool = True,
    find_stubs_package: bool = False,
) -> tuple[str, Package | NamespacePackage]
```

Find the top-level parent module of a module.

If a Path is passed, only try to find the module as a file path. If a string is passed, first try to find the module as a file path, then look into the search paths.

Parameters:

- #### **`module`**

  (`str | Path`) – The module name or path.

- #### **`try_relative_path`**

  (`bool`, default: `True` ) – Whether to try finding the module as a relative path, when the given module is not already a path.

- #### **`find_stubs_package`**

  (`bool`, default: `False` ) – Whether to search for stubs-only package. If both the package and its stubs are found, they'll be merged together. If only the stubs are found, they'll be used as the package itself.

Raises:

- `FileNotFoundError` – When a Path was passed and the module could not be found: the directory has no __init__.py file in it the path does not exist
- `ModuleNotFoundError` – When a string was passed and the module could not be found: no module/__init__.py no module.py no module.pth no module directory (namespace packages) or unsupported .pth file

Returns:

- `tuple[str, Package | NamespacePackage]` – The name of the module, and an instance representing its (namespace) package.

Source code in `packages/griffelib/src/griffe/_internal/finder.py`

```
def find_spec(
    self,
    module: str | Path,
    *,
    try_relative_path: bool = True,
    find_stubs_package: bool = False,
) -> tuple[str, Package | NamespacePackage]:
    """Find the top-level parent module of a module.

    If a Path is passed, only try to find the module as a file path.
    If a string is passed, first try to find the module as a file path,
    then look into the search paths.

    Parameters:
        module: The module name or path.
        try_relative_path: Whether to try finding the module as a relative path,
            when the given module is not already a path.
        find_stubs_package: Whether to search for stubs-only package.
            If both the package and its stubs are found, they'll be merged together.
            If only the stubs are found, they'll be used as the package itself.

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
        module_name, module_path = self._module_name_path(module)
        top_module_name = self._top_module_name(module_path)
    elif try_relative_path:
        try:
            module_name, module_path = self._module_name_path(Path(module))
        except FileNotFoundError:
            module_name = module
            top_module_name = module.split(".", 1)[0]
        else:
            top_module_name = self._top_module_name(module_path)
    else:
        module_name = module
        top_module_name = module.split(".", 1)[0]

    # Only search for actual package, let exceptions bubble up.
    if not find_stubs_package:
        return module_name, self.find_package(top_module_name)

    # Search for both package and stubs-only package.
    try:
        package = self.find_package(top_module_name)
    except ModuleNotFoundError:
        package = None
    try:
        stubs = self.find_package(top_module_name + "-stubs")
    except ModuleNotFoundError:
        stubs = None

    # None found, raise error.
    if package is None and stubs is None:
        raise ModuleNotFoundError(top_module_name)

    # Both found, assemble them to be merged later.
    if package and stubs:
        if isinstance(package, Package) and isinstance(stubs, Package):
            package.stubs = stubs.path
        elif isinstance(package, NamespacePackage) and isinstance(stubs, NamespacePackage):
            package.path += stubs.path
        return module_name, package

    # Return either one.
    return module_name, package or stubs  # ty:ignore[invalid-return-type]
```

### insert_search_path

```
insert_search_path(position: int, path: Path) -> None
```

Insert a search path at the given position.

The path will be resolved (absolute, normalized). The path won't be inserted if it is already in the search paths list.

Parameters:

- #### **`position`**

  (`int`) – The insert position in the list.

- #### **`path`**

  (`Path`) – The path to insert.

Source code in `packages/griffelib/src/griffe/_internal/finder.py`

```
def insert_search_path(self, position: int, path: Path) -> None:
    """Insert a search path at the given position.

    The path will be resolved (absolute, normalized).
    The path won't be inserted if it is already in the search paths list.

    Parameters:
        position: The insert position in the list.
        path: The path to insert.
    """
    path = path.resolve()
    if path not in self.search_paths:
        self.search_paths.insert(position, path)
```

### iter_submodules

```
iter_submodules(
    path: Path | list[Path], seen: set | None = None
) -> Iterator[NamePartsAndPathType]
```

Iterate on a module's submodules, if any.

Parameters:

- #### **`path`**

  (`Path | list[Path]`) – The module path.

- #### **`seen`**

  (`set | None`, default: `None` ) – If not none, this set is used to skip some files. The goal is to replicate the behavior of Python by only using the first packages (with __init__ modules) of the same name found in different namespace packages. As soon as we find an __init__ module, we add its parent path to the seen set, which will be reused when scanning the next namespace packages.

Yields:

- **`name_parts`** ( `tuple[str, ...]` ) – The parts of a submodule name.
- **`filepath`** ( `Path` ) – A submodule filepath.

Source code in `packages/griffelib/src/griffe/_internal/finder.py`

```
def iter_submodules(
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
        # We never enter this condition again in recursive calls,
        # so we just have to set `seen` once regardless of its value.
        seen = set()
        for path_elem in path:
            yield from self.iter_submodules(path_elem, seen)
        return

    if path.stem == "__init__":
        path = path.parent
    # Optimization: just check if the file name ends with .py[icod]/.so
    # (to distinguish it from a directory), not if it's an actual file.
    elif path.suffix in self.extensions_set:
        return

    # `seen` is only set when we scan a list of paths (namespace package).
    # `skip` is used to prevent yielding modules
    # of a regular subpackage that we already yielded
    # from another part of the namespace.
    skip = set(seen or ())

    for subpath in self._filter_py_modules(path):
        rel_subpath = subpath.relative_to(path)
        if rel_subpath.parent in skip:
            logger.debug("Skip %s, another module took precedence", subpath)
            continue
        py_file = rel_subpath.suffix == ".py"
        stem = rel_subpath.stem
        if not py_file:
            # `.py[cod]` and `.so` files look like `name.cpython-38-x86_64-linux-gnu.ext`.
            stem = stem.split(".", 1)[0]
        if stem == "__init__":
            # Optimization: since it's a relative path, if it has only one part
            # and is named __init__, it means it's the starting path
            # (no need to compare it against starting path).
            if len(rel_subpath.parts) == 1:
                continue
            yield rel_subpath.parts[:-1], subpath
            if seen is not None:
                seen.add(rel_subpath.parent)
        elif py_file:
            yield rel_subpath.with_suffix("").parts, subpath
        else:
            yield rel_subpath.with_name(stem).parts, subpath
```

### submodules

```
submodules(module: Module) -> list[NamePartsAndPathType]
```

Return the list of a module's submodules.

Parameters:

- #### **`module`**

  (`Module`) – The parent module.

Returns:

- `list[NamePartsAndPathType]` – A list of tuples containing the parts of the submodule name and its path.

Source code in `packages/griffelib/src/griffe/_internal/finder.py`

```
def submodules(self, module: Module) -> list[NamePartsAndPathType]:
    """Return the list of a module's submodules.

    Parameters:
        module: The parent module.

    Returns:
        A list of tuples containing the parts of the submodule name and its path.
    """
    return sorted(
        chain(
            self.iter_submodules(module.filepath),
            self.iter_submodules(self._always_scan_for[module.name]),
        ),
        key=_module_depth,
    )
```

## Package

```
Package(name: str, path: Path, stubs: Path | None = None)
```

This class is a simple placeholder used during the process of finding packages.

Parameters:

- ### **`name`**

  (`str`) – The package name.

- ### **`path`**

  (`Path`) – The package path(s).

- ### **`stubs`**

  (`Path | None`, default: `None` ) – An optional path to the related stubs file (.pyi).

Attributes:

- **`name`** (`str`) – Package name.
- **`path`** (`Path`) – Package folder path.
- **`stubs`** (`Path | None`) – Package stubs file.

### name

```
name: str
```

Package name.

### path

```
path: Path
```

Package folder path.

### stubs

```
stubs: Path | None = None
```

Package stubs file.

## NamespacePackage

```
NamespacePackage(name: str, path: list[Path])
```

This class is a simple placeholder used during the process of finding packages.

Parameters:

- ### **`name`**

  (`str`) – The package name.

- ### **`path`**

  (`list[Path]`) – The package paths.

Attributes:

- **`name`** (`str`) – Namespace package name.
- **`path`** (`list[Path]`) – Namespace package folder paths.

### name

```
name: str
```

Namespace package name.

### path

```
path: list[Path]
```

Namespace package folder paths.

## **Types**

## NamePartsType

```
NamePartsType = tuple[str, ...]
```

Type alias for the parts of a module name.

## NamePartsAndPathType

```
NamePartsAndPathType = tuple[NamePartsType, Path]
```

Type alias for the parts of a module name and its path.
