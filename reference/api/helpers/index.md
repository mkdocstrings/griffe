# Helpers

## TmpPackage

```
TmpPackage(tmpdir: Path, name: str, path: Path)

```

A temporary package.

The `tmpdir` and `path` parameters can be passed as relative path. They will be resolved to absolute paths after initialization.

Attributes:

- **`name`** (`str`) – The package name, as to dynamically import it.
- **`path`** (`Path`) – The package path.
- **`tmpdir`** (`Path`) – The temporary directory containing the package.

### name

```
name: str

```

The package name, as to dynamically import it.

### path

```
path: Path

```

The package path.

### tmpdir

```
tmpdir: Path

```

The temporary directory containing the package.

## temporary_pyfile

```
temporary_pyfile(
    code: str, *, module_name: str = "module"
) -> Iterator[tuple[str, Path]]

```

Create a Python file containing the given code in a temporary directory.

Parameters:

- ### **`code`**

  (`str`) – The code to write to the temporary file.

- ### **`module_name`**

  (`str`, default: `'module'` ) – The name of the temporary module.

Yields:

- **`module_name`** ( `str` ) – The module name, as to dynamically import it.
- **`module_path`** ( `Path` ) – The module path.

## temporary_pypackage

```
temporary_pypackage(
    package: str,
    modules: Sequence[str]
    | Mapping[str, str]
    | None = None,
    *,
    init: bool = True,
    inits: bool = True,
) -> Iterator[TmpPackage]

```

Create a package containing the given modules in a temporary directory.

Parameters:

- ### **`package`**

  (`str`) – The package name. Example: "a" gives a package named a, while "a/b" gives a namespace package named a with a package inside named b. If init is false, then b is also a namespace package.

- ### **`modules`**

  (`Sequence[str] | Mapping[str, str] | None`, default: `None` ) – Additional modules to create in the package. If a list, simply touch the files: ["b.py", "c/d.py", "e/f"]. If a dict, keys are the file names and values their contents: {"b.py": "b = 1", "c/d.py": "print('hey from c')"}.

- ### **`init`**

  (`bool`, default: `True` ) – Whether to create an __init__ module in the top package.

- ### **`inits`**

  (`bool`, default: `True` ) – Whether to create __init__ modules in subpackages.

Yields:

- `TmpPackage` – A temporary package.

## temporary_visited_module

```
temporary_visited_module(
    code: str,
    *,
    module_name: str = "module",
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> Iterator[Module]

```

Create and visit a temporary module with the given code.

Parameters:

- ### **`code`**

  (`str`) – The code of the module.

- ### **`module_name`**

  (`str`, default: `'module'` ) – The name of the temporary module.

- ### **`extensions`**

  (`Extensions | None`, default: `None` ) – The extensions to use when visiting the AST.

- ### **`parent`**

  (`Module | None`, default: `None` ) – The optional parent of this module.

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. By default, no parsing is done.

- ### **`docstring_options`**

  (`dict[str, Any] | None`, default: `None` ) – Additional docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

Yields:

- `Module` – The visited module.

## temporary_visited_package

```
temporary_visited_package(
    package: str,
    modules: Sequence[str]
    | Mapping[str, str]
    | None = None,
    *,
    init: bool = True,
    inits: bool = True,
    extensions: Extensions | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
    allow_inspection: bool = False,
    store_source: bool = True,
    resolve_aliases: bool = False,
    resolve_external: bool | None = None,
    resolve_implicit: bool = False,
    search_sys_path: bool = False,
) -> Iterator[Module]

```

Create and visit a temporary package.

Parameters:

- ### **`package`**

  (`str`) – The package name. Example: "a" gives a package named a, while "a/b" gives a namespace package named a with a package inside named b. If init is false, then b is also a namespace package.

- ### **`modules`**

  (`Sequence[str] | Mapping[str, str] | None`, default: `None` ) – Additional modules to create in the package. If a list, simply touch the files: ["b.py", "c/d.py", "e/f"]. If a dict, keys are the file names and values their contents: {"b.py": "b = 1", "c/d.py": "print('hey from c')"}.

- ### **`init`**

  (`bool`, default: `True` ) – Whether to create an __init__ module in the top package.

- ### **`inits`**

  (`bool`, default: `True` ) – Whether to create __init__ modules in subpackages.

- ### **`extensions`**

  (`Extensions | None`, default: `None` ) – The extensions to use.

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. By default, no parsing is done.

- ### **`docstring_options`**

  (`dict[str, Any] | None`, default: `None` ) – Additional docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

- ### **`allow_inspection`**

  (`bool`, default: `False` ) – Whether to allow inspecting modules when visiting them is not possible.

- ### **`store_source`**

  (`bool`, default: `True` ) – Whether to store code source in the lines collection.

- ### **`resolve_aliases`**

  (`bool`, default: `False` ) – Whether to resolve aliases.

- ### **`resolve_external`**

  (`bool | None`, default: `None` ) – Whether to try to load unspecified modules to resolve aliases. Default value (None) means to load external modules only if they are the private sibling or the origin module (for example when ast imports from \_ast).

- ### **`resolve_implicit`**

  (`bool`, default: `False` ) – When false, only try to resolve an alias if it is explicitly exported.

- ### **`search_sys_path`**

  (`bool`, default: `False` ) – Whether to search the system paths for the package.

Yields:

- `Module` – A module.

## temporary_inspected_module

```
temporary_inspected_module(
    code: str,
    *,
    module_name: str = "module",
    import_paths: list[Path] | None = None,
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> Iterator[Module]

```

Create and inspect a temporary module with the given code.

Parameters:

- ### **`code`**

  (`str`) – The code of the module.

- ### **`module_name`**

  (`str`, default: `'module'` ) – The name of the temporary module.

- ### **`import_paths`**

  (`list[Path] | None`, default: `None` ) – Paths to import the module from.

- ### **`extensions`**

  (`Extensions | None`, default: `None` ) – The extensions to use when visiting the AST.

- ### **`parent`**

  (`Module | None`, default: `None` ) – The optional parent of this module.

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. By default, no parsing is done.

- ### **`docstring_options`**

  (`dict[str, Any] | None`, default: `None` ) – Additional docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

Yields:

- `Module` – The inspected module.

## temporary_inspected_package

```
temporary_inspected_package(
    package: str,
    modules: Sequence[str]
    | Mapping[str, str]
    | None = None,
    *,
    init: bool = True,
    inits: bool = True,
    extensions: Extensions | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
    allow_inspection: bool = True,
    store_source: bool = True,
    resolve_aliases: bool = False,
    resolve_external: bool | None = None,
    resolve_implicit: bool = False,
    search_sys_path: bool = False,
) -> Iterator[Module]

```

Create and inspect a temporary package.

Parameters:

- ### **`package`**

  (`str`) – The package name. Example: "a" gives a package named a, while "a/b" gives a namespace package named a with a package inside named b. If init is false, then b is also a namespace package.

- ### **`modules`**

  (`Sequence[str] | Mapping[str, str] | None`, default: `None` ) – Additional modules to create in the package. If a list, simply touch the files: ["b.py", "c/d.py", "e/f"]. If a dict, keys are the file names and values their contents: {"b.py": "b = 1", "c/d.py": "print('hey from c')"}.

- ### **`init`**

  (`bool`, default: `True` ) – Whether to create an __init__ module in the top package.

- ### **`inits`**

  (`bool`, default: `True` ) – Whether to create __init__ modules in subpackages.

- ### **`extensions`**

  (`Extensions | None`, default: `None` ) – The extensions to use.

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. By default, no parsing is done.

- ### **`docstring_options`**

  (`dict[str, Any] | None`, default: `None` ) – Additional docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

- ### **`allow_inspection`**

  (`bool`, default: `True` ) – Whether to allow inspecting modules.

- ### **`store_source`**

  (`bool`, default: `True` ) – Whether to store code source in the lines collection.

- ### **`resolve_aliases`**

  (`bool`, default: `False` ) – Whether to resolve aliases.

- ### **`resolve_external`**

  (`bool | None`, default: `None` ) – Whether to try to load unspecified modules to resolve aliases. Default value (None) means to load external modules only if they are the private sibling or the origin module (for example when ast imports from \_ast).

- ### **`resolve_implicit`**

  (`bool`, default: `False` ) – When false, only try to resolve an alias if it is explicitly exported.

- ### **`search_sys_path`**

  (`bool`, default: `False` ) – Whether to search the system paths for the package.

Yields:

- `Module` – A module.

## vtree

```
vtree(
    *objects: Object, return_leaf: bool = False
) -> Object

```

Link objects together, vertically.

Parameters:

- ### **`*objects`**

  (`Object`, default: `()` ) – A sequence of objects. The first one is at the top of the tree.

- ### **`return_leaf`**

  (`bool`, default: `False` ) – Whether to return the leaf instead of the root.

Raises:

- `ValueError` – When no objects are provided.

Returns:

- `Object` – The top or leaf object.

## htree

```
htree(*objects: Object) -> Object

```

Link objects together, horizontally.

Parameters:

- ### **`*objects`**

  (`Object`, default: `()` ) – A sequence of objects. All objects starting at the second become members of the first.

Raises:

- `ValueError` – When no objects are provided.

Returns:

- `Object` – The first given object, with all the other objects as members of it.

## module_vtree

```
module_vtree(
    path: str,
    *,
    leaf_package: bool = True,
    return_leaf: bool = False,
) -> Module

```

Link objects together, vertically.

Parameters:

- ### **`path`**

  (`str`) – The complete module path, like "a.b.c.d".

- ### **`leaf_package`**

  (`bool`, default: `True` ) – Whether the deepest module should also be a package.

- ### **`return_leaf`**

  (`bool`, default: `False` ) – Whether to return the leaf instead of the root.

Raises:

- `ValueError` – When no objects are provided.

Returns:

- `Module` – The top or leaf module.
