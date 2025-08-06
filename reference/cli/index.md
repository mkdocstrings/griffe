# CLI reference

## griffe

> Signatures for entire Python programs.

Global Options:

- `-h`, `--help`: Show this help message and exit. Commands also accept the -h/--help option.
- `-V`, `--version`: show program's version number and exit
- `--debug-info`: Print debug information.

Commands:

### dump

> Load package-signatures and dump them as JSON.

Search Options:

- `-s`, `--search`: Paths to search packages into.
- `-y`, `--sys-path`: Whether to append `sys.path` to search paths specified with `-s`.

Loading Options:

- `-B`, `--find-stubs-packages`: Whether to look for stubs-only packages and merge them with concrete ones.
- `-e`, `--extensions`: A list of extensions to use.
- `-X`, `--no-inspection`: Disallow inspection of builtin/compiled/not found modules. Default: `True`.
- `-x`, `--force-inspection`: Force inspection of everything, even when sources are found.

Dump Options:

- `packages` `PACKAGE`: Packages to find, load and dump.
- `-f`, `--full`: Whether to dump full data in JSON.
- `-o`, `--output`: Output file. Supports templating to output each package in its own file, with `{package}`. Default: `sys.stdout`.
- `-d`, `--docstyle`: The docstring style to parse.
- `-D`, `--docopts`: The options for the docstring parser.
- `-r`, `--resolve-aliases`: Whether to resolve aliases.
- `-I`, `--resolve-implicit`: Whether to resolve implicitly exported aliases as well. Aliases are explicitly exported when defined in `__all__`.
- `-U`, `--resolve-external`: Always resolve aliases pointing to external/unknown modules (not loaded directly).Default is to resolve only from one module to its private sibling (`ast` -> `_ast`).
- `--no-resolve-external`: Never resolve aliases pointing to external/unknown modules (not loaded directly).Default is to resolve only from one module to its private sibling (`ast` -> `_ast`). Default: `True`.
- `-S`, `--stats`: Show statistics at the end.

Debugging Options:

- `-L`, `--log-level` `LEVEL`: Set the log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Default: `INFO`.

Common Options:

- `-h`, `--help`: Show this help message and exit.

### check

> Check for API breakages or possible improvements.

Search Options:

- `-s`, `--search`: Paths to search packages into.
- `-y`, `--sys-path`: Whether to append `sys.path` to search paths specified with `-s`.

Loading Options:

- `-B`, `--find-stubs-packages`: Whether to look for stubs-only packages and merge them with concrete ones.
- `-e`, `--extensions`: A list of extensions to use.
- `-X`, `--no-inspection`: Disallow inspection of builtin/compiled/not found modules. Default: `True`.
- `-x`, `--force-inspection`: Force inspection of everything, even when sources are found.

Debugging Options:

- `-L`, `--log-level` `LEVEL`: Set the log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Default: `INFO`.

Common Options:

- `-h`, `--help`: Show this help message and exit.

Check Options:

- `package` `PACKAGE`: Package to find, load and check, as path.
- `-a`, `--against` `REF`: Older Git reference (commit, branch, tag) to check against. Default: load latest tag.
- `-b`, `--base-ref` `BASE_REF`: Git reference (commit, branch, tag) to check. Default: load current code.
- `--color`: Force enable colors in the output.
- `--no-color`: Force disable colors in the output.
- `-v`, `--verbose`: Verbose output.
- `-f`, `--format`: Output format.
