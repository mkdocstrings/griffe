# CLI entrypoints

## **Main API**

## main

```
main(args: list[str] | None = None) -> int
```

Run the main program.

This function is executed when you type `griffe` or `python -m griffe`.

Parameters:

- ### **`args`**

  (`list[str] | None`, default: `None` ) – Arguments passed from the command line.

Returns:

- `int` – An exit code.

## check

```
check(
    package: str | Path,
    against: str | None = None,
    against_path: str | Path | None = None,
    *,
    base_ref: str | None = None,
    extensions: Sequence[
        str | dict[str, Any] | Extension | type[Extension]
    ]
    | None = None,
    search_paths: Sequence[str | Path] | None = None,
    append_sys_path: bool = False,
    find_stubs_package: bool = False,
    allow_inspection: bool = True,
    force_inspection: bool = False,
    verbose: bool = False,
    color: bool | None = None,
    style: str | ExplanationStyle | None = None,
) -> int
```

Check for API breaking changes in two versions of the same package.

Parameters:

- ### **`package`**

  (`str | Path`) – The package to load and check.

- ### **`against`**

  (`str | None`, default: `None` ) – Older Git reference (commit, branch, tag) to check against.

- ### **`against_path`**

  (`str | Path | None`, default: `None` ) – Path when the "against" reference is checked out.

- ### **`base_ref`**

  (`str | None`, default: `None` ) – Git reference (commit, branch, tag) to check.

- ### **`extensions`**

  (`Sequence[str | dict[str, Any] | Extension | type[Extension]] | None`, default: `None` ) – The extensions to use.

- ### **`search_paths`**

  (`Sequence[str | Path] | None`, default: `None` ) – The paths to search into.

- ### **`append_sys_path`**

  (`bool`, default: `False` ) – Whether to append the contents of sys.path to the search paths.

- ### **`allow_inspection`**

  (`bool`, default: `True` ) – Whether to allow inspecting modules when visiting them is not possible.

- ### **`force_inspection`**

  (`bool`, default: `False` ) – Whether to force using dynamic analysis when loading data.

- ### **`verbose`**

  (`bool`, default: `False` ) – Use a verbose output.

Returns:

- `int` – 0 for success, 1 for failure.

## dump

```
dump(
    packages: Sequence[str],
    *,
    output: str | IO | None = None,
    full: bool = False,
    docstring_parser: DocstringStyle | Parser | None = None,
    docstring_options: DocstringOptions | None = None,
    extensions: Sequence[
        str | dict[str, Any] | Extension | type[Extension]
    ]
    | None = None,
    resolve_aliases: bool = False,
    resolve_implicit: bool = False,
    resolve_external: bool | None = None,
    search_paths: Sequence[str | Path] | None = None,
    find_stubs_package: bool = False,
    append_sys_path: bool = False,
    allow_inspection: bool = True,
    force_inspection: bool = False,
    stats: bool = False,
) -> int
```

Load packages data and dump it as JSON.

Parameters:

- ### **`packages`**

  (`Sequence[str]`) – The packages to load and dump.

- ### **`output`**

  (`str | IO | None`, default: `None` ) – Where to output the JSON-serialized data.

- ### **`full`**

  (`bool`, default: `False` ) – Whether to output full or minimal data.

- ### **`docstring_parser`**

  (`DocstringStyle | Parser | None`, default: `None` ) – The docstring parser to use. By default, no parsing is done.

- ### **`docstring_options`**

  (`DocstringOptions | None`, default: `None` ) – Docstring parsing options.

- ### **`resolve_aliases`**

  (`bool`, default: `False` ) – Whether to resolve aliases (indirect objects references).

- ### **`resolve_implicit`**

  (`bool`, default: `False` ) – Whether to resolve every alias or only the explicitly exported ones.

- ### **`resolve_external`**

  (`bool | None`, default: `None` ) – Whether to load additional, unspecified modules to resolve aliases. Default is to resolve only from one module to its private sibling (ast -> \_ast).

- ### **`extensions`**

  (`Sequence[str | dict[str, Any] | Extension | type[Extension]] | None`, default: `None` ) – The extensions to use.

- ### **`search_paths`**

  (`Sequence[str | Path] | None`, default: `None` ) – The paths to search into.

- ### **`find_stubs_package`**

  (`bool`, default: `False` ) – Whether to search for stubs-only packages. If both the package and its stubs are found, they'll be merged together. If only the stubs are found, they'll be used as the package itself.

- ### **`append_sys_path`**

  (`bool`, default: `False` ) – Whether to append the contents of sys.path to the search paths.

- ### **`allow_inspection`**

  (`bool`, default: `True` ) – Whether to allow inspecting modules when visiting them is not possible.

- ### **`force_inspection`**

  (`bool`, default: `False` ) – Whether to force using dynamic analysis when loading data.

- ### **`stats`**

  (`bool`, default: `False` ) – Whether to compute and log stats about loading.

Returns:

- `int` – 0 for success, 1 for failure.

## **Advanced API**

## get_parser

```
get_parser() -> ArgumentParser
```

Return the CLI argument parser.

Returns:

- `ArgumentParser` – An argparse parser.
