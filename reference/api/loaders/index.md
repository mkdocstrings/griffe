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

Source code in `packages/griffelib/src/griffe/_internal/loader.py`

````
def load(
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
) -> Object | Alias:
    """Load and return a Griffe object.

    In Griffe's context, loading means:

    - searching for a package, and finding it on the file system or as a builtin module
        (see the [`ModuleFinder`][griffe.ModuleFinder] class for more information)
    - extracting information from each of its (sub)modules, by either parsing
        the source code (see the [`visit`][griffe.visit] function)
        or inspecting the module at runtime (see the [`inspect`][griffe.inspect] function)

    The extracted information is stored in a collection of modules, which can be queried later.
    Each collected module is a tree of objects, representing the structure of the module.
    See the [`Module`][griffe.Module], [`Class`][griffe.Class],
    [`Function`][griffe.Function], [`Attribute`][griffe.Attribute], and
    [`TypeAlias`][griffe.TypeAlias] classes for more information.

    The main class used to load modules is [`GriffeLoader`][griffe.GriffeLoader].
    Convenience functions like this one and [`load_git`][griffe.load_git] are also available.

    Example:
        ```python
        import griffe

        module = griffe.load(...)
        ```

        This is a shortcut for:

        ```python
        from griffe import GriffeLoader

        loader = GriffeLoader(...)
        module = loader.load(...)
        ```

        See the documentation for the loader: [`GriffeLoader`][griffe.GriffeLoader].

    Parameters:
        objspec: The Python path of an object, or file path to a module.
        submodules: Whether to recurse on the submodules.
            This parameter only makes sense when loading a package (top-level module).
        try_relative_path: Whether to try finding the module as a relative path.
        extensions: The extensions to use.
        search_paths: The paths to search into.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.
        allow_inspection: Whether to allow inspecting modules when visiting them is not possible.
        force_inspection: Whether to force using dynamic analysis when loading data.
        store_source: Whether to store code source in the lines collection.
        find_stubs_package: Whether to search for stubs-only package.
            If both the package and its stubs are found, they'll be merged together.
            If only the stubs are found, they'll be used as the package itself.
        resolve_aliases: Whether to resolve aliases.
        resolve_external: Whether to try to load unspecified modules to resolve aliases.
            Default value (`None`) means to load external modules only if they are the private sibling
            or the origin module (for example when `ast` imports from `_ast`).
        resolve_implicit: When false, only try to resolve an alias if it is explicitly exported.

    Returns:
        A Griffe object.
    """
    loader = GriffeLoader(
        extensions=extensions,
        search_paths=search_paths,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        lines_collection=lines_collection,
        modules_collection=modules_collection,
        allow_inspection=allow_inspection,
        force_inspection=force_inspection,
        store_source=store_source,
    )
    result = loader.load(
        objspec,
        submodules=submodules,
        try_relative_path=try_relative_path,
        find_stubs_package=find_stubs_package,
    )
    if resolve_aliases:
        loader.resolve_aliases(implicit=resolve_implicit, external=resolve_external)
    return result
````

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

Source code in `packages/griffelib/src/griffe/_internal/loader.py`

````
def load_git(
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
) -> Object | Alias:
    """Load and return a module from a specific Git reference.

    This function will create a temporary
    [git worktree](https://git-scm.com/docs/git-worktree) at the requested reference
    before loading `module` with [`griffe.load`][griffe.load].

    This function requires that the `git` executable is installed.

    Examples:
        ```python
        from griffe import load_git

        old_api = load_git("my_module", ref="v0.1.0", repo="path/to/repo")
        ```

    Parameters:
        objspec: The Python path of an object, or file path to a module.
        ref: A Git reference such as a commit, tag or branch.
        repo: Path to the repository (i.e. the directory *containing* the `.git` directory)
        submodules: Whether to recurse on the submodules.
            This parameter only makes sense when loading a package (top-level module).
        extensions: The extensions to use.
        search_paths: The paths to search into (relative to the repository root).
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.
        allow_inspection: Whether to allow inspecting modules when visiting them is not possible.
        force_inspection: Whether to force using dynamic analysis when loading data.
        find_stubs_package: Whether to search for stubs-only package.
            If both the package and its stubs are found, they'll be merged together.
            If only the stubs are found, they'll be used as the package itself.
        resolve_aliases: Whether to resolve aliases.
        resolve_external: Whether to try to load unspecified modules to resolve aliases.
            Default value (`None`) means to load external modules only if they are the private sibling
            or the origin module (for example when `ast` imports from `_ast`).
        resolve_implicit: When false, only try to resolve an alias if it is explicitly exported.

    Returns:
        A Griffe object.
    """
    with _tmp_worktree(repo, ref) as worktree:
        search_paths = [worktree / path for path in search_paths or ["."]]
        if isinstance(objspec, Path):
            objspec = worktree / objspec

        return load(
            objspec,
            submodules=submodules,
            try_relative_path=False,
            extensions=extensions,
            search_paths=search_paths,
            docstring_parser=docstring_parser,
            docstring_options=docstring_options,
            lines_collection=lines_collection,
            modules_collection=modules_collection,
            allow_inspection=allow_inspection,
            force_inspection=force_inspection,
            find_stubs_package=find_stubs_package,
            resolve_aliases=resolve_aliases,
            resolve_external=resolve_external,
            resolve_implicit=resolve_implicit,
        )
````

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

Source code in `packages/griffelib/src/griffe/_internal/loader.py`

```
def load_pypi(
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
) -> Object | Alias:
    """Load and return a module from a specific package version downloaded using pip.

    Parameters:
        package: The package import name.
        distribution: The distribution name.
        version_spec: The version specifier to use when installing with pip.
        submodules: Whether to recurse on the submodules.
            This parameter only makes sense when loading a package (top-level module).
        extensions: The extensions to use.
        search_paths: The paths to search into (relative to the repository root).
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.
        allow_inspection: Whether to allow inspecting modules when visiting them is not possible.
        force_inspection: Whether to force using dynamic analysis when loading data.
        find_stubs_package: Whether to search for stubs-only package.
            If both the package and its stubs are found, they'll be merged together.
            If only the stubs are found, they'll be used as the package itself.
        resolve_aliases: Whether to resolve aliases.
        resolve_external: Whether to try to load unspecified modules to resolve aliases.
            Default value (`None`) means to load external modules only if they are the private sibling
            or the origin module (for example when `ast` imports from `_ast`).
        resolve_implicit: When false, only try to resolve an alias if it is explicitly exported.
    """
    if not all(find_spec(pkg) for pkg in ("pip", "wheel", "platformdirs")):
        raise RuntimeError("Please install Griffe with the 'pypi' extra to use this feature.")

    import platformdirs  # noqa: PLC0415

    pypi_cache_dir = Path(platformdirs.user_cache_dir("griffe"))
    install_dir = pypi_cache_dir / f"{distribution}{version_spec}"
    if install_dir.exists():
        logger.debug("Using cached %s%s", distribution, version_spec)
    else:
        with tempfile.TemporaryDirectory(dir=pypi_cache_dir) as tmpdir:
            install_dir = Path(tmpdir) / distribution
            logger.debug("Downloading %s%s", distribution, version_spec)
            process = subprocess.run(  # noqa: S603
                [
                    sys.executable,
                    "-mpip",
                    "install",
                    "--no-deps",
                    "--no-compile",
                    "--no-warn-script-location",
                    "--no-input",
                    "--disable-pip-version-check",
                    "--no-python-version-warning",
                    "-t",
                    str(install_dir),
                    f"{distribution}{version_spec}",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if process.returncode:
                logger.error(process.stdout)
                raise RuntimeError(f"Could not pip install {distribution}{version_spec}")
            logger.debug(process.stdout)
            shutil.rmtree(install_dir / "bin", ignore_errors=True)
            re_dist = re.sub("[._-]", "[._-]", distribution)
            version = next(
                match.group(1)
                for file in install_dir.iterdir()
                if (match := re.match(rf"{re_dist}-(.+)\.dist-info", file.name, re.IGNORECASE))
            )
            dest_dir = pypi_cache_dir / f"{distribution}=={version}"
            if not dest_dir.exists():
                install_dir.rename(dest_dir)
            install_dir = dest_dir

    if not package:
        files = sorted((file.name.lower() for file in install_dir.iterdir()), reverse=True)
        name = distribution.lower().replace("-", "_")
        if name in files or f"{name}.py" in files:
            package = name
        elif len(files) == 1:
            raise RuntimeError(f"No package found in {distribution}=={version}")
        else:
            try:
                package = next(file.split(".", 1)[0] for file in files if not file.endswith(".dist-info"))
            except StopIteration:
                raise RuntimeError(f"Could not guess package name for {distribution}=={version} (files; {files})")  # noqa: B904

    return load(
        package,
        submodules=submodules,
        try_relative_path=False,
        extensions=extensions,
        search_paths=[install_dir, *(search_paths or ())],
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        lines_collection=lines_collection,
        modules_collection=modules_collection,
        allow_inspection=allow_inspection,
        force_inspection=force_inspection,
        find_stubs_package=find_stubs_package,
        resolve_aliases=resolve_aliases,
        resolve_external=resolve_external,
        resolve_implicit=resolve_implicit,
    )
```

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

Source code in `packages/griffelib/src/griffe/_internal/loader.py`

```
def __init__(
    self,
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
) -> None:
    """Initialize the loader.

    Parameters:
        extensions: The extensions to use.
        search_paths: The paths to search into.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.
        allow_inspection: Whether to allow inspecting modules when visiting them is not possible.
        store_source: Whether to store code source in the lines collection.
    """
    self.extensions: Extensions = extensions or load_extensions()
    """Loaded Griffe extensions."""
    self.docstring_parser: DocstringStyle | Parser | None = docstring_parser
    """Selected docstring parser."""
    self.docstring_options: DocstringOptions = docstring_options or {}
    """Configured parsing options."""
    self.lines_collection: LinesCollection = lines_collection or LinesCollection()
    """Collection of source code lines."""
    self.modules_collection: ModulesCollection = modules_collection or ModulesCollection()
    """Collection of modules."""
    self.allow_inspection: bool = allow_inspection
    """Whether to allow inspecting (importing) modules for which we can't find sources."""
    self.force_inspection: bool = force_inspection
    """Whether to force inspecting (importing) modules, even when sources were found."""
    self.store_source: bool = store_source
    """Whether to store source code in the lines collection."""
    self._search_paths: Sequence[str | Path] | None = search_paths
    self._time_stats: dict = {
        "time_spent_visiting": 0,
        "time_spent_inspecting": 0,
    }
```

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
finder: ModuleFinder
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

Source code in `packages/griffelib/src/griffe/_internal/loader.py`

```
def expand_exports(self, module: Module, seen: set | None = None) -> None:
    """Expand exports: try to recursively expand all module exports (`__all__` values).

    See also: [`Module.exports`][griffe.Module.exports].

    Parameters:
        module: The module to recurse on.
        seen: Used to avoid infinite recursion.
    """
    seen = seen or set()
    seen.add(module.path)
    if module.exports is None:
        return

    expanded = []
    for export in module.exports:
        # It's a name: we resolve it, get the module it comes from,
        # recurse into it, and add its exports to the current ones.
        if isinstance(export, ExprName):
            module_path = export.canonical_path.rsplit(".", 1)[0]  # Remove trailing `.__all__`.
            try:
                next_module = self.modules_collection.get_member(module_path)
            except KeyError:
                logger.debug("Cannot expand '%s', try pre-loading corresponding package", export.canonical_path)
                continue
            if next_module.path not in seen:
                self.expand_exports(next_module, seen)
            try:
                expanded += [export for export in next_module.exports if export not in expanded]
            except TypeError:
                logger.warning("Unsupported item in %s.__all__: %s (use strings only)", module.path, export)
        # It's a string, simply add it to the current exports.
        else:
            expanded.append(export)
    module.exports = expanded

    # Make sure to expand exports in all modules.
    for submodule in module.modules.values():
        if not submodule.is_alias and submodule.path not in seen:
            self.expand_exports(submodule, seen)
```

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

Source code in `packages/griffelib/src/griffe/_internal/loader.py`

```
def expand_wildcards(
    self,
    obj: Object,
    *,
    external: bool | None = None,
    seen: set | None = None,
) -> None:
    """Expand wildcards: try to recursively expand all found wildcards.

    See also: [`Alias.wildcard`][griffe.Alias.wildcard].

    Parameters:
        obj: The object and its members to recurse on.
        external: When true, try to load unspecified modules to expand wildcards.
        seen: Used to avoid infinite recursion.
    """
    expanded = []
    to_remove = []
    seen = seen or set()
    seen.add(obj.path)

    # First we expand wildcard imports and store the objects in a temporary `expanded` variable,
    # while also keeping track of the members representing wildcard import, to remove them later.
    for member in obj.members.values():
        # Handle a wildcard.
        if member.is_alias and member.wildcard:  # ty:ignore[possibly-missing-attribute]
            package = member.wildcard.split(".", 1)[0]  # ty:ignore[possibly-missing-attribute]
            not_loaded = obj.package.path != package and package not in self.modules_collection

            # Try loading the (unknown) package containing the wildcard importe module (if allowed to).
            if not_loaded:
                if external is False or (external is None and package != f"_{obj.package.name}"):
                    continue
                try:
                    self.load(package, try_relative_path=False)
                except (ImportError, LoadingError) as error:
                    logger.debug("Could not expand wildcard import %s in %s: %s", member.name, obj.path, error)
                    continue

            # Try getting the module from which every public object is imported.
            try:
                target = self.modules_collection.get_member(member.target_path)  # ty:ignore[possibly-missing-attribute]
            except KeyError:
                logger.debug(
                    "Could not expand wildcard import %s in %s: %s not found in modules collection",
                    member.name,
                    obj.path,
                    cast("Alias", member).target_path,
                )
                continue

            # Recurse into this module, expanding wildcards there before collecting everything.
            if target.path not in seen:
                try:
                    self.expand_wildcards(target, external=external, seen=seen)
                except (AliasResolutionError, CyclicAliasError) as error:
                    logger.debug("Could not expand wildcard import %s in %s: %s", member.name, obj.path, error)
                    continue

            # Collect every imported object.
            expanded.extend(self._expand_wildcard(member))  # ty:ignore[invalid-argument-type]
            to_remove.append(member.name)

        # Recurse in unseen submodules.
        elif not member.is_alias and member.is_module and member.path not in seen:
            self.expand_wildcards(member, external=external, seen=seen)  # ty:ignore[invalid-argument-type]

    # Then we remove the members representing wildcard imports.
    for name in to_remove:
        obj.del_member(name)

    # Finally we process the collected objects.
    for new_member, alias_lineno, alias_endlineno in expanded:
        overwrite = False
        already_present = new_member.name in obj.members
        self_alias = (
            new_member.is_alias and cast("Alias", new_member).target_path == f"{obj.path}.{new_member.name}"
        )

        # If a member with the same name is already present in the current object,
        # we only overwrite it if the alias is imported lower in the module
        # (meaning that the alias takes precedence at runtime).
        if already_present:
            old_member = obj.get_member(new_member.name)
            old_lineno = old_member.alias_lineno if old_member.is_alias else old_member.lineno
            overwrite = alias_lineno > (old_lineno or 0)

        # 1. If the expanded member is an alias with a target path equal to its own path, we stop.
        #    This situation can arise because of Griffe's mishandling of (abusive) wildcard imports.
        #    We have yet to check how Python handles this itself, or if there's an algorithm
        #    that we could follow to untangle back-and-forth wildcard imports.
        # 2. If the expanded member was already present and we decided not to overwrite it, we stop.
        # 3. Otherwise we proceed further.
        if not self_alias and (not already_present or overwrite):
            alias = Alias(
                new_member.name,
                new_member,
                lineno=alias_lineno,
                endlineno=alias_endlineno,
                parent=obj,  # ty:ignore[invalid-argument-type]
                wildcard_imported=True,
            )
            # Special case: we avoid overwriting a submodule with an alias.
            # Griffe suffers from this limitation where an object cannot store both
            # a submodule and a member of the same name, while this poses (almost) no issue in Python.
            # We always give precedence to the submodule.
            # See the "avoid member-submodule name shadowing" section in the "Python code" docs page.
            if already_present:
                prev_member = obj.get_member(new_member.name)
                with suppress(AliasResolutionError, CyclicAliasError):
                    if prev_member.is_module:
                        continue

            # Everything went right (supposedly), we add the alias as a member of the current object.
            obj.set_member(new_member.name, alias)
```

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

Source code in `packages/griffelib/src/griffe/_internal/loader.py`

```
def load(
    self,
    objspec: str | Path | None = None,
    /,
    *,
    submodules: bool = True,
    try_relative_path: bool = True,
    find_stubs_package: bool = False,
) -> Object | Alias:
    """Load an object as a Griffe object, given its Python or file path.

    Note that this will load the whole object's package,
    and return only the specified object.
    The rest of the package can be accessed from the returned object
    with regular methods and properties (`parent`, `members`, etc.).

    Examples:
        >>> loader.load("griffe.Module")
        Alias("Module", "griffe._internal.models.Module")

    Parameters:
        objspec: The Python path of an object, or file path to a module.
        submodules: Whether to recurse on the submodules.
            This parameter only makes sense when loading a package (top-level module).
        try_relative_path: Whether to try finding the module as a relative path.
        find_stubs_package: Whether to search for stubs-only package.
            If both the package and its stubs are found, they'll be merged together.
            If only the stubs are found, they'll be used as the package itself.

    Raises:
        LoadingError: When loading a module failed for various reasons.
        ModuleNotFoundError: When a module was not found and inspection is disallowed.

    Returns:
        A Griffe object.
    """
    obj_path: str
    package = None
    top_module = None

    # We always start by searching paths on the disk,
    # even if inspection is forced.
    logger.debug("Searching path(s) for %s", objspec)
    try:
        obj_path, package = self.finder.find_spec(
            objspec,  # ty:ignore[invalid-argument-type]
            try_relative_path=try_relative_path,
            find_stubs_package=find_stubs_package,
        )
    except ModuleNotFoundError:
        # If we couldn't find paths on disk and inspection is disabled,
        # re-raise ModuleNotFoundError.
        logger.debug("Could not find path for %s on disk", objspec)
        if not (self.allow_inspection or self.force_inspection):
            raise

        # Otherwise we try to dynamically import the top-level module.
        obj_path = str(objspec)
        top_module_name = obj_path.split(".", 1)[0]
        logger.debug("Trying to dynamically import %s", top_module_name)
        top_module_object = dynamic_import(top_module_name, self.finder.search_paths)

        try:
            top_module_path = top_module_object.__path__
            if not top_module_path:
                raise ValueError(f"Module {top_module_name} has no paths set")  # noqa: TRY301
        except (AttributeError, ValueError):
            # If the top-level module has no `__path__`, we inspect it as-is,
            # and do not try to recurse into submodules (there shouldn't be any in builtin/compiled modules).
            logger.debug("Module %s has no paths set (built-in module?). Inspecting it as-is.", top_module_name)
            top_module = self._inspect_module(top_module_name)
            self.modules_collection.set_member(top_module.path, top_module)
            return self._post_load(top_module, obj_path)

        # We found paths, and use them to build our intermediate Package or NamespacePackage struct.
        logger.debug("Module %s has paths set: %s", top_module_name, top_module_path)
        top_module_path = [Path(path) for path in top_module_path]
        if len(top_module_path) > 1:
            package = NamespacePackage(top_module_name, top_module_path)
        else:
            package = Package(top_module_name, top_module_path[0])

    # We have an intermediate package, and an object path: we're ready to load.
    logger.debug("Found %s: loading", objspec)
    try:
        top_module = self._load_package(package, submodules=submodules)
    except LoadingError:
        logger.exception("Could not load package %s", package)
        raise

    return self._post_load(top_module, obj_path)
```

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

Source code in `packages/griffelib/src/griffe/_internal/loader.py`

```
def resolve_aliases(
    self,
    *,
    implicit: bool = False,
    external: bool | None = None,
    max_iterations: int | None = None,
) -> tuple[set[str], int]:
    """Resolve aliases.

    Parameters:
        implicit: When false, only try to resolve an alias if it is explicitly exported.
        external: When false, don't try to load unspecified modules to resolve aliases.
        max_iterations: Maximum number of iterations on the loader modules collection.

    Returns:
        The unresolved aliases and the number of iterations done.
    """
    if max_iterations is None:
        max_iterations = float("inf")  # ty:ignore[invalid-assignment]
    prev_unresolved: set[str] = set()
    unresolved: set[str] = set("0")  # Init to enter loop.
    iteration = 0
    collection = self.modules_collection.members

    # Before resolving aliases, we try to expand wildcard imports again
    # (this was already done in `_post_load()`),
    # this time with the user-configured `external` setting,
    # and with potentially more packages loaded in the collection,
    # allowing to resolve more aliases.
    for wildcards_module in list(collection.values()):
        self.expand_wildcards(wildcards_module, external=external)

    load_failures: set[str] = set()
    while unresolved and unresolved != prev_unresolved and iteration < max_iterations:  # ty:ignore[unsupported-operator]
        prev_unresolved = unresolved - {"0"}
        unresolved = set()
        resolved: set[str] = set()
        iteration += 1
        for module_name in list(collection.keys()):
            module = collection[module_name]
            next_resolved, next_unresolved = self.resolve_module_aliases(
                module,
                implicit=implicit,
                external=external,
                load_failures=load_failures,
            )
            resolved |= next_resolved
            unresolved |= next_unresolved
        logger.debug(
            "Iteration %s finished, %s aliases resolved, still %s to go",
            iteration,
            len(resolved),
            len(unresolved),
        )
    return unresolved, iteration
```

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

Source code in `packages/griffelib/src/griffe/_internal/loader.py`

```
def resolve_module_aliases(
    self,
    obj: Object | Alias,
    *,
    implicit: bool = False,
    external: bool | None = None,
    seen: set[str] | None = None,
    load_failures: set[str] | None = None,
) -> tuple[set[str], set[str]]:
    """Follow aliases: try to recursively resolve all found aliases.

    Parameters:
        obj: The object and its members to recurse on.
        implicit: When false, only try to resolve an alias if it is explicitly exported.
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

    for member in obj.members.values():
        # Handle aliases.
        if member.is_alias:
            if member.wildcard or member.resolved:  # ty:ignore[possibly-missing-attribute]
                continue
            if not implicit and not member.is_exported:
                continue

            # Try resolving the alias. If it fails, check if it is because it comes
            # from an external package, and decide if we should load that package
            # to allow the alias to be resolved at the next iteration (maybe).
            try:
                member.resolve_target()  # ty:ignore[possibly-missing-attribute]
            except AliasResolutionError as error:
                target = error.alias.target_path
                unresolved.add(member.path)
                package = target.split(".", 1)[0]
                load_module = (
                    (external is True or (external is None and package == f"_{obj.package.name}"))
                    and package not in load_failures
                    and obj.package.path != package
                    and package not in self.modules_collection
                )
                if load_module:
                    logger.debug("Failed to resolve alias %s -> %s", member.path, target)
                    try:
                        self.load(package, try_relative_path=False)
                    except (ImportError, LoadingError) as error:
                        logger.debug("Could not follow alias %s: %s", member.path, error)
                        load_failures.add(package)
            except CyclicAliasError as error:
                logger.debug(str(error))
            else:
                logger.debug("Alias %s was resolved to %s", member.path, member.final_target.path)  # ty:ignore[possibly-missing-attribute]
                resolved.add(member.path)

        # Recurse into unseen modules and classes.
        elif member.kind in {Kind.MODULE, Kind.CLASS} and member.path not in seen:
            sub_resolved, sub_unresolved = self.resolve_module_aliases(
                member,
                implicit=implicit,
                external=external,
                seen=seen,
                load_failures=load_failures,
            )
            resolved |= sub_resolved
            unresolved |= sub_unresolved

    return resolved, unresolved
```

### stats

```
stats() -> Stats
```

Compute some statistics.

Returns:

- `Stats` – Some statistics.

Source code in `packages/griffelib/src/griffe/_internal/loader.py`

```
def stats(self) -> Stats:
    """Compute some statistics.

    Returns:
        Some statistics.
    """
    stats = Stats(self)
    stats.time_spent_visiting = self._time_stats["time_spent_visiting"]
    stats.time_spent_inspecting = self._time_stats["time_spent_inspecting"]
    return stats
```

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

Source code in `packages/griffelib/src/griffe/_internal/collections.py`

```
def __init__(self) -> None:
    """Initialize the collection."""
    self.members: dict[str, Module] = {}
    """Members (modules) of the collection."""
```

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

Source code in `packages/griffelib/src/griffe/_internal/collections.py`

```
def __bool__(self) -> bool:
    """A modules collection is always true-ish."""
    return True
```

### __contains__

```
__contains__(item: Any) -> bool
```

Check if a module is in the collection.

Source code in `packages/griffelib/src/griffe/_internal/collections.py`

```
def __contains__(self, item: Any) -> bool:
    """Check if a module is in the collection."""
    return item in self.members
```

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

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def __delitem__(self, key: str | Sequence[str]) -> None:
    """Delete a member with its name or path.

    This method is part of the consumer API:
    do not use when producing Griffe trees!

    Members will be looked up in both declared members and inherited ones,
    triggering computation of the latter.

    Parameters:
        key: The name or path of the member.

    Examples:
        >>> del griffe_object["foo"]
        >>> del griffe_object["path.to.bar"]
        >>> del griffe_object[("path", "to", "qux")]
    """
    parts = _get_parts(key)
    if len(parts) == 1:
        name = parts[0]
        try:
            del self.members[name]  # ty:ignore[unresolved-attribute]
        except KeyError:
            del self.inherited_members[name]  # ty:ignore[unresolved-attribute]
    else:
        del self.all_members[parts[0]][parts[1:]]  # ty:ignore[unresolved-attribute]
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

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def __getitem__(self, key: str | Sequence[str]) -> Any:
    """Get a member with its name or path.

    This method is part of the consumer API:
    do not use when producing Griffe trees!

    Members will be looked up in both declared members and inherited ones,
    triggering computation of the latter.

    Parameters:
        key: The name or path of the member.

    Examples:
        >>> foo = griffe_object["foo"]
        >>> bar = griffe_object["path.to.bar"]
        >>> qux = griffe_object[("path", "to", "qux")]
    """
    parts = _get_parts(key)
    if len(parts) == 1:
        return self.all_members[parts[0]]  # ty:ignore[unresolved-attribute]
    return self.all_members[parts[0]][parts[1:]]  # ty:ignore[unresolved-attribute]
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

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def __setitem__(self, key: str | Sequence[str], value: Object | Alias) -> None:
    """Set a member with its name or path.

    This method is part of the consumer API:
    do not use when producing Griffe trees!

    Parameters:
        key: The name or path of the member.
        value: The member.

    Examples:
        >>> griffe_object["foo"] = foo
        >>> griffe_object["path.to.bar"] = bar
        >>> griffe_object[("path", "to", "qux")] = qux
    """
    parts = _get_parts(key)
    if len(parts) == 1:
        name = parts[0]
        self.members[name] = value  # ty:ignore[unresolved-attribute]
        if self.is_collection:  # ty:ignore[unresolved-attribute]
            value._modules_collection = self  # ty:ignore[invalid-assignment]
        else:
            value.parent = self  # ty:ignore[invalid-assignment]
    else:
        self.members[parts[0]][parts[1:]] = value  # ty:ignore[unresolved-attribute]
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

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def del_member(self, key: str | Sequence[str]) -> None:
    """Delete a member with its name or path.

    This method is part of the producer API:
    you can use it safely while building Griffe trees
    (for example in Griffe extensions).

    Members will be looked up in declared members only, not inherited ones.

    Parameters:
        key: The name or path of the member.

    Examples:
        >>> griffe_object.del_member("foo")
        >>> griffe_object.del_member("path.to.bar")
        >>> griffe_object.del_member(("path", "to", "qux"))
    """
    parts = _get_parts(key)
    if len(parts) == 1:
        name = parts[0]
        del self.members[name]  # ty:ignore[unresolved-attribute]
    else:
        self.members[parts[0]].del_member(parts[1:])  # ty:ignore[unresolved-attribute]
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

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def get_member(self, key: str | Sequence[str]) -> Any:
    """Get a member with its name or path.

    This method is part of the producer API:
    you can use it safely while building Griffe trees
    (for example in Griffe extensions).

    Members will be looked up in declared members only, not inherited ones.

    Parameters:
        key: The name or path of the member.

    Examples:
        >>> foo = griffe_object["foo"]
        >>> bar = griffe_object["path.to.bar"]
        >>> bar = griffe_object[("path", "to", "bar")]
    """
    parts = _get_parts(key)
    if len(parts) == 1:
        return self.members[parts[0]]  # ty:ignore[unresolved-attribute]
    return self.members[parts[0]].get_member(parts[1:])  # ty:ignore[unresolved-attribute]
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

Source code in `packages/griffelib/src/griffe/_internal/mixins.py`

```
def set_member(self, key: str | Sequence[str], value: Object | Alias) -> None:
    """Set a member with its name or path.

    This method is part of the producer API:
    you can use it safely while building Griffe trees
    (for example in Griffe extensions).

    Parameters:
        key: The name or path of the member.
        value: The member.

    Examples:
        >>> griffe_object.set_member("foo", foo)
        >>> griffe_object.set_member("path.to.bar", bar)
        >>> griffe_object.set_member(("path", "to", "qux"), qux)
    """
    parts = _get_parts(key)
    if len(parts) == 1:
        name = parts[0]
        if name in self.members:  # ty:ignore[unresolved-attribute]
            member = self.members[name]  # ty:ignore[unresolved-attribute]
            if not member.is_alias:
                # When reassigning a module to an existing one,
                # try to merge them as one regular and one stubs module
                # (implicit support for .pyi modules).
                if member.is_module and not (member.is_namespace_package or member.is_namespace_subpackage):
                    # Accessing attributes of the value or member can trigger alias errors.
                    # Accessing file paths can trigger a builtin module error.
                    with suppress(AliasResolutionError, CyclicAliasError, BuiltinModuleError):
                        if value.is_module and value.filepath != member.filepath:
                            with suppress(ValueError):
                                value = merge_stubs(member, value)  # ty:ignore[invalid-argument-type]
                for alias in member.aliases.values():
                    with suppress(CyclicAliasError):
                        alias.target = value
        self.members[name] = value  # ty:ignore[unresolved-attribute]
        if self.is_collection:  # ty:ignore[unresolved-attribute]
            value._modules_collection = self  # ty:ignore[invalid-assignment]
        else:
            value.parent = self  # ty:ignore[invalid-assignment]
    else:
        self.members[parts[0]].set_member(parts[1:], value)  # ty:ignore[unresolved-attribute]
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

Source code in `packages/griffelib/src/griffe/_internal/collections.py`

```
def __init__(self) -> None:
    """Initialize the collection."""
    self._data: dict[Path, list[str]] = {}
```

### __bool__

```
__bool__() -> bool
```

A lines collection is always true-ish.

Source code in `packages/griffelib/src/griffe/_internal/collections.py`

```
def __bool__(self) -> bool:
    """A lines collection is always true-ish."""
    return True
```

### __contains__

```
__contains__(item: Path) -> bool
```

Check if a file path is in the collection.

Source code in `packages/griffelib/src/griffe/_internal/collections.py`

```
def __contains__(self, item: Path) -> bool:
    """Check if a file path is in the collection."""
    return item in self._data
```

### __getitem__

```
__getitem__(key: Path) -> list[str]
```

Get the lines of a file path.

Source code in `packages/griffelib/src/griffe/_internal/collections.py`

```
def __getitem__(self, key: Path) -> list[str]:
    """Get the lines of a file path."""
    return self._data[key]
```

### __setitem__

```
__setitem__(key: Path, value: list[str]) -> None
```

Set the lines of a file path.

Source code in `packages/griffelib/src/griffe/_internal/collections.py`

```
def __setitem__(self, key: Path, value: list[str]) -> None:
    """Set the lines of a file path."""
    self._data[key] = value
```

### items

```
items() -> ItemsView
```

Return the collection items.

Returns:

- `ItemsView` – The collection items.

Source code in `packages/griffelib/src/griffe/_internal/collections.py`

```
def items(self) -> ItemsView:
    """Return the collection items.

    Returns:
        The collection items.
    """
    return self._data.items()
```

### keys

```
keys() -> KeysView
```

Return the collection keys.

Returns:

- `KeysView` – The collection keys.

Source code in `packages/griffelib/src/griffe/_internal/collections.py`

```
def keys(self) -> KeysView:
    """Return the collection keys.

    Returns:
        The collection keys.
    """
    return self._data.keys()
```

### values

```
values() -> ValuesView
```

Return the collection values.

Returns:

- `ValuesView` – The collection values.

Source code in `packages/griffelib/src/griffe/_internal/collections.py`

```
def values(self) -> ValuesView:
    """Return the collection values.

    Returns:
        The collection values.
    """
    return self._data.values()
```

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

Source code in `packages/griffelib/src/griffe/_internal/stats.py`

```
def __init__(self, loader: GriffeLoader) -> None:
    """Initialiwe the stats object.

    Parameters:
        loader: The loader to compute stats for.
    """
    self.loader = loader
    """The loader to compute stats for."""

    modules_by_extension = defaultdict(
        int,
        {
            "": 0,
            ".py": 0,
            ".pyi": 0,
            ".pyc": 0,
            ".pyo": 0,
            ".pyd": 0,
            ".so": 0,
        },
    )

    top_modules = loader.modules_collection.members.values()

    self.by_kind = {
        Kind.MODULE: 0,
        Kind.CLASS: 0,
        Kind.FUNCTION: 0,
        Kind.ATTRIBUTE: 0,
        Kind.TYPE_ALIAS: 0,
    }
    """Number of objects by kind."""

    self.packages = len(top_modules)
    """Number of packages."""

    self.modules_by_extension = modules_by_extension
    """Number of modules by extension."""

    self.lines = sum(len(lines) for lines in loader.lines_collection.values())
    """Total number of lines."""

    self.time_spent_visiting = 0
    """Time spent visiting modules."""

    self.time_spent_inspecting = 0
    """Time spent inspecting modules."""

    self.time_spent_serializing = 0
    """Time spent serializing objects."""

    for module in top_modules:
        self._itercount(module)
```

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

Source code in `packages/griffelib/src/griffe/_internal/stats.py`

```
def as_text(self) -> str:
    """Format the statistics as text.

    Returns:
        Text stats.
    """
    lines = []
    packages = self.packages
    modules = self.by_kind[Kind.MODULE]
    classes = self.by_kind[Kind.CLASS]
    functions = self.by_kind[Kind.FUNCTION]
    attributes = self.by_kind[Kind.ATTRIBUTE]
    type_aliases = self.by_kind[Kind.TYPE_ALIAS]
    objects = sum((modules, classes, functions, attributes, type_aliases))
    lines.append("Statistics")
    lines.append("---------------------")
    lines.append("Number of loaded objects")
    lines.append(f"  Modules: {modules}")
    lines.append(f"  Classes: {classes}")
    lines.append(f"  Functions: {functions}")
    lines.append(f"  Attributes: {attributes}")
    lines.append(f"  Type aliases: {type_aliases}")
    lines.append(f"  Total: {objects} across {packages} packages")
    per_ext = self.modules_by_extension
    builtin = per_ext[""]
    regular = per_ext[".py"]
    stubs = per_ext[".pyi"]
    compiled = modules - builtin - regular - stubs
    lines.append("")
    lines.append(f"Total number of lines: {self.lines}")
    lines.append("")
    lines.append("Modules")
    lines.append(f"  Builtin: {builtin}")
    lines.append(f"  Compiled: {compiled}")
    lines.append(f"  Regular: {regular}")
    lines.append(f"  Stubs: {stubs}")
    lines.append("  Per extension:")
    for ext, number in sorted(per_ext.items()):
        if ext:
            lines.append(f"    {ext}: {number}")

    visit_time = self.time_spent_visiting / 1000
    inspect_time = self.time_spent_inspecting / 1000
    total_time = visit_time + inspect_time
    visit_percent = visit_time / total_time * 100
    inspect_percent = inspect_time / total_time * 100

    force_inspection = self.loader.force_inspection
    visited_modules = 0 if force_inspection else regular
    try:
        visit_time_per_module = visit_time / visited_modules
    except ZeroDivisionError:
        visit_time_per_module = 0

    inspected_modules = builtin + compiled + (regular if force_inspection else 0)
    try:
        inspect_time_per_module = inspect_time / inspected_modules
    except ZeroDivisionError:
        inspect_time_per_module = 0

    lines.append("")
    lines.append(
        f"Time spent visiting modules ({visited_modules}): "
        f"{visit_time}ms, {visit_time_per_module:.02f}ms/module ({visit_percent:.02f}%)",
    )
    lines.append(
        f"Time spent inspecting modules ({inspected_modules}): "
        f"{inspect_time}ms, {inspect_time_per_module:.02f}ms/module ({inspect_percent:.02f}%)",
    )

    serialize_time = self.time_spent_serializing / 1000
    serialize_time_per_module = serialize_time / modules
    lines.append(f"Time spent serializing: {serialize_time}ms, {serialize_time_per_module:.02f}ms/module")

    return "\n".join(lines)
```

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

Source code in `packages/griffelib/src/griffe/_internal/merger.py`

```
def merge_stubs(mod1: Module, mod2: Module) -> Module:
    """Merge stubs into a module.

    Parameters:
        mod1: A regular module or stubs module.
        mod2: A regular module or stubs module.

    Raises:
        ValueError: When both modules are regular modules (no stubs is passed).

    Returns:
        The regular module.
    """
    logger.debug("Trying to merge %s and %s", mod1.filepath, mod2.filepath)
    if mod1.filepath.suffix == ".pyi":  # ty:ignore[possibly-missing-attribute]
        stubs = mod1
        module = mod2
    elif mod2.filepath.suffix == ".pyi":  # ty:ignore[possibly-missing-attribute]
        stubs = mod2
        module = mod1
    else:
        raise ValueError("cannot merge regular (non-stubs) modules together")
    _merge_module_stubs(module, stubs)
    return module
```
