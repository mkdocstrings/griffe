# Welcome

> Griffe, pronounced "grif" (`/ɡʁif/`), is a french word that means "claw", but also "signature" in a familiar way. "On reconnaît bien là sa griffe."

- **Getting started**

  ______________________________________________________________________

  Learn how to quickly install and use Griffe.

  [Installation](installation/) [Introduction](introduction/)

- **Deep dive**

  ______________________________________________________________________

  Learn everything you can do with Griffe.

  [Guide](guide/users/) [API reference](reference/api/)

## What is Griffe?

Griffe is a Python tool and library that gives you signatures for entire Python programs. It extracts the structure, the frame, the skeleton of your project, to generate API documentation or find breaking changes in your API.

Griffe can be used as a Python library. For example, the [Python handler](https://mkdocstrings.github.io/python) of [mkdocstrings](https://mkdocstrings.github.io/) uses Griffe to collect API data and render API documentation in HTML. Griffe can also be used on the command-line, to load and serialize your API data to JSON, or find breaking changes in your API since the previous version of your library.

Serializing as JSON

```
$ griffe dump griffe -ssrc -r 2>/dev/null | head -n29
{
  "griffe": {
    "deprecated": null,
    "docstring": {
      "endlineno": 161,
      "lineno": 5,
      "value": "Griffe package.\n\nSignatures for entire Python programs.\nExtract the structure, the frame, the skeleton of your project,\nto generate API documentation or find breaking changes in your API.\n\nThe entirety of the public API is exposed here, in the top-level `griffe` module.\n\nAll messages written to standard output or error are logged using the `logging` module.\nOur logger's name is set to `\"griffe\"` and is public (you can rely on it).\nYou can obtain the logger from the standard `logging` module: `logging.getLogger(\"griffe\")`.\nActual logging messages are not part of the public API (they might change without notice).\n\nRaised exceptions throughout the package are part of the public API (you can rely on them).\nTheir actual messages are not part of the public API (they might change without notice).\n\nThe following paragraphs will help you discover the package's content.\n\n## CLI entrypoints\n\nGriffe provides a command-line interface (CLI) to interact with the package. The CLI entrypoints can be called from Python code.\n\n- [`griffe.main`][]: Run the main program.\n- [`griffe.check`][]: Check for API breaking changes in two versions of the same package.\n- [`griffe.dump`][]: Load packages data and dump it as JSON.\n\n## Loaders\n\nTo load API data, Griffe provides several high-level functions.\n\n- [`griffe.load`][]: Load and return a Griffe object.\n- [`griffe.load_git`][]: Load and return a module from a specific Git reference.\n- [`griffe.load_pypi`][]: Load and return a module from a specific package version downloaded using pip.\n\n## Models\n\nThe data loaded by Griffe is represented by several classes.\n\n- [`griffe.Module`][]: The class representing a Python module.\n- [`griffe.Class`][]: The class representing a Python class.\n- [`griffe.Function`][]: The class representing a Python function or method.\n- [`griffe.Attribute`][]: The class representing a Python attribute.\n- [`griffe.Alias`][]: This class represents an alias, or indirection, to an object declared in another module.\n\nAdditional classes are available to represent other concepts.\n\n- [`griffe.Decorator`][]: This class represents a decorator.\n- [`griffe.Parameters`][]: This class is a container for parameters.\n- [`griffe.Parameter`][]: This class represent a function parameter.\n\n## Agents\n\nGriffe is able to analyze code both statically and dynamically, using the following \"agents\".\nHowever most of the time you will only need to use the loaders above.\n\n- [`griffe.visit`][]: Parse and visit a module file.\n- [`griffe.inspect`][]: Inspect a module.\n\n## Serializers\n\nGriffe can serizalize data to dictionary and JSON.\n\n- [`griffe.Object.as_json`][griffe.Object.as_json]\n- [`griffe.Object.from_json`][griffe.Object.from_json]\n- [`griffe.JSONEncoder`][]: JSON encoder for Griffe objects.\n- [`griffe.json_decoder`][]: JSON decoder for Griffe objects.\n\n## API checks\n\nGriffe can compare two versions of the same package to find breaking changes.\n\n- [`griffe.find_breaking_changes`][]: Find breaking changes between two versions of the same API.\n- [`griffe.Breakage`][]: Breakage classes can explain what broke from a version to another.\n\n## Extensions\n\nGriffe supports extensions. You can create your own extension by subclassing the `griffe.Extension` class.\n\n- [`griffe.load_extensions`][]: Load configured extensions.\n- [`griffe.Extension`][]: Base class for Griffe extensions.\n\n## Docstrings\n\nGriffe can parse docstrings into structured data.\n\nMain class:\n\n- [`griffe.Docstring`][]: This class represents docstrings.\n\nDocstring section and element classes all start with `Docstring`.\n\nDocstring parsers:\n\n- [`griffe.parse`][]: Parse the docstring.\n- [`griffe.parse_auto`][]: Parse a docstring by automatically detecting the style it uses.\n- [`griffe.parse_google`][]: Parse a Google-style docstring.\n- [`griffe.parse_numpy`][]: Parse a Numpydoc-style docstring.\n- [`griffe.parse_sphinx`][]: Parse a Sphinx-style docstring.\n\n## Exceptions\n\nGriffe uses several exceptions to signal errors.\n\n- [`griffe.GriffeError`][]: The base exception for all Griffe errors.\n- [`griffe.LoadingError`][]: Exception for loading errors.\n- [`griffe.NameResolutionError`][]: Exception for names that cannot be resolved in a object scope.\n- [`griffe.UnhandledEditableModuleError`][]: Exception for unhandled editables modules, when searching modules.\n- [`griffe.UnimportableModuleError`][]: Exception for modules that cannot be imported.\n- [`griffe.AliasResolutionError`][]: Exception for aliases that cannot be resolved.\n- [`griffe.CyclicAliasError`][]: Exception raised when a cycle is detected in aliases.\n- [`griffe.LastNodeError`][]: Exception raised when trying to access a next or previous node.\n- [`griffe.RootNodeError`][]: Exception raised when trying to use siblings properties on a root node.\n- [`griffe.BuiltinModuleError`][]: Exception raised when trying to access the filepath of a builtin module.\n- [`griffe.ExtensionError`][]: Base class for errors raised by extensions.\n- [`griffe.ExtensionNotLoadedError`][]: Exception raised when an extension could not be loaded.\n- [`griffe.GitError`][]: Exception raised for errors related to Git.\n\n# Expressions\n\nGriffe stores snippets of code (attribute values, decorators, base class, type annotations) as expressions.\nExpressions are basically abstract syntax trees (AST) with a few differences compared to the nodes returned by [`ast`][].\nGriffe provides a few helpers to extract expressions from regular AST nodes.\n\n- [`griffe.get_annotation`][]: Get a type annotation as expression.\n- [`griffe.get_base_class`][]: Get a base class as expression.\n- [`griffe.get_condition`][]: Get a condition as expression.\n- [`griffe.get_expression`][]: Get an expression from an AST node.\n- [`griffe.safe_get_annotation`][]: Get a type annotation as expression, safely (returns `None` on error).\n- [`griffe.safe_get_base_class`][]: Get a base class as expression, safely (returns `None` on error).\n- [`griffe.safe_get_condition`][]: Get a condition as expression, safely (returns `None` on error).\n- [`griffe.safe_get_expression`][]: Get an expression from an AST node, safely (returns `None` on error).\n\nThe base class for expressions.\n\n- [`griffe.Expr`][]\n\nExpression classes all start with `Expr`.\n\n# Loggers\n\nIf you want to log messages from extensions, get a logger with `get_logger`.\nThe `logger` attribute is used by Griffe itself. You can use it to temporarily disable Griffe logging.\n\n- [`griffe.logger`][]: Our global logger, used throughout the library.\n- [`griffe.get_logger`][]: Create and return a new logger instance.\n\n# Helpers\n\nTo test your Griffe extensions, or to load API data from code in memory, Griffe provides the following helpers.\n\n- [`griffe.temporary_pyfile`][]: Create a Python file containing the given code in a temporary directory.\n- [`griffe.temporary_pypackage`][]: Create a package containing the given modules in a temporary directory.\n- [`griffe.temporary_visited_module`][]: Create and visit a temporary module with the given code.\n- [`griffe.temporary_visited_package`][]: Create and visit a temporary package.\n- [`griffe.temporary_inspected_module`][]: Create and inspect a temporary module with the given code.\n- [`griffe.temporary_inspected_package`][]: Create and inspect a temporary package."
    },
    "exports": [
      "DEFAULT_LOG_LEVEL",
      "Alias",
      "AliasResolutionError",
      "Attribute",
      "AttributeChangedTypeBreakage",
      "AttributeChangedValueBreakage",
      "Breakage",
      "BreakageKind",
      "BuiltinModuleError",
      "Class",
      "ClassRemovedBaseBreakage",
      "CyclicAliasError",
      "DataclassesExtension",
      "Decorator",
      "DelMembersMixin",
      "Docstring",
      "DocstringAdmonition",
      "DocstringAttribute",
      "DocstringClass",
      "DocstringDeprecated",

```

Checking for API breaking changes

```
$ griffe check griffe -ssrc -b0.46.0.1.2.0 -a0.45.0.1.2.0 --verbose
src/griffe/mixins.py:303: ObjectAliasMixin.is_exported:
Public object points to a different kind of object:
  Old: function
  New: attribute

src/griffe/mixins.py:353: ObjectAliasMixin.is_public:
Public object points to a different kind of object:
  Old: function
  New: attribute

src/griffe/dataclasses.py:520: Object.has_labels(labels):
Parameter kind was changed:
  Old: positional or keyword
  New: variadic positional

src/griffe/diff.py:571: find_breaking_changes(ignore_private):
Parameter default was changed:
  Old: True
  New: _sentinel

src/griffe/extensions/base.py:463: load_extensions(exts):
Parameter kind was changed:
  Old: positional or keyword
  New: variadic positional

src/griffe/dataclasses.py:1073: Alias.has_labels(labels):
Parameter kind was changed:
  Old: positional or keyword
  New: variadic positional

```

[Playground](playground/) [Join our Gitter channel](https://app.gitter.im/#/room/#mkdocstrings_griffe:gitter.im)
