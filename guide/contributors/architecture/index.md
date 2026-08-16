# Project architecture

This document describes how the project is architectured, both regarding boilerplate and actual code. We start by giving an overview of the project's contents:

```
📁 .git/
📁 .github/ # (1)!
📁 .venv/ # (2)!
📁 .venvs/ # (3)!
📁 .vscode/ # (4)!
📁 .zed/ # (5)!
📁 config/ # (6)!
📁 docs/ # (7)!
📁 htmlcov/ # (8)!
📁 packages/ # (9)!
📁 scripts/ # (10)!
📁 site/ # (11)!
 .copier-answers.yml # (12)!
 .envrc # (13)!
 .gitignore
 CHANGELOG.md
 CODE_OF_CONDUCT.md
 CONTRIBUTING.md
 LICENSE
 Makefile # (14)!
 README.md
 duties.py # (15)!
 logo.svg
 mkdocs.yml # (16)!
 pyproject.toml # (17)!
 uv.lock
```

1. GitHub workflows, issue templates and other configuration.

   ```
   📁 ISSUE_TEMPLATE/ # (1)!
   📁 workflows/ # (2)!
    FUNDING.yml
    pull_request_template.md
   ```

   1. ```
       1-bug.md
       2-feature.md
       3-docs.md
       4-change.md
       config.yml
      ```
   1. ```
       ci.yml
       release.yml
       sponsors.yml
      ```

1. The default virtual environment (git-ignored). See make setup command.

1. The virtual environments for all supported Python versions (git-ignored). See make setup command.

1. The configuration for VSCode (git-ignored). See make vscode command.

   ```
    configurationCache.log
    dryrun.log
    launch.json
    settings.json
    targets.log
    tasks.json
   ```

1. ```
    debug.json
    settings.json
    tasks.json
   ```

1. Contains our tooling configuration. See [Scripts, configuration](#scripts-configuration).

   ```
   📁 vscode/ # (1)!
    coverage.ini
    git-changelog.toml
    pytest.ini
    ruff.toml
    ty.toml
   ```

   1. ```
       launch.json
       settings.json
       tasks.json
      ```

1. Documentation sources (Markdown pages). See make docs task.

   ```
   📁 .overrides/ # (1)!
   📁 css/ # (2)!
   📁 extensions/ # (3)!
   📁 guide/ # (4)!
   📁 img/ # (5)!
   📁 js/ # (6)!
   📁 reference/ # (7)!
    alternatives.md
    changelog.md
    code-of-conduct.md
    community.md
    contributing.md
    credits.md
    downstream-projects.md
    extensions.md
    getting-help.md
    getting-started.md
    guide.md
    index.md
    installation.md
    introduction.md
    license.md
    logo.svg
    playground.md
    reference.md
    schema-docstrings-options.json
    schema.json
   ```

   1. Customization of [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)' templates.

      ```
      📁 partials/ # (1)!
       main.html
      ```

      1. ```
          comments.html
          path-item.html
         ```

   1. ```
       custom.css
       material.css
       mkdocstrings.css
      ```

   1. ```
      📁 built-in/ # (1)!
      📁 official/ # (2)!
      📁 third-party/ # (3)!
       built-in.md
       official.md
       third-party.md
      ```

      1. ```
          dataclasses.md
          unpack-typeddict.md
         ```
      1. ```
          autodocstringstyle.md
          inherited-docstrings.md
          public-redundant-aliases.md
          public-wildcard-imports.md
          pydantic.md
          runtime-objects.md
          sphinx.md
          typingdoc.md
          warnings-deprecated.md
         ```
      1. ```
          docstring-inheritance.md
          fastapi.md
          fieldz.md
          generics.md
          inherited-method-crossrefs.md
          modernized-annotations.md
         ```

   1. ```
      📁 contributors/ # (1)!
      📁 users/ # (2)!
       contributors.md
       users.md
      ```

      1. ```
          architecture.md
          commands.md
          setup.md
          workflow.md
         ```
      1. ```
         📁 how-to/ # (1)!
         📁 recommendations/ # (2)!
          checking.md
          extending.md
          loading.md
          navigating.md
          serializing.md
         ```
         1. ```
             parse-docstrings.md
             selectively-inspect.md
             set-docstring-styles.md
             set-git-info.md
             support-decorators.md
            ```
         1. ```
             docstrings.md
             public-apis.md
             python-code.md
            ```

   1. ```
       favicon.ico
       gha_annotations_1.png
       gha_annotations_2.png
      ```

   1. ```
       feedback.js
      ```

   1. ```
      📁 api/ # (1)!
       api.md
       cli.md
       docstrings.md
      ```

      1. Python API reference, injected with [mkdocstrings](https://mkdocstrings.github.io/).

         ```
         📁 docstrings/ # (1)!
         📁 models/ # (2)!
          agents.md
          checks.md
          cli.md
          docstrings.md
          exceptions.md
          expressions.md
          extensions.md
          finder.md
          helpers.md
          loaders.md
          loggers.md
          models.md
          serializers.md
         ```

         1. ```
             models.md
             parsers.md
            ```
         1. ```
             alias.md
             attribute.md
             class.md
             function.md
             module.md
             type_alias.md
            ```

1. HTML report for Python code coverage (git-ignored), integrated in the [Coverage report](https://mkdocstrings.github.io/griffe/guide/contributors/coverage/index.md) page. See make coverage task.

1. ```
   📁 griffecli/ # (1)!
   📁 griffelib/ # (2)!
   ```

   1. ```
      📁 src/ # (1)!
      📁 tests/ # (2)!
       pyproject.toml
      ```
      1. ```
         📁 griffecli/ # (1)!
         ```

         1. ```
            📁 _internal/ # (1)!
             __init__.py
             __main__.py
             py.typed
            ```
            1. ```
                __init__.py
                cli.py
               ```

      1. Our test suite. See [Tests](#tests).

         ```
          __init__.py
          test_cli.py
         ```
   1. ```
      📁 src/ # (1)!
      📁 tests/ # (2)!
       pyproject.toml
      ```
      1. ```
         📁 griffe/ # (1)!
         ```

         1. ```
            📁 _internal/ # (1)!
             __init__.py
             __main__.py
             py.typed
            ```
            1. Our internal API, hidden from users. See [Program structure](#program-structure).

               ```
               📁 agents/ # (1)!
               📁 docstrings/ # (2)!
               📁 extensions/ # (3)!
                __init__.py
                c3linear.py
                collections.py
                debug.py
                diff.py
                encoders.py
                enumerations.py
                exceptions.py
                expressions.py
                finder.py
                git.py
                helpers.py
                importer.py
                loader.py
                logger.py
                merger.py
                mixins.py
                models.py
                stats.py
               ```

               1. ```
                  📁 nodes/ # (1)!
                   __init__.py
                   inspector.py
                   visitor.py
                  ```
                  1. ```
                      __init__.py
                      assignments.py
                      ast.py
                      docstrings.py
                      exports.py
                      imports.py
                      parameters.py
                      runtime.py
                      values.py
                     ```
               1. ```
                   __init__.py
                   auto.py
                   google.py
                   models.py
                   numpy.py
                   parsers.py
                   sphinx.py
                   utils.py
                  ```
               1. ```
                   __init__.py
                   base.py
                   dataclasses.py
                   unpack_typeddict.py
                  ```

      1. Our test suite. See [Tests](#tests).

         ```
         📁 fixtures/
         📁 test_docstrings/ # (1)!
         📁 test_extensions/ # (2)!
          __init__.py
          conftest.py
          helpers.py
          test_api.py
          test_diff.py
          test_encoders.py
          test_expressions.py
          test_finder.py
          test_functions.py
          test_git.py
          test_inheritance.py
          test_inspector.py
          test_loader.py
          test_merger.py
          test_mixins.py
          test_models.py
          test_nodes.py
          test_public_api.py
          test_stdlib.py
          test_visitor.py
         ```

         1. ```
             __init__.py
             conftest.py
             helpers.py
             test_google.py
             test_numpy.py
             test_sphinx.py
             test_warnings.py
            ```
         1. ```
             __init__.py
             test_base.py
             test_dataclasses.py
             test_unpack_typeddict.py
            ```

1. Our different scripts. See [Scripts, configuration](#scripts-configuration).

   ```
    gen_credits.py
    gen_griffe_json.py
    gen_structure_docs.py
    get_version.py
    make
    make.py
   ```

1. Documentation site, built with `make run mkdocs build` (git-ignored).

1. The answers file generated by [Copier](https://copier.readthedocs.io/en/stable/). See [Boilerplate](#boilerplate).

1. The environment configuration, automatically sourced by [direnv](https://direnv.net/). See [commands](https://mkdocstrings.github.io/griffe/guide/contributors/commands/index.md).

1. A dummy makefile, only there for auto-completion. See [commands](https://mkdocstrings.github.io/griffe/guide/contributors/commands/index.md).

1. Our project tasks, written with [duty](https://pawamoy.github.io/duty). See Tasks.

1. The build configuration for our docs. See make docs task.

1. The project metadata and production dependencies.

## Boilerplate

This project's skeleton (the file-tree shown above) is actually generated from a [Copier](https://copier.readthedocs.io/en/stable/) template called [copier-uv](https://pawamoy.github.io/copier-uv/). When generating the project, Copier asks a series of questions (configured by the template itself), and the answers are used to render the file and directory names, as well as the file contents. Copier also records answers in the `.copier-answers.yml` file, allowing to update the project with latest changes from the template while reusing previous answers.

To update the project (in order to apply latest changes from the template), we use the following command:

```
copier update --trust --skip-answered
```

## Scripts, configuration

We have a few scripts that let us manage the various maintenance aspects for this project. The entry-point is the `make` script located in the `scripts` folder. It doesn't need any dependency to be installed to run. See [Management commands](https://mkdocstrings.github.io/griffe/guide/contributors/commands/index.md) for more information.

The `make` script can also invoke what we call "tasks". Tasks need our development dependencies to be installed to run. These tasks are written in the `duties.py` file, and the development dependencies are listed in `devdeps.txt`.

The tools used in tasks have their configuration files stored in the `config` folder, to unclutter the root of the repository. The tasks take care of calling the tools with the right options to locate their respective configuration files.

## Sources

Sources are located in the `packages/` subfolders, following the [src-layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/). We use [Hatch](https://hatch.pypa.io/latest/) to build source and wheel distributions, and configure it in `pyproject.toml`.

## Tests

Our test suite is located in the `tests` folder. It is located outside of the sources as to not pollute distributions (it would be very wrong to publish a `tests` package as part of our distributions, since this name is extremely common), or worse, the public API. The `tests` folder is however included in our source distributions (`.tar.gz`), alongside most of our metadata and configuration files. Check out our `pyproject.toml` files to get the full list of files included in our source distributions for every individual package within the `packages/` folder.

The test suite is based on [pytest](https://docs.pytest.org/en/8.2.x/). Test modules reflect our internal API structure, and except for a few test modules that test specific aspects of our API, each test module tests the logic from the corresponding module in the internal API. For example, `test_finder.py` tests code of the `griffe._internal.finder` internal module, while `test_functions` tests our ability to extract correct information from function signatures, statically. The general rule of thumb when writing new tests is to mirror the internal API. If a test touches to many aspects of the loading process, it can be added to the `test_loader` test module.

## Program structure

Griffe is split into two pieces: the library and the CLI.

Each of them has an internal API contained within an `_internal` folder:

- `packages/griffelib/src/griffe/_internal` for the library,
- `packages/griffecli/src/griffecli/_internal` for the CLI.

Griffe can be installed in library-only mode, which means that the CLI package from `packages/griffecli` is not present. Library-only mode can be preferred if the user does not utilize the CLI functionality of Griffe and does not want to incorporate its dependencies.

The top-level `packages/griffelib/src/griffe/__init__.py` module exposes all the public API available: it always re-exports internal objects from various submodules of `griffe._internal` and, if the CLI is installed, it re-exports the public API of `griffecli` as well.

Users then import `griffe` directly, or import objects from it. If they don't have `griffecli` installed, they cannot import the CLI-related functionality, such as griffecli.check.

We'll be honest: our code organization is not the most elegant, but it works Have a look at the following module dependency graph, which will basically tell you nothing except that we have a lot of inter-module dependencies. Arrows read as "imports from". The code base is generally pleasant to work with though.

*You can zoom and pan all diagrams on this page with mouse inputs.*

The following sections are generated automatically by iterating on the modules of our public and internal APIs respectively, and extracting the comment blocks at the top of each module. The comment blocks are addressed to readers of the code (maintainers, contributors), while module docstrings are addressed to users of the API. Module docstrings in our internal API are never written, because our module layout is hidden, and therefore modules aren't part of the public API, so it doesn't make much sense to write "user documentation" in them.

### CLI entrypoint

#### `griffe.__main__`

SPDX-License-Identifier: ISC

### Public API

#### `griffe`

SPDX-License-Identifier: ISC

### Internal API

SPDX-License-Identifier: ISC

#### `agents`

SPDX-License-Identifier: ISC

##### `inspector.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `nodes`

SPDX-License-Identifier: ISC

###### `assignments.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

###### `ast.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

###### `docstrings.py`

SPDX-License-Identifier: ISC

###### `exports.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

###### `imports.py`

SPDX-License-Identifier: ISC

###### `parameters.py`

SPDX-License-Identifier: ISC

###### `runtime.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

###### `values.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `visitor.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `c3linear.py`

This module contains a single function, `c3linear_merge`. The function is generic enough to be in its own module.

- Copyright (c) 2019 Vitaly R. Samigullin
- Adapted from <https://github.com/pilosus/c3linear>
- Adapted from <https://github.com/tristanlatr/pydocspec>

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `collections.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `debug.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `diff.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `docstrings`

SPDX-License-Identifier: ISC

##### `auto.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `google.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `models.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `numpy.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `parsers.py`

SPDX-License-Identifier: ISC

##### `sphinx.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `utils.py`

SPDX-License-Identifier: ISC

#### `encoders.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `enumerations.py`

SPDX-License-Identifier: ISC

#### `exceptions.py`

SPDX-License-Identifier: ISC

#### `expressions.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `extensions`

SPDX-License-Identifier: ISC

##### `base.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `dataclasses.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `unpack_typeddict.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `finder.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `git.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `helpers.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `importer.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `loader.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `logger.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `merger.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `mixins.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `models.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `stats.py`

SPDX-License-Identifier: ISC

xml version="1.0" encoding="UTF-8" standalone="no"?
