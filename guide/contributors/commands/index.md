# Management commands

The entry-point to run commands to manage the project is our Python `make` script, located in the `scripts` folder. You can either call it directly with `./scripts/make`, or you can use [direnv](https://direnv.net/) to add the script to your command line path. Once direnv is installed and hooked into your shell, allow it once for this directory with `direnv allow`. Now you can directly call the Python script with `make`. The `Makefile` is just here to provide auto-completion.

Try typing `make` or `make help` to show the available commands.

```
$ make
Available commands
  help                  Print this help. Add task name to print help.
  setup                 Setup all virtual environments (install dependencies).
  run                   Run a command in the default virtual environment.
  multirun              Run a command for all configured Python versions.
  allrun                Run a command in all virtual environments.
  3.x                   Run a command in the virtual environment for Python 3.x.
  clean                 Delete build artifacts and cache files.
  vscode                Configure VSCode to work on this project.
```

## Commands

Commands are always available: they don't require any Python dependency to be installed.

### `setup`

Setup all virtual environments (install dependencies).

```
make setup
```

The `setup` command installs all the Python dependencies required to work on the project. Virtual environments and dependencies are managed by [uv](https://github.com/astral-sh/uv). Development dependencies are listed in the `devdeps.txt` file.

The command will create a virtual environment in the `.venv` folder, as well as one virtual environment per supported Python version in the `.venvs/3.x` folders. Supported Python versions are listed in the `scripts/make` file, and can be overridden by setting the `PYTHON_VERSIONS` environment variable.

If you cloned the repository on the same file-system as uv's cache, everything will be hard linked from the cache, so don't worry about wasting disk space.

Once dependencies are installed, try running `make` or `make help` again, to show additional tasks.

```
$ make
Available commands
  help                  Print this help. Add task name to print help.
  setup                 Setup all virtual environments (install dependencies).
  run                   Run a command in the default virtual environment.
  multirun              Run a command for all configured Python versions.
  allrun                Run a command in all virtual environments.
  3.x                   Run a command in the virtual environment for Python 3.x.
  clean                 Delete build artifacts and cache files.
  vscode                Configure VSCode to work on this project.

Available tasks
  build                 Build source and wheel distributions.
  changelog             Update the changelog in-place with latest commits.
  check                 Check it all!
  check-api             Check for API breaking changes.
  check-docs            Check if the documentation builds correctly.
  check-quality         Check the code quality.
  check-types           Check that the code is correctly typed.
  coverage              Report coverage as text and HTML.
  docs                  Serve the documentation (localhost:8000).
  docs-deploy           Deploy the documentation to GitHub pages.
  format                Run formatting tools on the code.
  fuzz                  Fuzz Griffe against generated Python code.
  publish               Publish source and wheel distributions to PyPI.
  release               Release a new version of the project.
  test                  Run the test suite.
```

These tasks are written using [duty](https://github.com/pawamoy/duty) (a task runner), and located in the `duties.py` module in the repository root.

Some of these tasks will run in the default virtual environment (`.venv`), while others will run in all the supported Python version environments (`.venvs/3.x`).

Source code in `scripts/make.py`

````
@_command("setup")
def setup() -> None:
    """Setup all virtual environments (install dependencies).

    ```bash
    make setup
    ```

    The `setup` command installs all the Python dependencies required to work on the project.
    Virtual environments and dependencies are managed by [uv](https://github.com/astral-sh/uv).
    Development dependencies are listed in the `devdeps.txt` file.

    The command will create a virtual environment in the `.venv` folder,
    as well as one virtual environment per supported Python version in the `.venvs/3.x` folders.
    Supported Python versions are listed in the `scripts/make` file, and can be overridden
    by setting the `PYTHON_VERSIONS` environment variable.

    If you cloned the repository on the same file-system as uv's cache,
    everything will be hard linked from the cache, so don't worry about wasting disk space.

    Once dependencies are installed, try running `make` or `make help` again, to show additional tasks.

    ```console exec="1" source="console" id="make-help2"
    $ alias make="$PWD/scripts/make"  # markdown-exec: hide
    $ make
    ```

    These tasks are written using [duty](https://github.com/pawamoy/duty) (a task runner),
    and located in the `duties.py` module in the repository root.

    Some of these tasks will run in the default virtual environment (`.venv`),
    while others will run in all the supported Python version environments (`.venvs/3.x`).
    """
    if not shutil.which("uv"):
        raise ValueError("make: setup: uv must be installed, see https://github.com/astral-sh/uv")

    print("Installing dependencies (default environment)")
    default_venv = Path(".venv")
    if not default_venv.exists():
        _shell("uv venv --python python")
    _uv_install(default_venv)

    if PYTHON_VERSIONS:
        for version in PYTHON_VERSIONS:
            print(f"\nInstalling dependencies (python{version})")
            venv_path = Path(f".venvs/{version}")
            if not venv_path.exists():
                _shell(f"uv venv --python {version} {venv_path}")
            with _environ(VIRTUAL_ENV=str(venv_path.resolve())):
                _uv_install(venv_path)
````

### `help`

Print this help. Add task name to print help.

```
make help [TASK]
```

When the Python dependencies are not installed, this command just print the available commands. When the Python dependencies are installed, [duty](https://github.com/pawamoy/duty) is available so the command can also print the available tasks.

If you add a task name after the command, it will print help for this specific task.

Source code in `scripts/make.py`

````
@_command("help")
def help(*args: str) -> None:
    """Print this help. Add task name to print help.

    ```bash
    make help [TASK]
    ```

    When the Python dependencies are not installed,
    this command just print the available commands.
    When the Python dependencies are installed,
    [duty](https://github.com/pawamoy/duty) is available
    so the command can also print the available tasks.

    If you add a task name after the command, it will print help for this specific task.
    """
    if len(args) > 1:
        _run("default", "duty", "--help", args[1])
    else:
        print("Available commands", flush=True)
        for cmd in _commands:
            print(f"  {cmd.__cmdname__:21} {cmd.__doc__.splitlines()[0]}", flush=True)  # type: ignore[attr-defined,union-attr]
        if Path(".venv").exists():
            print("\nAvailable tasks", flush=True)
            run("duty", "--list")
````

### `run`

Run a command in the default virtual environment.

```
make run <CMD> [ARG...]
```

This command runs an arbitrary command inside the default virtual environment (`.venv`). It is especially useful to start a Python interpreter without having to first activate the virtual environment: `make run python`.

Source code in `scripts/make.py`

````
@_command("run")
def run(cmd: str, *args: str, **kwargs: Any) -> None:
    """Run a command in the default virtual environment.

    ```bash
    make run <CMD> [ARG...]
    ```

    This command runs an arbitrary command inside the default virtual environment (`.venv`).
    It is especially useful to start a Python interpreter without having to first activate
    the virtual environment: `make run python`.
    """
    _run("default", cmd, *args, **kwargs)
````

### `multirun`

Run a command for all configured Python versions.

```
make multirun <CMD> [ARG...]
```

This command runs an arbitrary command inside the environments for all supported Python versions. It is especially useful for running tests.

Source code in `scripts/make.py`

````
@_command("multirun")
def multirun(cmd: str, *args: str, **kwargs: Any) -> None:
    """Run a command for all configured Python versions.

    ```bash
    make multirun <CMD> [ARG...]
    ```

    This command runs an arbitrary command inside the environments
    for all supported Python versions. It is especially useful for running tests.
    """
    if PYTHON_VERSIONS:
        for version in PYTHON_VERSIONS:
            run3x(version, cmd, *args, **kwargs)
    else:
        run(cmd, *args, **kwargs)
````

### `allrun`

Run a command in all virtual environments.

```
make multirun <CMD> [ARG...]
```

This command runs an arbitrary command inside the default environment, as well as the environments for all supported Python versions.

This command is especially useful to install, remove or update dependencies in all environments at once. For example, if you want to install a dependency in editable mode, from a local source:

```
make allrun uv pip install -e ../other-project
```

Source code in `scripts/make.py`

````
@_command("allrun")
def allrun(cmd: str, *args: str, **kwargs: Any) -> None:
    """Run a command in all virtual environments.

    ```bash
    make multirun <CMD> [ARG...]
    ```

    This command runs an arbitrary command inside the default environment,
    as well as the environments for all supported Python versions.

    This command is especially useful to install, remove or update dependencies
    in all environments at once. For example, if you want to install a dependency
    in editable mode, from a local source:

    ```bash
    make allrun uv pip install -e ../other-project
    ```
    """
    run(cmd, *args, **kwargs)
    if PYTHON_VERSIONS:
        multirun(cmd, *args, **kwargs)
````

### `3.x`

Run a command in the virtual environment for Python 3.x.

```
make 3.x <CMD> [ARG...]
```

This command runs an arbitrary command inside the environment of the selected Python version. It can be useful if you want to run a task that usually runs in the default environment with a different Python version.

Source code in `scripts/make.py`

````
@_command("3.x")
def run3x(version: str, cmd: str, *args: str, **kwargs: Any) -> None:
    """Run a command in the virtual environment for Python 3.x.

    ```bash
    make 3.x <CMD> [ARG...]
    ```

    This command runs an arbitrary command inside the environment of the selected Python version.
    It can be useful if you want to run a task that usually runs in the default environment
    with a different Python version.
    """
    _run(version, cmd, *args, **kwargs)
````

### `clean`

Delete build artifacts and cache files.

```
make clean
```

This command simply deletes build artifacts and cache files and folders such as `build/`, `.cache/`, etc.. The virtual environments (`.venv` and `.venvs/*`) are not removed by this command.

Source code in `scripts/make.py`

````
@_command("clean")
def clean() -> None:
    """Delete build artifacts and cache files.

    ```bash
    make clean
    ```

    This command simply deletes build artifacts and cache files and folders
    such as `build/`, `.cache/`, etc.. The virtual environments (`.venv` and `.venvs/*`)
    are not removed by this command.
    """
    paths_to_clean = ["build", "dist", "htmlcov", "site", ".coverage*", ".pdm-build"]
    for path in paths_to_clean:
        _shell(f"rm -rf {path}")

    cache_dirs = [".cache", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__"]
    for dirpath in Path().rglob("*/"):
        if dirpath.parts[0] not in (".venv", ".venvs") and dirpath.name in cache_dirs:
            shutil.rmtree(dirpath, ignore_errors=True)
````

### `vscode`

Configure VSCode to work on this project.

```
make vscode
```

This command configures the [VSCode editor](https://code.visualstudio.com/) by copying the following files into the `.vscode` directory:

- `launch.json`, for run configurations (to run debug sessions)
- `settings.json`, for various editor settings like linting tools and their configuration
- `tasks.json`, for running tasks directly from VSCode's interface

Warning: These files will be overwritten every time the command is run.

Source code in `scripts/make.py`

````
@_command("vscode")
def vscode() -> None:
    """Configure VSCode to work on this project.

    ```bash
    make vscode
    ```

    This command configures the [VSCode editor](https://code.visualstudio.com/)
    by copying the following files into the `.vscode` directory:

    - `launch.json`, for run configurations (to run debug sessions)
    - `settings.json`, for various editor settings like linting tools and their configuration
    - `tasks.json`, for running tasks directly from VSCode's interface

    Warning:
        These files will be overwritten every time the command is run.
    """
    Path(".vscode").mkdir(parents=True, exist_ok=True)
    _shell("cp -v config/vscode/* .vscode")
````

## Tasks

Tasks require the Python dependencies to be installed. They use various tools and libraries to assert code quality, run tests, serve the documentation locally, or build and publish distributions of your project. There are multiple ways to run tasks:

- `make TASK`, the main, configured way to run a task
- `make run duty TASK`, to run a task in the default environment
- `make multirun duty TASK`, to run a task on all supported Python versions
- `make allrun duty TASK`, to run a task in *all* environments
- `make 3.x duty TASK`, to run a task on a specific Python version

### `build`

Build source and wheel distributions.

```
make build
```

Build distributions of your project for the current version. The build task uses the [`build` tool](https://build.pypa.io/en/stable/) to build `.tar.gz` (Gzipped sources archive) and `.whl` (wheel) distributions of your project in the `dist` directory.

Source code in `duties.py`

````
@duty
def build(ctx: Context) -> None:
    """Build source and wheel distributions.

    ```bash
    make build
    ```

    Build distributions of your project for the current version.
    The build task uses the [`build` tool](https://build.pypa.io/en/stable/)
    to build `.tar.gz` (Gzipped sources archive) and `.whl` (wheel) distributions
    of your project in the `dist` directory.
    """
    ctx.run(
        tools.build(),
        title="Building source and wheel distributions",
        pty=PTY,
    )
````

### `changelog`

Update the changelog in-place with latest commits.

```
make changelog [bump=VERSION]
```

Update the changelog in-place. The changelog task uses [git-changelog](https://pawamoy.github.io/git-changelog/) to read Git commits and parse their messages to infer the new version based on our commit message convention.

The new version will be based on the types of the latest commits, unless a specific version is provided with the `bump` parameter.

If the group of commits contains only bug fixes (`fix:`) and/or commits that are not interesting for users (`chore:`, `style:`, etc.), the changelog will gain a new **patch** entry. It means that the new suggested version will be a patch bump of the previous one: `0.1.1` becomes `0.1.2`.

If the group of commits contains at least one feature (`feat:`), the changelog will gain a new **minor** entry. It means that the new suggested version will be a minor bump of the previous one: `0.1.1` becomes `0.2.0`.

If there is, in the group of commits, a commit whose body contains something like `Breaking change`, the changelog will gain a new **major** entry, unless the version is still an "alpha" version (starting with 0), in which case it gains a **minor** entry. It means that the new suggested version will be a major bump of the previous one: `1.2.1` becomes `2.0.0`, but `0.2.1` is only bumped up to `0.3.0`. Moving from "alpha" status to "beta" or "stable" status is a choice left to the developers, when they consider the package is ready for it.

The configuration for git-changelog is located at `config/git-changelog.toml`.

Parameters:

- **`bump`** (`str`, default: `''` ) – Bump option passed to git-changelog.

Source code in `duties.py`

````
@duty
def changelog(ctx: Context, bump: str = "") -> None:
    """Update the changelog in-place with latest commits.

    ```bash
    make changelog [bump=VERSION]
    ```

    Update the changelog in-place. The changelog task uses [git-changelog](https://pawamoy.github.io/git-changelog/)
    to read Git commits and parse their messages to infer the new version based
    on our [commit message convention][commit-message-convention].

    The new version will be based on the types of the latest commits,
    unless a specific version is provided with the `bump` parameter.

    If the group of commits contains only bug fixes (`fix:`)
    and/or commits that are not interesting for users (`chore:`, `style:`, etc.),
    the changelog will gain a new **patch** entry.
    It means that the new suggested version will be a patch bump
    of the previous one: `0.1.1` becomes `0.1.2`.

    If the group of commits contains at least one feature (`feat:`),
    the changelog will gain a new **minor** entry.
    It means that the new suggested version will be a minor bump
    of the previous one: `0.1.1` becomes `0.2.0`.

    If there is, in the group of commits, a commit whose body contains something like `Breaking change`,
    the changelog will gain a new **major** entry, unless the version is still an "alpha" version (starting with 0),
    in which case it gains a **minor** entry.
    It means that the new suggested version will be a major bump
    of the previous one: `1.2.1` becomes `2.0.0`, but `0.2.1` is only bumped up to `0.3.0`.
    Moving from "alpha" status to "beta" or "stable" status is a choice left to the developers,
    when they consider the package is ready for it.

    The configuration for git-changelog is located at `config/git-changelog.toml`.

    Parameters:
        bump: Bump option passed to git-changelog.
    """
    ctx.run(tools.git_changelog(bump=bump or None), title="Updating changelog")
    ctx.run(tools.yore.check(bump=bump or _get_changelog_version()), title="Checking legacy code")
````

### `check`

Check it all!

```
make check
```

Composite command to run all the check commands:

- check-quality, to check the code quality on all Python versions
- check-types, to type-check the code on all Python versions
- check-docs, to check the docs on all Python versions
- check-api, to check for API breaking changes

Source code in `duties.py`

````
@duty(pre=["check-quality", "check-types", "check-docs", "check-api"])
def check(ctx: Context) -> None:
    """Check it all!

    ```bash
    make check
    ```

    Composite command to run all the check commands:

    - [`check-quality`][], to check the code quality on all Python versions
    - [`check-types`][], to type-check the code on all Python versions
    - [`check-docs`][], to check the docs on all Python versions
    - [`check-api`][], to check for API breaking changes
    """
````

### `check-api`

Check for API breaking changes.

```
make check-api
```

Compare the current code to the latest version (Git tag) using [Griffe](https://mkdocstrings.github.io/griffe/), to search for API breaking changes since latest version. It is set to allow failures, and is more about providing information than preventing CI to pass.

Parameters:

- **`*cli_args`** (`str`, default: `()` ) – Additional Griffe CLI arguments.

Source code in `duties.py`

````
@duty(nofail=PY_VERSION == PY_DEV)
def check_api(ctx: Context, *cli_args: str) -> None:
    """Check for API breaking changes.

    ```bash
    make check-api
    ```

    Compare the current code to the latest version (Git tag)
    using [Griffe](https://mkdocstrings.github.io/griffe/),
    to search for API breaking changes since latest version.
    It is set to allow failures, and is more about providing information
    than preventing CI to pass.

    Parameters:
        *cli_args: Additional Griffe CLI arguments.
    """
    ctx.run(
        tools.griffe.check(
            "griffe",
            search=["src"],
            color=True,
            extensions=[
                "griffe_inherited_docstrings",
                # YORE: Bump 2: Remove line.
                "scripts/griffe_exts.py",
                "unpack_typeddict",
            ],
        ).add_args(*cli_args),
        title="Checking for API breaking changes",
        nofail=True,
    )
````

### `check-docs`

Check if the documentation builds correctly.

```
make check-docs
```

Build the docs with [MkDocs](https://www.mkdocs.org/) in strict mode.

The configuration for MkDocs is located at `mkdocs.yml`.

This task builds the documentation with strict behavior: any warning will be considered an error and the command will fail. The warnings/errors can be about incorrect docstring format, or invalid cross-references.

Source code in `duties.py`

````
@duty(nofail=PY_VERSION == PY_DEV)
def check_docs(ctx: Context) -> None:
    """Check if the documentation builds correctly.

    ```bash
    make check-docs
    ```

    Build the docs with [MkDocs](https://www.mkdocs.org/) in strict mode.

    The configuration for MkDocs is located at `mkdocs.yml`.

    This task builds the documentation with strict behavior:
    any warning will be considered an error and the command will fail.
    The warnings/errors can be about incorrect docstring format,
    or invalid cross-references.
    """
    Path("htmlcov").mkdir(parents=True, exist_ok=True)
    Path("htmlcov/index.html").touch(exist_ok=True)
    if CI:
        os.environ["DEPLOY"] = "true"
    with _material_insiders():
        ctx.run(
            tools.mkdocs.build(strict=True, verbose=True),
            title=_pyprefix("Building documentation"),
        )
````

### `check-quality`

Check the code quality.

```
make check-quality
```

Check the code quality using [Ruff](https://astral.sh/ruff).

The configuration for Ruff is located at `config/ruff.toml`. In this file, you can deactivate rules or activate others to customize your analysis. Rule identifiers always start with one or more capital letters, like `D`, `S` or `BLK`, then followed by a number.

You can ignore a rule on a specific code line by appending a `noqa` comment ("no quality analysis/assurance"):

src/your_package/module.py

```
print("a code line that triggers a Ruff warning")  # noqa: ID
```

...where ID is the identifier of the rule you want to ignore for this line.

Example:

src/your_package/module.py

```
import subprocess
```

````
```console
$ make check-quality
✗ Checking code quality (1)
> ruff check --config=config/ruff.toml src/ tests/ scripts/
src/your_package/module.py:2:1: S404 Consider possible security implications associated with subprocess module.
````

Now add a comment to ignore this warning.

```python title="src/your_package/module.py"
import subprocess  # noqa: S404
```

```console
$ make check-quality
✓ Checking code quality
```

You can disable multiple different warnings on a single line by separating them with commas, for example `# noqa: D300,D301`.

```

You can disable a warning globally by adding its ID
into the list in `config/ruff.toml`.

You can also disable warnings per file, like so:

config/ruff.toml

```

[per-file-ignores] "src/your_package/your_module.py" = [ "T201", # Print statement ]

```


Source code in `duties.py`

```

@duty(nofail=PY_VERSION == PY_DEV) def check_quality(ctx: Context) -> None: """Check the code quality.

````
```bash
make check-quality
```

Check the code quality using [Ruff](https://astral.sh/ruff).

The configuration for Ruff is located at `config/ruff.toml`.
In this file, you can deactivate rules or activate others to customize your analysis.
Rule identifiers always start with one or more capital letters, like `D`, `S` or `BLK`,
then followed by a number.

You can ignore a rule on a specific code line by appending
a `noqa` comment ("no quality analysis/assurance"):

```python title="src/your_package/module.py"
print("a code line that triggers a Ruff warning")  # noqa: ID
```

...where ID is the identifier of the rule you want to ignore for this line.

Example:
    ```python title="src/your_package/module.py"
    import subprocess
    ```

    ```console
    $ make check-quality
    ✗ Checking code quality (1)
    > ruff check --config=config/ruff.toml src/ tests/ scripts/
    src/your_package/module.py:2:1: S404 Consider possible security implications associated with subprocess module.
    ```

    Now add a comment to ignore this warning.

    ```python title="src/your_package/module.py"
    import subprocess  # noqa: S404
    ```

    ```console
    $ make check-quality
    ✓ Checking code quality
    ```

    You can disable multiple different warnings on a single line
    by separating them with commas, for example `# noqa: D300,D301`.

You can disable a warning globally by adding its ID
into the list in `config/ruff.toml`.

You can also disable warnings per file, like so:

```toml title="config/ruff.toml"
[per-file-ignores]
"src/your_package/your_module.py" = [
    "T201",  # Print statement
]
```
"""
ctx.run(
    tools.ruff.check(*PY_SRC_LIST, config="config/ruff.toml"),
    title=_pyprefix("Checking code quality"),
)
````

```

### `check-types`

Check that the code is correctly typed.

```

make check-types

```

Run type-checking on the code with [Mypy](https://mypy.readthedocs.io/).

The configuration for Mypy is located at `config/mypy.ini`.

If you cannot or don't know how to fix a typing error in your code,
as a last resort you can ignore this specific error with a comment:

src/your_package/module.py

```

print("a code line that triggers a Mypy warning") # type: ignore[ID]

```

...where ID is the name of the warning.

Example:

src/your_package/module.py

```

result = data_dict.get(key, None).value

```

```

```console
$ make check-types
✗ Checking types (1)
> mypy --config-file=config/mypy.ini src/ tests/ scripts/
src/your_package/module.py:2:1: Item "None" of "Data | None" has no attribute "value" [union-attr]
```

Now add a comment to ignore this warning.

```python title="src/your_package/module.py"
result = data_dict.get(key, None).value  # type: ignore[union-attr]
```

```console
$ make check-types
✓ Checking types
```

```


Source code in `duties.py`

```

@duty(nofail=PY_VERSION == PY_DEV) def check_types(ctx: Context) -> None: """Check that the code is correctly typed.

````
```bash
make check-types
```

Run type-checking on the code with [Mypy](https://mypy.readthedocs.io/).

The configuration for Mypy is located at `config/mypy.ini`.

If you cannot or don't know how to fix a typing error in your code,
as a last resort you can ignore this specific error with a comment:

```python title="src/your_package/module.py"
print("a code line that triggers a Mypy warning")  # type: ignore[ID]
```

...where ID is the name of the warning.

Example:
    ```python title="src/your_package/module.py"
    result = data_dict.get(key, None).value
    ```

    ```console
    $ make check-types
    ✗ Checking types (1)
    > mypy --config-file=config/mypy.ini src/ tests/ scripts/
    src/your_package/module.py:2:1: Item "None" of "Data | None" has no attribute "value" [union-attr]
    ```

    Now add a comment to ignore this warning.

    ```python title="src/your_package/module.py"
    result = data_dict.get(key, None).value  # type: ignore[union-attr]
    ```

    ```console
    $ make check-types
    ✓ Checking types
    ```
"""
os.environ["FORCE_COLOR"] = "1"
ctx.run(
    tools.mypy(*PY_SRC_LIST, config_file="config/mypy.ini"),
    title=_pyprefix("Type-checking"),
)
````

```

### `coverage`

Report coverage as text and HTML.

```

make coverage

```

Combine coverage data from multiple test runs with [Coverage.py](https://coverage.readthedocs.io/),
then generate an HTML report into the `htmlcov` directory,
and print a text report in the console.


Source code in `duties.py`

```

@duty(silent=True, aliases=["cov"]) def coverage(ctx: Context) -> None: """Report coverage as text and HTML.

````
```bash
make coverage
```

Combine coverage data from multiple test runs with [Coverage.py](https://coverage.readthedocs.io/),
then generate an HTML report into the `htmlcov` directory,
and print a text report in the console.
"""
ctx.run(tools.coverage.combine(), nofail=True)
ctx.run(tools.coverage.report(rcfile="config/coverage.ini"), capture=False)
ctx.run(tools.coverage.html(rcfile="config/coverage.ini"))
````

```

### `docs`

Serve the documentation (localhost:8000).

```

make docs

```

This task uses [MkDocs](https://www.mkdocs.org/) to serve the documentation locally.

Parameters:

- **`*cli_args`**
  (`str`, default:
  `()`
  )
  –
  Additional MkDocs CLI arguments.
- **`host`**
  (`str`, default:
  `'127.0.0.1'`
  )
  –
  The host to serve the docs from.
- **`port`**
  (`int`, default:
  `8000`
  )
  –
  The port to serve the docs on.


Source code in `duties.py`

```

@duty def docs(ctx: Context, \*cli_args: str, host: str = "127.0.0.1", port: int = 8000) -> None: """Serve the documentation (localhost:8000).

````
```bash
make docs
```

This task uses [MkDocs](https://www.mkdocs.org/) to serve the documentation locally.

Parameters:
    *cli_args: Additional MkDocs CLI arguments.
    host: The host to serve the docs from.
    port: The port to serve the docs on.
"""
with _material_insiders():
    ctx.run(
        tools.mkdocs.serve(dev_addr=f"{host}:{port}").add_args(*cli_args),
        title="Serving documentation",
        capture=False,
    )
````

```

### `docs-deploy`

Deploy the documentation to GitHub pages.

```

make docs-deploy

```

Use [MkDocs](https://www.mkdocs.org/) to build and deploy the documentation to GitHub pages.


Source code in `duties.py`

```

@duty def docs_deploy(ctx: Context) -> None: """Deploy the documentation to GitHub pages.

````
```bash
make docs-deploy
```

Use [MkDocs](https://www.mkdocs.org/) to build and deploy the documentation to GitHub pages.
"""
os.environ["DEPLOY"] = "true"
with _material_insiders() as insiders:
    if not insiders:
        ctx.run(lambda: False, title="Not deploying docs without Material for MkDocs Insiders!")
    ctx.run(tools.mkdocs.gh_deploy(force=True), title="Deploying documentation")
````

```

### `format`

Run formatting tools on the code.

```

make format

```

Format the code with [Ruff](https://astral.sh/ruff).
This command will also automatically fix some coding issues when possible.


Source code in `duties.py`

```

@duty def format(ctx: Context) -> None: """Run formatting tools on the code.

````
```bash
make format
```

Format the code with [Ruff](https://astral.sh/ruff).
This command will also automatically fix some coding issues when possible.
"""
ctx.run(
    tools.ruff.check(*PY_SRC_LIST, config="config/ruff.toml", fix_only=True, exit_zero=True),
    title="Auto-fixing code",
)
ctx.run(tools.ruff.format(*PY_SRC_LIST, config="config/ruff.toml"), title="Formatting code")
````

```

### `fuzz`

Fuzz Griffe against generated Python code.

Parameters:

- **`ctx`**
  (`Context`)
  –
  The context instance (passed automatically).
- **`size`**
  (`int`, default:
  `20`
  )
  –
  The size of the case set (number of cases to test).
- **`seeds`**
  (`_Seeds`, default:
  `_Seeds()`
  )
  –
  Seeds to test or exclude (comma-separated integers).
- **`min_seed`**
  (`int`, default:
  `0`
  )
  –
  Minimum value for the seeds range.
- **`max_seed`**
  (`int`, default:
  `1000000`
  )
  –
  Maximum value for the seeds range.


Source code in `duties.py`

```

@duty def fuzz( ctx: Context, \*, size: int = 20, min_seed: int = 0, max_seed: int = 1_000_000, seeds: \_Seeds = \_Seeds(), # noqa: B008 ) -> None: """Fuzz Griffe against generated Python code.

```
Parameters:
    ctx: The context instance (passed automatically).
    size: The size of the case set (number of cases to test).
    seeds: Seeds to test or exclude (comma-separated integers).
    min_seed: Minimum value for the seeds range.
    max_seed: Maximum value for the seeds range.
"""
from griffe import visit  # noqa: PLC0415

warnings.simplefilter("ignore", SyntaxWarning)

def fails(code: str, filepath: Path) -> bool:
    try:
        visit(filepath.stem, filepath=filepath, code=code)
    except Exception:  # noqa: BLE001
        return True
    return False

def test_seed(seed: int, revisit: bool = False) -> bool:  # noqa: FBT001,FBT002
    filepath = Path(gettempdir(), f"fuzz_{seed}_{sys.version_info.minor}.py")
    if filepath.exists():
        if revisit:
            code = filepath.read_text()
        else:
            return True
    else:
        code = generate(seed)
        filepath.write_text(code)

    if fails(code, filepath):
        new_code = minimize(code, partial(fails, filepath=filepath))
        if code != new_code:
            filepath.write_text(new_code)
        return False
    return True

revisit = bool(seeds)
seeds = seeds or sample(range(min_seed, max_seed + 1), size)  # type: ignore[assignment]
for seed in seeds:
    ctx.run(test_seed, args=[seed, revisit], title=f"Visiting code generated with seed {seed}")
```

```

### `publish`

Publish source and wheel distributions to PyPI.

```

make publish

```

Publish the source and wheel distributions of your project to PyPI
using [Twine](https://twine.readthedocs.io/).


Source code in `duties.py`

```

@duty def publish(ctx: Context) -> None: """Publish source and wheel distributions to PyPI.

````
```bash
make publish
```

Publish the source and wheel distributions of your project to PyPI
using [Twine](https://twine.readthedocs.io/).
"""
if not Path("dist").exists():
    ctx.run("false", title="No distribution files found")
dists = [str(dist) for dist in Path("dist").iterdir()]
ctx.run(
    tools.twine.upload(*dists, skip_existing=True),
    title="Publishing source and wheel distributions to PyPI",
    pty=PTY,
)
````

```

### `release`

Release a new version of the project.

```

make release [version=VERSION]

```

This task will:

- Stage changes to `pyproject.toml` and `CHANGELOG.md`
- Commit the changes with a message like `chore: Prepare release 1.0.0`
- Tag the commit with the new version number
- Push the commit and the tag to the remote repository
- Build source and wheel distributions
- Publish the distributions to PyPI
- Deploy the documentation to GitHub pages

Parameters:

- **`version`**
  (`str`, default:
  `''`
  )
  –
  The new version number to use. If not provided, you will be prompted for it.


Source code in `duties.py`

```

@duty(post=["build", "publish", "docs-deploy"]) def release(ctx: Context, version: str = "") -> None: """Release a new version of the project.

````
```bash
make release [version=VERSION]
```

This task will:

- Stage changes to `pyproject.toml` and `CHANGELOG.md`
- Commit the changes with a message like `chore: Prepare release 1.0.0`
- Tag the commit with the new version number
- Push the commit and the tag to the remote repository
- Build source and wheel distributions
- Publish the distributions to PyPI
- Deploy the documentation to GitHub pages

Parameters:
    version: The new version number to use. If not provided, you will be prompted for it.
"""
if not (version := (version or input("> Version to release: ")).strip()):
    ctx.run("false", title="A version must be provided")
ctx.run("git add pyproject.toml CHANGELOG.md", title="Staging files", pty=PTY)
ctx.run(["git", "commit", "-m", f"chore: Prepare release {version}"], title="Committing changes", pty=PTY)
ctx.run(f"git tag -m '' -a {version}", title="Tagging commit", pty=PTY)
ctx.run("git push", title="Pushing commits", pty=False)
ctx.run("git push --tags", title="Pushing tags", pty=False)
````

```

### `test`

Run the test suite.

```

make test

```

Run the test suite with [Pytest](https://docs.pytest.org/) and plugins.
Code source coverage is computed thanks to
[coveragepy](https://coverage.readthedocs.io/en/coverage-5.1/).

Parameters:

- **`*cli_args`**
  (`str`, default:
  `()`
  )
  –
  Additional Pytest CLI arguments.


Source code in `duties.py`

```

@duty(nofail=PY_VERSION == PY_DEV) def test(ctx: Context, \*cli_args: str) -> None: """Run the test suite.

````
```bash
make test
```

Run the test suite with [Pytest](https://docs.pytest.org/) and plugins.
Code source coverage is computed thanks to
[coveragepy](https://coverage.readthedocs.io/en/coverage-5.1/).

Parameters:
    *cli_args: Additional Pytest CLI arguments.
"""
os.environ["COVERAGE_FILE"] = f".coverage.{PY_VERSION}"
os.environ["PYTHONWARNDEFAULTENCODING"] = "1"
ctx.run(
    tools.pytest(
        "tests",
        config_file="config/pytest.ini",
        color="yes",
    ).add_args("-n", "auto", *cli_args),
    title=_pyprefix("Running tests"),
)
````

```
```
