# griffe

Griffe package.

Signatures for entire Python programs. Extract the structure, the frame, the skeleton of your project, to generate API documentation or find breaking changes in your API.

The entirety of the public API is exposed here, in the top-level `griffe` module.

All messages written to standard output or error are logged using the `logging` module. Our logger's name is set to `"griffe"` and is public (you can rely on it). You can obtain the logger from the standard `logging` module: `logging.getLogger("griffe")`. Actual logging messages are not part of the public API (they might change without notice).

Raised exceptions throughout the package are part of the public API (you can rely on them). Their actual messages are not part of the public API (they might change without notice).

The following paragraphs will help you discover the package's content.

### CLI entrypoints

Griffe provides a command-line interface (CLI) to interact with the package. The CLI entrypoints can be called from Python code.

- griffe.main: Run the main program.
- griffe.check: Check for API breaking changes in two versions of the same package.
- griffe.dump: Load packages data and dump it as JSON.

### Loaders

To load API data, Griffe provides several high-level functions.

- griffe.load: Load and return a Griffe object.
- griffe.load_git: Load and return a module from a specific Git reference.
- griffe.load_pypi: Load and return a module from a specific package version downloaded using pip.

### Models

The data loaded by Griffe is represented by several classes.

- griffe.Module: The class representing a Python module.
- griffe.Class: The class representing a Python class.
- griffe.Function: The class representing a Python function or method.
- griffe.Attribute: The class representing a Python attribute.
- griffe.Alias: This class represents an alias, or indirection, to an object declared in another module.

Additional classes are available to represent other concepts.

- griffe.Decorator: This class represents a decorator.
- griffe.Parameters: This class is a container for parameters.
- griffe.Parameter: This class represent a function parameter.

### Agents

Griffe is able to analyze code both statically and dynamically, using the following "agents". However most of the time you will only need to use the loaders above.

- griffe.visit: Parse and visit a module file.
- griffe.inspect: Inspect a module.

### Serializers

Griffe can serizalize data to dictionary and JSON.

- griffe.Object.as_json
- griffe.Object.from_json
- griffe.JSONEncoder: JSON encoder for Griffe objects.
- griffe.json_decoder: JSON decoder for Griffe objects.

### API checks

Griffe can compare two versions of the same package to find breaking changes.

- griffe.find_breaking_changes: Find breaking changes between two versions of the same API.
- griffe.Breakage: Breakage classes can explain what broke from a version to another.

### Extensions

Griffe supports extensions. You can create your own extension by subclassing the `griffe.Extension` class.

- griffe.load_extensions: Load configured extensions.
- griffe.Extension: Base class for Griffe extensions.

### Docstrings

Griffe can parse docstrings into structured data.

Main class:

- griffe.Docstring: This class represents docstrings.

Docstring section and element classes all start with `Docstring`.

Docstring parsers:

- griffe.parse: Parse the docstring.
- griffe.parse_auto: Parse a docstring by automatically detecting the style it uses.
- griffe.parse_google: Parse a Google-style docstring.
- griffe.parse_numpy: Parse a Numpydoc-style docstring.
- griffe.parse_sphinx: Parse a Sphinx-style docstring.

### Exceptions

Griffe uses several exceptions to signal errors.

- griffe.GriffeError: The base exception for all Griffe errors.
- griffe.LoadingError: Exception for loading errors.
- griffe.NameResolutionError: Exception for names that cannot be resolved in a object scope.
- griffe.UnhandledEditableModuleError: Exception for unhandled editables modules, when searching modules.
- griffe.UnimportableModuleError: Exception for modules that cannot be imported.
- griffe.AliasResolutionError: Exception for aliases that cannot be resolved.
- griffe.CyclicAliasError: Exception raised when a cycle is detected in aliases.
- griffe.LastNodeError: Exception raised when trying to access a next or previous node.
- griffe.RootNodeError: Exception raised when trying to use siblings properties on a root node.
- griffe.BuiltinModuleError: Exception raised when trying to access the filepath of a builtin module.
- griffe.ExtensionError: Base class for errors raised by extensions.
- griffe.ExtensionNotLoadedError: Exception raised when an extension could not be loaded.
- griffe.GitError: Exception raised for errors related to Git.

## Expressions

Griffe stores snippets of code (attribute values, decorators, base class, type annotations) as expressions. Expressions are basically abstract syntax trees (AST) with a few differences compared to the nodes returned by ast. Griffe provides a few helpers to extract expressions from regular AST nodes.

- griffe.get_annotation: Get a type annotation as expression.
- griffe.get_base_class: Get a base class as expression.
- griffe.get_class_keyword: Get a class keyword as expression.
- griffe.get_condition: Get a condition as expression.
- griffe.get_expression: Get an expression from an AST node.
- griffe.safe_get_annotation: Get a type annotation as expression, safely (returns `None` on error).
- griffe.safe_get_base_class: Get a base class as expression, safely (returns `None` on error).
- griffe.safe_get_class_keyword: Get a class keyword as expression, safely (returns `None` on error).
- griffe.safe_get_condition: Get a condition as expression, safely (returns `None` on error).
- griffe.safe_get_expression: Get an expression from an AST node, safely (returns `None` on error).

The base class for expressions.

- griffe.Expr

Expression classes all start with `Expr`.

## Loggers

If you want to log messages from extensions, get a logger with `get_logger`. The `logger` attribute is used by Griffe itself. You can use it to temporarily disable Griffe logging.

- griffe.logger: Our global logger, used throughout the library.
- griffe.get_logger: Create and return a new logger instance.

## Helpers

To test your Griffe extensions, or to load API data from code in memory, Griffe provides the following helpers.

- griffe.temporary_pyfile: Create a Python file containing the given code in a temporary directory.
- griffe.temporary_pypackage: Create a package containing the given modules in a temporary directory.
- griffe.temporary_visited_module: Create and visit a temporary module with the given code.
- griffe.temporary_visited_package: Create and visit a temporary package.
- griffe.temporary_inspected_module: Create and inspect a temporary module with the given code.
- griffe.temporary_inspected_package: Create and inspect a temporary package.
