
# Management commands

The entry-point to run commands to manage the project is our Python `make` script, located in the `scripts` folder. You can either call it directly with `./scripts/make`, or you can use [direnv](https://direnv.net/) to add the script to your command line path. Once direnv is installed and hooked into your shell, allow it once for this directory with `direnv allow`. Now you can directly call the Python script with `make`. The `Makefile` is just here to provide auto-completion.

Try typing `make` or `make help` to show the available commands.

```console exec="1" source="console"
$ alias make="$PWD/scripts/make"; cd  # markdown-exec: hide
$ make
```

## Commands

Commands are always available: they don't require any Python dependency to be installed.

### `setup`

::: make.setup
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `help`

::: make.help
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `run`

::: make.run
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `multirun`

::: make.multirun
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `allrun`

::: make.allrun
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `3.x`

::: make.run3x
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `clean`

::: make.clean
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `vscode`

::: make.vscode
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

### `build`

::: duties.build
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `changelog`

::: duties.changelog
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `check`

::: duties.check
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `check-api`

::: duties.check_api
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `check-docs`

::: duties.check_docs
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `check-quality`

::: duties.check_quality
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `check-types`

::: duties.check_types
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `coverage`

::: duties.coverage
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `docs`

::: duties.docs
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `docs-deploy`

::: duties.docs_deploy
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `format`

::: duties.format
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `fuzz`

::: duties.fuzz
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `publish`

::: duties.publish
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `release`

::: duties.release
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false

### `test`

::: duties.test
    options:
        heading_level: 3
        show_root_heading: false
        show_root_toc_entry: false
        separate_signature: false
        parameter_headings: false
