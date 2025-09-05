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

### `help`

Print this help. Add task name to print help.

```
make help [TASK]
```

When the Python dependencies are not installed, this command just print the available commands. When the Python dependencies are installed, [duty](https://github.com/pawamoy/duty) is available so the command can also print the available tasks.

If you add a task name after the command, it will print help for this specific task.

### `run`

Run a command in the default virtual environment.

```
make run <CMD> [ARG...]
```

This command runs an arbitrary command inside the default virtual environment (`.venv`). It is especially useful to start a Python interpreter without having to first activate the virtual environment: `make run python`.

### `multirun`

Run a command for all configured Python versions.

```
make multirun <CMD> [ARG...]
```

This command runs an arbitrary command inside the environments for all supported Python versions. It is especially useful for running tests.

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

### `3.x`

Run a command in the virtual environment for Python 3.x.

```
make 3.x <CMD> [ARG...]
```

This command runs an arbitrary command inside the environment of the selected Python version. It can be useful if you want to run a task that usually runs in the default environment with a different Python version.

### `clean`

Delete build artifacts and cache files.

```
make clean
```

This command simply deletes build artifacts and cache files and folders such as `build/`, `.cache/`, etc.. The virtual environments (`.venv` and `.venvs/*`) are not removed by this command.

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

### `check-api`

Check for API breaking changes.

```
make check-api
```

Compare the current code to the latest version (Git tag) using [Griffe](https://mkdocstrings.github.io/griffe/), to search for API breaking changes since latest version. It is set to allow failures, and is more about providing information than preventing CI to pass.

Parameters:

- **`*cli_args`** (`str`, default: `()` ) – Additional Griffe CLI arguments.

### `check-docs`

Check if the documentation builds correctly.

```
make check-docs
```

Build the docs with [MkDocs](https://www.mkdocs.org/) in strict mode.

The configuration for MkDocs is located at `mkdocs.yml`.

This task builds the documentation with strict behavior: any warning will be considered an error and the command will fail. The warnings/errors can be about incorrect docstring format, or invalid cross-references.

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

### `coverage`

Report coverage as text and HTML.

```

make coverage

```

Combine coverage data from multiple test runs with [Coverage.py](https://coverage.readthedocs.io/),
then generate an HTML report into the `htmlcov` directory,
and print a text report in the console.

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

### `docs-deploy`

Deploy the documentation to GitHub pages.

```

make docs-deploy

```

Use [MkDocs](https://www.mkdocs.org/) to build and deploy the documentation to GitHub pages.

Parameters:

- **`force`**
  (`bool`, default:
  `False`
  )
  –
  Whether to force deployment, even from non-Insiders version.

### `format`

Run formatting tools on the code.

```

make format

```

Format the code with [Ruff](https://astral.sh/ruff).
This command will also automatically fix some coding issues when possible.

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

### `publish`

Publish source and wheel distributions to PyPI.

```

make publish

```

Publish the source and wheel distributions of your project to PyPI
using [Twine](https://twine.readthedocs.io/).

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

### `test`

Run the test suite.

```

make test [match=EXPR]

````

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
- **`match`**
  (`str`, default:
  `''`
  )
  –
  A pytest expression to filter selected tests.```
````
