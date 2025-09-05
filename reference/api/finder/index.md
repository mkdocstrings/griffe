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
