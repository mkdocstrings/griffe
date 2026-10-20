# Management commands

!!! info "For contributors and maintainers"
    Use this page to choose a development task and find its options. Start with [environment setup](setup.md) if dependencies are not installed.

The entry-point to run commands to manage the project is our Python `make` script, located in the `scripts` folder. You can either call it directly with `./scripts/make`, or you can use [direnv](https://direnv.net/) to add the script to your command line path. Once direnv is installed and hooked into your shell, allow it once for this directory with `direnv allow`. Now you can directly call the Python script with `make`. The `Makefile` is just here to provide auto-completion.

On this page, a **command** is a built-in operation of the `make` script. A **task** is an operation defined in `duties.py`, using the [duty](https://pawamoy.github.io/duty/) task runner. Both are invoked with `make NAME`.

Try typing `make` or `make help` to show the available commands.

```console exec="1" source="console" id="make-help1"
$ alias make="$PWD/scripts/make"; cd  # markdown-exec: hide
$ make
```

## Commands

Commands are always available: they don't require any Python dependency to be installed.

| Command | Use it to |
| --- | --- |
| [`setup`](#command-setup) | Install development dependencies in the virtual environments. |
| [`help`](#command-help) | List operations or show a task's options. |
| [`run`](#command-run) | Run a tool in the default environment. |
| [`multirun`](#command-multirun) | Run a tool for all configured Python versions. |
| [`allrun`](#command-allrun) | Run a tool in both the default and version-specific environments. |
| [`3.x`](#command-3.x) | Run a tool with a particular Python version. |
| [`clean`](#command-clean) | Remove build artifacts and caches. |
| [`vscode`](#command-vscode) | Configure VSCode for development. |
| [`zed`](#command-zed) | Configure Zed for development. |

[](){#command-setup}

### `setup`

::: make.setup
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#command-help}

### `help`

::: make.help
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#command-run}

### `run`

::: make.run
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#command-multirun}

### `multirun`

::: make.multirun
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#command-allrun}

### `allrun`

::: make.allrun
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#command-3.x}

### `3.x`

::: make.run3x
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#command-clean}

### `clean`

::: make.clean
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#command-vscode}

### `vscode`

::: make.vscode
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#command-zed}

### `zed`

::: make.zed
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

## Tasks

Tasks require the Python dependencies to be installed. They use various tools and libraries to assert code quality, run tests, serve the documentation locally, or build and publish distributions of your project. There are multiple ways to run tasks:

- `make TASK`, the main, configured way to run a task
- `make run duty TASK`, to run a task in the default environment
- `make multirun duty TASK`, to run a task on all supported Python versions
- `make allrun duty TASK`, to run a task in *all* environments
- `make 3.x duty TASK`, to run a task on a specific Python version

| Task | Use it to |
| --- | --- |
| [`build`](#task-build) | Build distributions locally to check packaging. |
| [`changelog`](#task-changelog) | Prepare a changelog entry before a release (maintainers). |
| [`check`](#task-check) | Run all checks before submitting changes. |
| [`check-api`](#task-check-api) | Look for breaking changes after editing the public API. |
| [`check-docs`](#task-check-docs) | Build documentation and report warnings as errors. |
| [`check-quality`](#task-check-quality) | Check code style and lint rules. |
| [`check-security`](#task-check-security) | Audit dependencies and GitHub Actions workflows. |
| [`check-types`](#task-check-types) | Check types after changing annotations or implementation. |
| [`coverage`](#task-coverage) | Find code that tests do not cover. |
| [`docs`](#task-docs) | Preview documentation while editing. |
| [`docs-deploy`](#task-docs-deploy) | Publish the documentation to GitHub Pages (maintainers). |
| [`format`](#task-format) | Format Python code and apply automatic lint fixes. |
| [`fuzz`](#task-fuzz) | Search for static analysis failures with generated code. |
| [`publish`](#task-publish) | Upload built distributions to PyPI (maintainers). |
| [`release`](#task-release) | Tag and publish a new version (maintainers). |
| [`test`](#task-test) | Check behavior after changing code. |

[](){#task-build}

### `build`

Before a release, run `make build` to check that source and wheel distributions can be built. The resulting files are written to `dist/`.

::: duties.build
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-changelog}

### `changelog`

When preparing a release, run `make changelog` to generate an entry from commit messages. Review the changes in `CHANGELOG.md` before releasing.

::: duties.changelog
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-check}

### `check`

Before opening a pull request, run `make check` to find quality, typing, documentation, security, and API compatibility issues.

::: duties.check
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-check-api}

### `check-api`

After changing a public signature, run `make check-api` to compare both packages against their latest Git tag. Review any reported breakages.

::: duties.check_api
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-check-docs}

### `check-docs`

After editing documentation or docstrings, run `make check-docs` to catch build warnings. A successful build writes the site to `site/`.

::: duties.check_docs
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-check-quality}

### `check-quality`

After editing Python code, run `make check-quality` to find lint violations. Fix the reported issues before submitting your changes.

::: duties.check_quality
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-check-security}

### `check-security`

After changing dependencies or GitHub Actions workflows, run these audits to find known vulnerabilities and workflow security issues:

```bash
make check-security
```

::: duties.check_security
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-check-types}

### `check-types`

After changing annotations or return values, run `make check-types` to find type errors across the configured Python versions.

::: duties.check_types
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-coverage}

### `coverage`

After running tests, run `make coverage` to identify missing test cases. Open `htmlcov/index.html` to see which lines were not executed.

::: duties.coverage
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-docs}

### `docs`

While editing documentation, run `make docs` and open <http://localhost:8000>. The local preview updates when you save changes.

::: duties.docs
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-docs-deploy}

### `docs-deploy`

When publishing documentation independently of a release, maintainers can run `make docs-deploy`. This builds the site and pushes it to GitHub Pages.

::: duties.docs_deploy
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-format}

### `format`

Before checking Python changes, run `make format` to apply formatting and automatic lint fixes. Review the resulting diff before committing.

::: duties.format
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-fuzz}

### `fuzz`

When investigating static analysis failures, generate a small set of Python modules and check whether Griffe can visit them:

```bash
make fuzz size=5
```

To reproduce a failure, pass its seed, for example `make fuzz seeds=12345`. Failing examples are minimized and saved in the system temporary directory.

::: duties.fuzz
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-publish}

### `publish`

After building release distributions, maintainers can run `make publish` to upload files from `dist/` to PyPI.

::: duties.publish
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-release}

### `release`

After reviewing the changelog, maintainers can publish the corresponding version with:

```bash
make release version=7.8.9
```

Replace `7.8.9` with the version in the changelog. This task commits, tags, pushes, publishes distributions, and deploys documentation. See the [release process](workflow.md#release-process) for the full procedure.

::: duties.release
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

[](){#task-test}

### `test`

After fixing a bug, run `make test` to check for regressions across the configured Python versions.

To focus on a particular area in the default environment, pass Pytest arguments through `make run`:

```bash
make run duty test -- -k test_finder
```

::: duties.test
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false
