# Project architecture

This document describes how the project is architectured, both regarding boilerplate and actual code. We start by giving an overview of the project's contents:

```
📁 .git/
📁 .github/ # (1)!
📁 .venv/ # (2)!
📁 .venvs/ # (3)!
📁 .vscode/ # (4)!
📁 config/ # (5)!
📁 docs/ # (6)!
📁 htmlcov/ # (7)!
📁 scripts/ # (8)!
📁 src/ # (9)!
📁 tests/ # (10)!
 .copier-answers.yml # (11)!
 .envrc # (12)!
 .gitignore
 CHANGELOG.md
 CODE_OF_CONDUCT.md
 CONTRIBUTING.md
 LICENSE
 Makefile # (13)!
 README.md
 duties.py # (14)!
 logo.svg
 mkdocs.yml # (15)!
 pyproject.toml # (16)!
 uv.lock

```

1. GitHub workflows, issue templates and other configuration.

   ```
   📁 ISSUE_TEMPLATE/ # (1)!
   📁 workflows/ # (2)!
    FUNDING.yml

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

      ```

1. The default virtual environment (git-ignored). See make setup command.

1. The virtual environments for all supported Python versions (git-ignored). See make setup command.

1. The configuration for VSCode (git-ignored). See make vscode command.

   ```
    launch.json
    settings.json
    tasks.json

   ```

1. Contains our tooling configuration. See [Scripts, configuration](#scripts-configuration).

   ```
   📁 vscode/ # (1)!
    coverage.ini
    git-changelog.toml
    mypy.ini
    pytest.ini
    ruff.toml

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
   📁 insiders/ # (6)!
   📁 js/ # (7)!
   📁 reference/ # (8)!
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
       insiders.css
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
       changelog.md
       goals.yml
       index.md
       installation.md

      ```

   1. ```
       feedback.js
       insiders.js

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
          git.md
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

1. HTML report for Python code coverage (git-ignored), integrated in the [Coverage report](../coverage/) page. See make coverage task.

1. Our different scripts. See [Scripts, configuration](#scripts-configuration).

   ```
    gen_credits.py
    gen_griffe_json.py
    gen_structure_docs.py
    get_version.py
    insiders.py
    make
    make.py

   ```

1. The source of our Python package(s). See [Sources](#sources) and [Program structure](#program-structure).

   ```
   📁 _griffe/ # (1)!
   📁 griffe/ # (2)!

   ```

   1. Our internal API, hidden from users. See [Program structure](#program-structure).

      ```
      📁 agents/ # (1)!
      📁 docstrings/ # (2)!
      📁 extensions/ # (3)!
       __init__.py
       c3linear.py
       cli.py
       collections.py
       debug.py
       diff.py
       encoders.py
       enumerations.py
       exceptions.py
       expressions.py
       finder.py
       git.py
       importer.py
       loader.py
       logger.py
       merger.py
       mixins.py
       models.py
       py.typed
       stats.py
       tests.py

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

         ```

   1. Our public API, exposed to users. See [Program structure](#program-structure).

      ```
       __init__.py
       __main__.py
       py.typed

      ```

1. Our test suite. See [Tests](#tests).

   ```
   📁 fixtures/
   📁 test_docstrings/ # (1)!
    __init__.py
    conftest.py
    helpers.py
    test_api.py
    test_cli.py
    test_diff.py
    test_encoders.py
    test_expressions.py
    test_extensions.py
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

1. The answers file generated by [Copier](https://copier.readthedocs.io/en/stable/). See [Boilerplate](#boilerplate).

1. The environment configuration, automatically sourced by [direnv](https://direnv.net/). See [commands](../commands/).

1. A dummy makefile, only there for auto-completion. See [commands](../commands/).

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

We have a few scripts that let us manage the various maintenance aspects for this project. The entry-point is the `make` script located in the `scripts` folder. It doesn't need any dependency to be installed to run. See [Management commands](../commands/) for more information.

The `make` script can also invoke what we call "tasks". Tasks need our development dependencies to be installed to run. These tasks are written in the `duties.py` file, and the development dependencies are listed in `devdeps.txt`.

The tools used in tasks have their configuration files stored in the `config` folder, to unclutter the root of the repository. The tasks take care of calling the tools with the right options to locate their respective configuration files.

## Sources

Sources are located in the `src` folder, following the [src-layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/). We use [PDM-Backend](https://backend.pdm-project.org/) to build source and wheel distributions, and configure it in `pyproject.toml` to search for packages in the `src` folder.

## Tests

Our test suite is located in the `tests` folder. It is located outside of the sources as to not pollute distributions (it would be very wrong to publish a `tests` package as part of our distributions, since this name is extremely common), or worse, the public API. The `tests` folder is however included in our source distributions (`.tar.gz`), alongside most of our metadata and configuration files. Check out `pyproject.toml` to get the full list of files included in our source distributions.

The test suite is based on [pytest](https://docs.pytest.org/en/8.2.x/). Test modules reflect our internal API structure, and except for a few test modules that test specific aspects of our API, each test module tests the logic from the corresponding module in the internal API. For example, `test_finder.py` tests code of the `_griffe.finder` internal module, while `test_functions` tests our ability to extract correct information from function signatures, statically. The general rule of thumb when writing new tests is to mirror the internal API. If a test touches to many aspects of the loading process, it can be added to the `test_loader` test module.

## Program structure

Griffe is composed of two packages:

- `_griffe`, which is our internal API, hidden from users
- `griffe`, which is our public API, exposed to users

When installing the `griffe` distribution from PyPI.org (or any other index where it is published), both the `_griffe` and `griffe` packages are installed. Users then import `griffe` directly, or import objects from it. The top-level `griffe/__init__.py` module exposes all the public API, by importing the internal objects from various submodules of `_griffe`.

We'll be honest: our code organization is not the most elegant, but it works Have a look at the following module dependency graph, which will basically tell you nothing except that we have a lot of inter-module dependencies. Arrows read as "imports from". The code base is generally pleasant to work with though.

*You can zoom and pan all diagrams on this page with mouse inputs.*

The following sections are generated automatically by iterating on the modules of our public and internal APIs respectively, and extracting the comment blocks at the top of each module. The comment blocks are addressed to readers of the code (maintainers, contributors), while module docstrings are addressed to users of the API. Module docstrings in our internal API are never written, because our module layout is hidden, and therefore modules aren't part of the public API, so it doesn't make much sense to write "user documentation" in them.

### CLI entrypoint

#### `griffe.__main__`

Entry-point module, in case you use `python -m griffe`.

Why does this file exist, and why `__main__`? For more info, read:

- <https://www.python.org/dev/peps/pep-0338/>
- <https://docs.python.org/3/using/cmdline.html#cmdoption-m>

### Public API

#### `griffe`

This top-level module imports all public names from the package, and exposes them as public objects. We have tests to make sure no object is forgotten in this list.

### Internal API

The internal API layout doesn't follow any particular paradigm: we simply organize code in different modules, depending on what the code is used for.

#### `agents`

These modules contain the different agents that are able to extract data.

##### `inspector.py`

This module contains our dynamic analysis agent, capable of inspecting modules and objects in memory, at runtime.

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `nodes`

These submodules contain utilities for working with AST and object nodes.

###### `assignments.py`

This module contains utilities for extracting information from assignment nodes.

xml version="1.0" encoding="UTF-8" standalone="no"?

###### `ast.py`

This module contains utilities for navigating AST nodes.

xml version="1.0" encoding="UTF-8" standalone="no"?

###### `docstrings.py`

This module contains utilities for extracting docstrings from nodes.

###### `exports.py`

This module contains utilities for extracting exports from `__all__` assignments.

xml version="1.0" encoding="UTF-8" standalone="no"?

###### `imports.py`

This module contains utilities for working with imports and relative imports.

###### `parameters.py`

This module contains utilities for extracting information from parameter nodes.

###### `runtime.py`

This module contains utilities for extracting information from runtime objects.

xml version="1.0" encoding="UTF-8" standalone="no"?

###### `values.py`

This module contains utilities for extracting attribute values.

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `visitor.py`

This module contains our static analysis agent, capable of parsing and visiting sources, statically.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `c3linear.py`

This module contains a single function, `c3linear_merge`. The function is generic enough to be in its own module.

- Copyright (c) 2019 Vitaly R. Samigullin
- Adapted from <https://github.com/pilosus/c3linear>
- Adapted from <https://github.com/tristanlatr/pydocspec>

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `cli.py`

This module contains all CLI-related things. Why does this file exist, and why not put this in `__main__`?

We might be tempted to import things from `__main__` later, but that will cause problems; the code will get executed twice:

- When we run `python -m griffe`, Python will execute `__main__.py` as a script. That means there won't be any `griffe.__main__` in `sys.modules`.
- When you import `__main__` it will get executed again (as a module) because there's no `griffe.__main__` in `sys.modules`.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `collections.py`

This module contains collection-related classes, which are used throughout the API.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `debug.py`

This module is here to help users report bugs. It provides a function to print environment information, which is called from the public `griffe.debug` module (when called with `python -m griffe.debug`) or thanks to the `--debug-info` CLI flag.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `diff.py`

This module exports "breaking changes" related utilities. The logic here is to iterate on objects and their members recursively, to yield found breaking changes.

The breakage class definitions might sound a bit verbose, but declaring them this way helps with (de)serialization, which we don't use yet, but could use in the future.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `docstrings`

These submodules define models and parsers for docstrings.

##### `google.py`

This module defines functions to parse Google-style docstrings into structured data.

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `models.py`

This module contains the models for storing docstrings structured data.

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `numpy.py`

This module defines functions to parse Numpy-style docstrings into structured data.

Based on <https://numpydoc.readthedocs.io/en/latest/format.html>, it seems Numpydoc is a superset of RST. Since fully parsing RST is a non-goal of this project, some things are stripped from the Numpydoc specification.

Rejected as non particularly Pythonic or useful as sections:

- See also: this section feels too subjective (specially crafted as a standard for Numpy itself), and there are may ways to reference related items in a docstring, depending on the chosen markup.

Rejected as naturally handled by the user-chosen markup:

- Warnings: this is just markup.
- Notes: again, just markup.
- References: again, just markup.

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `parsers.py`

This module imports all the defined parsers and provides a generic function to parse docstrings.

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `sphinx.py`

This module defines functions to parse Sphinx docstrings into structured data.

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `utils.py`

This module contains utilities for docstrings parsers.

#### `encoders.py`

This module contains data encoders/serializers and decoders/deserializers. We only support JSON for now, but might want to add more formats in the future.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `enumerations.py`

This module contains all the enumerations of the package.

#### `exceptions.py`

This module contains all the exceptions specific to Griffe.

#### `expressions.py`

This module contains the data classes that represent resolvable names and expressions. First we declare data classes for each kind of expression, mostly corresponding to Python's AST nodes. Then we declare builder methods, that iterate AST nodes and build the corresponding data classes, and two utilities `_yield` and `_join` to help iterate on expressions. Finally we declare a few public helpers to safely get expressions from AST nodes in different scenarios.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `extensions`

These submodules contain our extension system, as well as built-in extensions.

##### `base.py`

This module contains the base class for extensions and the functions to load them.

xml version="1.0" encoding="UTF-8" standalone="no"?

##### `dataclasses.py`

Built-in extension adding support for dataclasses.

This extension re-creates `__init__` methods of dataclasses during static analysis.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `finder.py`

This module contains the code allowing to find modules.

Note: It might be possible to replace a good part of this module's logic with utilities from `importlib` (however the util in question is private):

```
>>> from importlib.util import _find_spec
>>> _find_spec("griffe.agents", _find_spec("griffe", None).submodule_search_locations)
ModuleSpec(
    name='griffe.agents',
    loader=<_frozen_importlib_external.SourceFileLoader object at 0x7fa5f34e8110>,
    origin='/media/data/dev/griffe/src/griffe/agents/__init__.py',
    submodule_search_locations=['/media/data/dev/griffe/src/griffe/agents'],
)

```

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `git.py`

This module contains Git utilities, used by our load_git function, which in turn is used to load the API for different snapshots of a Git repository and find breaking changes between them.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `importer.py`

This module contains utilities to dynamically import objects. These utilities are used by our Inspector to dynamically import objects specified as Python paths, like `package.module.Class.method`.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `loader.py`

This module contains all the logic for loading API data from sources or compiled modules.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `logger.py`

This module contains the logger used throughout Griffe. The logger is actually a wrapper around the standard Python logger. We wrap it so that it is easier for other downstream libraries to patch it. For example, mkdocstrings-python patches the logger to relocate it as a child of `mkdocs.plugins` so that it fits in the MkDocs logging configuration.

We use a single, global logger because our public API is exposed in a single module, `griffe`. Extensions however should use their own logger, which is why we provide the `get_logger` function.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `merger.py`

This module contains utilities to merge stubs data and concrete data.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `mixins.py`

This module contains some mixins classes that hold shared methods of the different kinds of objects, and aliases.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `models.py`

This module contains our models definitions, to represent Python objects (and other aspects of Python APIs)... in Python.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `stats.py`

This module contains utilities to compute loading statistics, like time spent visiting modules statically or dynamically.

xml version="1.0" encoding="UTF-8" standalone="no"?

#### `tests.py`

This module contains helpers. They simplify programmatic use of Griffe, for example to load data from strings or to create temporary packages. They are particularly useful for our own tests suite.

xml version="1.0" encoding="UTF-8" standalone="no"?
