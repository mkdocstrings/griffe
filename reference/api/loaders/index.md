# Loaders

## **Main API**

## load

```
load(
    objspec: str | Path | None = None,
    /,
    *,
    submodules: bool = True,
    try_relative_path: bool = True,
    extensions: Extensions | None = None,
    search_paths: Sequence[str | Path] | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: DocstringOptions | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
    allow_inspection: bool = True,
    force_inspection: bool = False,
    store_source: bool = True,
    find_stubs_package: bool = False,
    resolve_aliases: bool = False,
    resolve_external: bool | None = None,
    resolve_implicit: bool = False,
) -> Object | Alias
```

Load and return a Griffe object.

In Griffe's context, loading means:

- searching for a package, and finding it on the file system or as a builtin module (see the ModuleFinder class for more information)
- extracting information from each of its (sub)modules, by either parsing the source code (see the visit function) or inspecting the module at runtime (see the inspect function)

The extracted information is stored in a collection of modules, which can be queried later. Each collected module is a tree of objects, representing the structure of the module. See the Module, Class, Function, Attribute, and TypeAlias classes for more information.

The main class used to load modules is GriffeLoader. Convenience functions like this one and load_git are also available.

Example

```
import griffe

module = griffe.load(...)
```

This is a shortcut for:

```
from griffe import GriffeLoader

loader = GriffeLoader(...)
module = loader.load(...)
```

See the documentation for the loader: GriffeLoader.

Parameters:

- ### **`objspec`**

  (`str | Path | None`, default: `None` ) – The Python path of an object, or file path to a module.

- ### **`submodules`**

  (`bool`, default: `True` ) – Whether to recurse on the submodules. This parameter only makes sense when loading a package (top-level module).

- ### **`try_relative_path`**

  (`bool`, default: `True` ) – Whether to try finding the module as a relative path.

- ### **`extensions`**

  (`Extensions | None`, default: `None` ) – The extensions to use.

- ### **`search_paths`**

  (`Sequence[str | Path] | None`, default: `None` ) – The paths to search into.

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. By default, no parsing is done.

- ### **`docstring_options`**

  (`DocstringOptions | None`, default: `None` ) – Docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

- ### **`allow_inspection`**

  (`bool`, default: `True` ) – Whether to allow inspecting modules when visiting them is not possible.

- ### **`force_inspection`**

  (`bool`, default: `False` ) – Whether to force using dynamic analysis when loading data.

- ### **`store_source`**

  (`bool`, default: `True` ) – Whether to store code source in the lines collection.

- ### **`find_stubs_package`**

  (`bool`, default: `False` ) – Whether to search for stubs-only package. If both the package and its stubs are found, they'll be merged together. If only the stubs are found, they'll be used as the package itself.

- ### **`resolve_aliases`**

  (`bool`, default: `False` ) – Whether to resolve aliases.

- ### **`resolve_external`**

  (`bool | None`, default: `None` ) – Whether to try to load unspecified modules to resolve aliases. Default value (None) means to load external modules only if they are the private sibling or the origin module (for example when ast imports from \_ast).

- ### **`resolve_implicit`**

  (`bool`, default: `False` ) – When false, only try to resolve an alias if it is explicitly exported.

Returns:

- `Object | Alias` – A Griffe object.

## load_git

```
load_git(
    objspec: str | Path | None = None,
    /,
    *,
    ref: str = "HEAD",
    repo: str | Path = ".",
    submodules: bool = True,
    extensions: Extensions | None = None,
    search_paths: Sequence[str | Path] | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: DocstringOptions | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
    allow_inspection: bool = True,
    force_inspection: bool = False,
    find_stubs_package: bool = False,
    resolve_aliases: bool = False,
    resolve_external: bool | None = None,
    resolve_implicit: bool = False,
) -> Object | Alias
```

Load and return a module from a specific Git reference.

This function will create a temporary [git worktree](https://git-scm.com/docs/git-worktree) at the requested reference before loading `module` with griffe.load.

This function requires that the `git` executable is installed.

Examples:

```
from griffe import load_git

old_api = load_git("my_module", ref="v0.1.0", repo="path/to/repo")
```

Parameters:

- ### **`objspec`**

  (`str | Path | None`, default: `None` ) – The Python path of an object, or file path to a module.

- ### **`ref`**

  (`str`, default: `'HEAD'` ) – A Git reference such as a commit, tag or branch.

- ### **`repo`**

  (`str | Path`, default: `'.'` ) – Path to the repository (i.e. the directory containing the .git directory)

- ### **`submodules`**

  (`bool`, default: `True` ) – Whether to recurse on the submodules. This parameter only makes sense when loading a package (top-level module).

- ### **`extensions`**

  (`Extensions | None`, default: `None` ) – The extensions to use.

- ### **`search_paths`**

  (`Sequence[str | Path] | None`, default: `None` ) – The paths to search into (relative to the repository root).

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. By default, no parsing is done.

- ### **`docstring_options`**

  (`DocstringOptions | None`, default: `None` ) – Docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

- ### **`allow_inspection`**

  (`bool`, default: `True` ) – Whether to allow inspecting modules when visiting them is not possible.

- ### **`force_inspection`**

  (`bool`, default: `False` ) – Whether to force using dynamic analysis when loading data.

- ### **`find_stubs_package`**

  (`bool`, default: `False` ) – Whether to search for stubs-only package. If both the package and its stubs are found, they'll be merged together. If only the stubs are found, they'll be used as the package itself.

- ### **`resolve_aliases`**

  (`bool`, default: `False` ) – Whether to resolve aliases.

- ### **`resolve_external`**

  (`bool | None`, default: `None` ) – Whether to try to load unspecified modules to resolve aliases. Default value (None) means to load external modules only if they are the private sibling or the origin module (for example when ast imports from \_ast).

- ### **`resolve_implicit`**

  (`bool`, default: `False` ) – When false, only try to resolve an alias if it is explicitly exported.

Returns:

- `Object | Alias` – A Griffe object.

## load_pypi

```
load_pypi(
    package: str,
    distribution: str,
    version_spec: str,
    *,
    submodules: bool = True,
    extensions: Extensions | None = None,
    search_paths: Sequence[str | Path] | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: DocstringOptions | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
    allow_inspection: bool = True,
    force_inspection: bool = False,
    find_stubs_package: bool = False,
    resolve_aliases: bool = False,
    resolve_external: bool | None = None,
    resolve_implicit: bool = False,
) -> Object | Alias
```

Load and return a module from a specific package version downloaded using pip.

[Sponsors only](../../../insiders/) — [Insiders 1.1.0](../../../insiders/changelog/#1.1.0).

Parameters:

- ### **`package`**

  (`str`) – The package import name.

- ### **`distribution`**

  (`str`) – The distribution name.

- ### **`version_spec`**

  (`str`) – The version specifier to use when installing with pip.

- ### **`submodules`**

  (`bool`, default: `True` ) – Whether to recurse on the submodules. This parameter only makes sense when loading a package (top-level module).

- ### **`extensions`**

  (`Extensions | None`, default: `None` ) – The extensions to use.

- ### **`search_paths`**

  (`Sequence[str | Path] | None`, default: `None` ) – The paths to search into (relative to the repository root).

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. By default, no parsing is done.

- ### **`docstring_options`**

  (`DocstringOptions | None`, default: `None` ) – Docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

- ### **`allow_inspection`**

  (`bool`, default: `True` ) – Whether to allow inspecting modules when visiting them is not possible.

- ### **`force_inspection`**

  (`bool`, default: `False` ) – Whether to force using dynamic analysis when loading data.

- ### **`find_stubs_package`**

  (`bool`, default: `False` ) – Whether to search for stubs-only package. If both the package and its stubs are found, they'll be merged together. If only the stubs are found, they'll be used as the package itself.

- ### **`resolve_aliases`**

  (`bool`, default: `False` ) – Whether to resolve aliases.

- ### **`resolve_external`**

  (`bool | None`, default: `None` ) – Whether to try to load unspecified modules to resolve aliases. Default value (None) means to load external modules only if they are the private sibling or the origin module (for example when ast imports from \_ast).

- ### **`resolve_implicit`**

  (`bool`, default: `False` ) – When false, only try to resolve an alias if it is explicitly exported.

## **Advanced API**

## GriffeLoader

```
GriffeLoader(
    *,
    extensions: Extensions | None = None,
    search_paths: Sequence[str | Path] | None = None,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: DocstringOptions | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
    allow_inspection: bool = True,
    force_inspection: bool = False,
    store_source: bool = True,
)
```

The Griffe loader, allowing to load data from modules.

Parameters:

- ### **`extensions`**

  (`Extensions | None`, default: `None` ) – The extensions to use.

- ### **`search_paths`**

  (`Sequence[str | Path] | None`, default: `None` ) – The paths to search into.

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. By default, no parsing is done.

- ### **`docstring_options`**

  (`DocstringOptions | None`, default: `None` ) – Docstring parsing options.

- ### **`lines_collection`**

  (`LinesCollection | None`, default: `None` ) – A collection of source code lines.

- ### **`modules_collection`**

  (`ModulesCollection | None`, default: `None` ) – A collection of modules.

- ### **`allow_inspection`**

  (`bool`, default: `True` ) – Whether to allow inspecting modules when visiting them is not possible.

- ### **`store_source`**

  (`bool`, default: `True` ) – Whether to store code source in the lines collection.

Methods:

- **`expand_exports`** – Expand exports: try to recursively expand all module exports (__all__ values).
- **`expand_wildcards`** – Expand wildcards: try to recursively expand all found wildcards.
- **`load`** – Load an object as a Griffe object, given its Python or file path.
- **`resolve_aliases`** – Resolve aliases.
- **`resolve_module_aliases`** – Follow aliases: try to recursively resolve all found aliases.
- **`stats`** – Compute some statistics.

Attributes:

- **`allow_inspection`** (`bool`) – Whether to allow inspecting (importing) modules for which we can't find sources.
- **`docstring_options`** (`DocstringOptions`) – Configured parsing options.
- **`docstring_parser`** (`DocstringStyle | Parser | None`) – Selected docstring parser.
- **`extensions`** (`Extensions`) – Loaded Griffe extensions.
- **`finder`** (`ModuleFinder`) – The module source finder.
- **`force_inspection`** (`bool`) – Whether to force inspecting (importing) modules, even when sources were found.
- **`ignored_modules`** (`set[str]`) – Special modules to ignore when loading.
- **`lines_collection`** (`LinesCollection`) – Collection of source code lines.
- **`modules_collection`** (`ModulesCollection`) – Collection of modules.
- **`store_source`** (`bool`) – Whether to store source code in the lines collection.

### allow_inspection

```
allow_inspection: bool = allow_inspection
```

Whether to allow inspecting (importing) modules for which we can't find sources.

### docstring_options

```
docstring_options: DocstringOptions = (
    docstring_options or {}
)
```

Configured parsing options.

### docstring_parser

```
docstring_parser: DocstringStyle | Parser | None = (
    docstring_parser
)
```

Selected docstring parser.

### extensions

```
extensions: Extensions = extensions or load_extensions()
```

Loaded Griffe extensions.

### finder

```
finder: ModuleFinder = ModuleFinder(search_paths)
```

The module source finder.

### force_inspection

```
force_inspection: bool = force_inspection
```

Whether to force inspecting (importing) modules, even when sources were found.

### ignored_modules

```
ignored_modules: set[str] = {'debugpy', '_pydev'}
```

Special modules to ignore when loading.

For example, `debugpy` and `_pydev` are used when debugging with VSCode and should generally never be loaded.

### lines_collection

```
lines_collection: LinesCollection = (
    lines_collection or LinesCollection()
)
```

Collection of source code lines.

### modules_collection

```
modules_collection: ModulesCollection = (
    modules_collection or ModulesCollection()
)
```

Collection of modules.

### store_source

```
store_source: bool = store_source
```

Whether to store source code in the lines collection.

### expand_exports

```
expand_exports(
    module: Module, seen: set | None = None
) -> None
```

Expand exports: try to recursively expand all module exports (`__all__` values).

See also: Module.exports.

Parameters:

- #### **`module`**

  (`Module`) – The module to recurse on.

- #### **`seen`**

  (`set | None`, default: `None` ) – Used to avoid infinite recursion.

### expand_wildcards

```
expand_wildcards(
    obj: Object,
    *,
    external: bool | None = None,
    seen: set | None = None,
) -> None
```

Expand wildcards: try to recursively expand all found wildcards.

See also: Alias.wildcard.

Parameters:

- #### **`obj`**

  (`Object`) – The object and its members to recurse on.

- #### **`external`**

  (`bool | None`, default: `None` ) – When true, try to load unspecified modules to expand wildcards.

- #### **`seen`**

  (`set | None`, default: `None` ) – Used to avoid infinite recursion.

### load

```
load(
    objspec: str | Path | None = None,
    /,
    *,
    submodules: bool = True,
    try_relative_path: bool = True,
    find_stubs_package: bool = False,
) -> Object | Alias
```

Load an object as a Griffe object, given its Python or file path.

Note that this will load the whole object's package, and return only the specified object. The rest of the package can be accessed from the returned object with regular methods and properties (`parent`, `members`, etc.).

Examples:

```
>>> loader.load("griffe.Module")
Alias("Module", "griffe._internal.models.Module")
```

Parameters:

- #### **`objspec`**

  (`str | Path | None`, default: `None` ) – The Python path of an object, or file path to a module.

- #### **`submodules`**

  (`bool`, default: `True` ) – Whether to recurse on the submodules. This parameter only makes sense when loading a package (top-level module).

- #### **`try_relative_path`**

  (`bool`, default: `True` ) – Whether to try finding the module as a relative path.

- #### **`find_stubs_package`**

  (`bool`, default: `False` ) – Whether to search for stubs-only package. If both the package and its stubs are found, they'll be merged together. If only the stubs are found, they'll be used as the package itself.

Raises:

- `LoadingError` – When loading a module failed for various reasons.
- `ModuleNotFoundError` – When a module was not found and inspection is disallowed.

Returns:

- `Object | Alias` – A Griffe object.

### resolve_aliases

```
resolve_aliases(
    *,
    implicit: bool = False,
    external: bool | None = None,
    max_iterations: int | None = None,
) -> tuple[set[str], int]
```

Resolve aliases.

Parameters:

- #### **`implicit`**

  (`bool`, default: `False` ) – When false, only try to resolve an alias if it is explicitly exported.

- #### **`external`**

  (`bool | None`, default: `None` ) – When false, don't try to load unspecified modules to resolve aliases.

- #### **`max_iterations`**

  (`int | None`, default: `None` ) – Maximum number of iterations on the loader modules collection.

Returns:

- `tuple[set[str], int]` – The unresolved aliases and the number of iterations done.

### resolve_module_aliases

```
resolve_module_aliases(
    obj: Object | Alias,
    *,
    implicit: bool = False,
    external: bool | None = None,
    seen: set[str] | None = None,
    load_failures: set[str] | None = None,
) -> tuple[set[str], set[str]]
```

Follow aliases: try to recursively resolve all found aliases.

Parameters:

- #### **`obj`**

  (`Object | Alias`) – The object and its members to recurse on.

- #### **`implicit`**

  (`bool`, default: `False` ) – When false, only try to resolve an alias if it is explicitly exported.

- #### **`external`**

  (`bool | None`, default: `None` ) – When false, don't try to load unspecified modules to resolve aliases.

- #### **`seen`**

  (`set[str] | None`, default: `None` ) – Used to avoid infinite recursion.

- #### **`load_failures`**

  (`set[str] | None`, default: `None` ) – Set of external packages we failed to load (to prevent retries).

Returns:

- `tuple[set[str], set[str]]` – Both sets of resolved and unresolved aliases.

### stats

```
stats() -> Stats
```

Compute some statistics.

Returns:

- `Stats` – Some statistics.

## ModulesCollection

```
ModulesCollection()
```

Bases: `GetMembersMixin`, `SetMembersMixin`, `DelMembersMixin`

```
              flowchart TD
              griffe.ModulesCollection[ModulesCollection]
              griffe._internal.mixins.GetMembersMixin[GetMembersMixin]
              griffe._internal.mixins.SetMembersMixin[SetMembersMixin]
              griffe._internal.mixins.DelMembersMixin[DelMembersMixin]

                              griffe._internal.mixins.GetMembersMixin --> griffe.ModulesCollection
                
                griffe._internal.mixins.SetMembersMixin --> griffe.ModulesCollection
                
                griffe._internal.mixins.DelMembersMixin --> griffe.ModulesCollection
                


              click griffe.ModulesCollection href "" "griffe.ModulesCollection"
              click griffe._internal.mixins.GetMembersMixin href "" "griffe._internal.mixins.GetMembersMixin"
              click griffe._internal.mixins.SetMembersMixin href "" "griffe._internal.mixins.SetMembersMixin"
              click griffe._internal.mixins.DelMembersMixin href "" "griffe._internal.mixins.DelMembersMixin"
```

A collection of modules, allowing easy access to members.

Initialize the collection.

Methods:

- **`__bool__`** – A modules collection is always true-ish.
- **`__contains__`** – Check if a module is in the collection.
- **`__delitem__`** – Delete a member with its name or path.
- **`__getitem__`** – Get a member with its name or path.
- **`__setitem__`** – Set a member with its name or path.
- **`del_member`** – Delete a member with its name or path.
- **`get_member`** – Get a member with its name or path.
- **`set_member`** – Set a member with its name or path.

Attributes:

- **`all_members`** (`dict[str, Module]`) – Members of the collection.
- **`is_collection`** – Marked as collection to distinguish from objects.
- **`members`** (`dict[str, Module]`) – Members (modules) of the collection.

### all_members

```
all_members: dict[str, Module]
```

Members of the collection.

This property is overwritten to simply return `self.members`, as `all_members` does not make sense for a modules collection.

### is_collection

```
is_collection = True
```

Marked as collection to distinguish from objects.

### members

```
members: dict[str, Module] = {}
```

Members (modules) of the collection.

### __bool__

```
__bool__() -> bool
```

A modules collection is always true-ish.

### __contains__

```
__contains__(item: Any) -> bool
```

Check if a module is in the collection.

### __delitem__

```
__delitem__(key: str | Sequence[str]) -> None
```

Delete a member with its name or path.

This method is part of the consumer API: do not use when producing Griffe trees!

Members will be looked up in both declared members and inherited ones, triggering computation of the latter.

Parameters:

- #### **`key`**

  (`str | Sequence[str]`) – The name or path of the member.

Examples:

```
>>> del griffe_object["foo"]
>>> del griffe_object["path.to.bar"]
>>> del griffe_object[("path", "to", "qux")]
```

### __getitem__

```
__getitem__(key: str | Sequence[str]) -> Any
```

Get a member with its name or path.

This method is part of the consumer API: do not use when producing Griffe trees!

Members will be looked up in both declared members and inherited ones, triggering computation of the latter.

Parameters:

- #### **`key`**

  (`str | Sequence[str]`) – The name or path of the member.

Examples:

```
>>> foo = griffe_object["foo"]
>>> bar = griffe_object["path.to.bar"]
>>> qux = griffe_object[("path", "to", "qux")]
```

### __setitem__

```
__setitem__(
    key: str | Sequence[str], value: Object | Alias
) -> None
```

Set a member with its name or path.

This method is part of the consumer API: do not use when producing Griffe trees!

Parameters:

- #### **`key`**

  (`str | Sequence[str]`) – The name or path of the member.

- #### **`value`**

  (`Object | Alias`) – The member.

Examples:

```
>>> griffe_object["foo"] = foo
>>> griffe_object["path.to.bar"] = bar
>>> griffe_object[("path", "to", "qux")] = qux
```

### del_member

```
del_member(key: str | Sequence[str]) -> None
```

Delete a member with its name or path.

This method is part of the producer API: you can use it safely while building Griffe trees (for example in Griffe extensions).

Members will be looked up in declared members only, not inherited ones.

Parameters:

- #### **`key`**

  (`str | Sequence[str]`) – The name or path of the member.

Examples:

```
>>> griffe_object.del_member("foo")
>>> griffe_object.del_member("path.to.bar")
>>> griffe_object.del_member(("path", "to", "qux"))
```

### get_member

```
get_member(key: str | Sequence[str]) -> Any
```

Get a member with its name or path.

This method is part of the producer API: you can use it safely while building Griffe trees (for example in Griffe extensions).

Members will be looked up in declared members only, not inherited ones.

Parameters:

- #### **`key`**

  (`str | Sequence[str]`) – The name or path of the member.

Examples:

```
>>> foo = griffe_object["foo"]
>>> bar = griffe_object["path.to.bar"]
>>> bar = griffe_object[("path", "to", "bar")]
```

### set_member

```
set_member(
    key: str | Sequence[str], value: Object | Alias
) -> None
```

Set a member with its name or path.

This method is part of the producer API: you can use it safely while building Griffe trees (for example in Griffe extensions).

Parameters:

- #### **`key`**

  (`str | Sequence[str]`) – The name or path of the member.

- #### **`value`**

  (`Object | Alias`) – The member.

Examples:

```
>>> griffe_object.set_member("foo", foo)
>>> griffe_object.set_member("path.to.bar", bar)
>>> griffe_object.set_member(("path", "to", "qux"), qux)
```

## LinesCollection

```
LinesCollection()
```

A simple dictionary containing the modules source code lines.

Initialize the collection.

Methods:

- **`__bool__`** – A lines collection is always true-ish.
- **`__contains__`** – Check if a file path is in the collection.
- **`__getitem__`** – Get the lines of a file path.
- **`__setitem__`** – Set the lines of a file path.
- **`items`** – Return the collection items.
- **`keys`** – Return the collection keys.
- **`values`** – Return the collection values.

### __bool__

```
__bool__() -> bool
```

A lines collection is always true-ish.

### __contains__

```
__contains__(item: Path) -> bool
```

Check if a file path is in the collection.

### __getitem__

```
__getitem__(key: Path) -> list[str]
```

Get the lines of a file path.

### __setitem__

```
__setitem__(key: Path, value: list[str]) -> None
```

Set the lines of a file path.

### items

```
items() -> ItemsView
```

Return the collection items.

Returns:

- `ItemsView` – The collection items.

### keys

```
keys() -> KeysView
```

Return the collection keys.

Returns:

- `KeysView` – The collection keys.

### values

```
values() -> ValuesView
```

Return the collection values.

Returns:

- `ValuesView` – The collection values.

## **Additional API**

## Stats

```
Stats(loader: GriffeLoader)
```

Load statistics for a Griffe loader.

Parameters:

- ### **`loader`**

  (`GriffeLoader`) – The loader to compute stats for.

Methods:

- **`as_text`** – Format the statistics as text.

Attributes:

- **`by_kind`** – Number of objects by kind.
- **`lines`** – Total number of lines.
- **`loader`** – The loader to compute stats for.
- **`modules_by_extension`** – Number of modules by extension.
- **`packages`** – Number of packages.
- **`time_spent_inspecting`** – Time spent inspecting modules.
- **`time_spent_serializing`** – Time spent serializing objects.
- **`time_spent_visiting`** – Time spent visiting modules.

### by_kind

```
by_kind = {
    MODULE: 0,
    CLASS: 0,
    FUNCTION: 0,
    ATTRIBUTE: 0,
    TYPE_ALIAS: 0,
}
```

Number of objects by kind.

### lines

```
lines = sum((len(lines)) for lines in (values()))
```

Total number of lines.

### loader

```
loader = loader
```

The loader to compute stats for.

### modules_by_extension

```
modules_by_extension = modules_by_extension
```

Number of modules by extension.

### packages

```
packages = len(top_modules)
```

Number of packages.

### time_spent_inspecting

```
time_spent_inspecting = 0
```

Time spent inspecting modules.

### time_spent_serializing

```
time_spent_serializing = 0
```

Time spent serializing objects.

### time_spent_visiting

```
time_spent_visiting = 0
```

Time spent visiting modules.

### as_text

```
as_text() -> str
```

Format the statistics as text.

Returns:

- `str` – Text stats.

## merge_stubs

```
merge_stubs(mod1: Module, mod2: Module) -> Module
```

Merge stubs into a module.

Parameters:

- ### **`mod1`**

  (`Module`) – A regular module or stubs module.

- ### **`mod2`**

  (`Module`) – A regular module or stubs module.

Raises:

- `ValueError` – When both modules are regular modules (no stubs is passed).

Returns:

- `Module` – The regular module.
