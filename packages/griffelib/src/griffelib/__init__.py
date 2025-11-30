# This top-level module imports all public names from the package,
# and exposes them as public objects. We have tests to make sure
# no object is forgotten in this list.

"""Griffe package.

Signatures for entire Python programs.
Extract the structure, the frame, the skeleton of your project,
to generate API documentation or find breaking changes in your API.

The entirety of the public API is exposed here, in the top-level `griffelib` module.

All messages written to standard output or error are logged using the `logging` module.
Our logger's name is set to `"griffelib"` and is public (you can rely on it).
You can obtain the logger from the standard `logging` module: `logging.getLogger("griffelib")`.
Actual logging messages are not part of the public API (they might change without notice).

Raised exceptions throughout the package are part of the public API (you can rely on them).
Their actual messages are not part of the public API (they might change without notice).

The following paragraphs will help you discover the package's content.

## CLI entrypoints

Griffe provides a command-line interface (CLI) to interact with the package. The CLI entrypoints can be called from Python code.

- [`griffecli.main`][]: Run the main program.
- [`griffecli.check`][]: Check for API breaking changes in two versions of the same package.
- [`griffecli.dump`][]: Load packages data and dump it as JSON.

## Loaders

To load API data, Griffe provides several high-level functions.

- [`griffelib.load`][]: Load and return a Griffe object.
- [`griffelib.load_git`][]: Load and return a module from a specific Git reference.
- [`griffelib.load_pypi`][]: Load and return a module from a specific package version downloaded using pip.

## Models

The data loaded by Griffe is represented by several classes.

- [`griffelib.Module`][]: The class representing a Python module.
- [`griffelib.Class`][]: The class representing a Python class.
- [`griffelib.Function`][]: The class representing a Python function or method.
- [`griffelib.Attribute`][]: The class representing a Python attribute.
- [`griffelib.Alias`][]: This class represents an alias, or indirection, to an object declared in another module.

Additional classes are available to represent other concepts.

- [`griffelib.Decorator`][]: This class represents a decorator.
- [`griffelib.Parameters`][]: This class is a container for parameters.
- [`griffelib.Parameter`][]: This class represent a function parameter.

## Agents

Griffe is able to analyze code both statically and dynamically, using the following "agents".
However most of the time you will only need to use the loaders above.

- [`griffelib.visit`][]: Parse and visit a module file.
- [`griffelib.inspect`][]: Inspect a module.

## Serializers

Griffe can serizalize data to dictionary and JSON.

- [`griffelib.Object.as_json`][griffelib.Object.as_json]
- [`griffelib.Object.from_json`][griffelib.Object.from_json]
- [`griffelib.JSONEncoder`][]: JSON encoder for Griffe objects.
- [`griffelib.json_decoder`][]: JSON decoder for Griffe objects.

## API checks

Griffe can compare two versions of the same package to find breaking changes.

- [`griffelib.find_breaking_changes`][]: Find breaking changes between two versions of the same API.
- [`griffelib.Breakage`][]: Breakage classes can explain what broke from a version to another.

## Extensions

Griffe supports extensions. You can create your own extension by subclassing the `griffelib.Extension` class.

- [`griffelib.load_extensions`][]: Load configured extensions.
- [`griffelib.Extension`][]: Base class for Griffe extensions.

## Docstrings

Griffe can parse docstrings into structured data.

Main class:

- [`griffelib.Docstring`][]: This class represents docstrings.

Docstring section and element classes all start with `Docstring`.

Docstring parsers:

- [`griffelib.parse`][]: Parse the docstring.
- [`griffelib.parse_auto`][]: Parse a docstring by automatically detecting the style it uses.
- [`griffelib.parse_google`][]: Parse a Google-style docstring.
- [`griffelib.parse_numpy`][]: Parse a Numpydoc-style docstring.
- [`griffelib.parse_sphinx`][]: Parse a Sphinx-style docstring.

## Exceptions

Griffe uses several exceptions to signal errors.

- [`griffelib.GriffeError`][]: The base exception for all Griffe errors.
- [`griffelib.LoadingError`][]: Exception for loading errors.
- [`griffelib.NameResolutionError`][]: Exception for names that cannot be resolved in a object scope.
- [`griffelib.UnhandledEditableModuleError`][]: Exception for unhandled editables modules, when searching modules.
- [`griffelib.UnimportableModuleError`][]: Exception for modules that cannot be imported.
- [`griffelib.AliasResolutionError`][]: Exception for aliases that cannot be resolved.
- [`griffelib.CyclicAliasError`][]: Exception raised when a cycle is detected in aliases.
- [`griffelib.LastNodeError`][]: Exception raised when trying to access a next or previous node.
- [`griffelib.RootNodeError`][]: Exception raised when trying to use siblings properties on a root node.
- [`griffelib.BuiltinModuleError`][]: Exception raised when trying to access the filepath of a builtin module.
- [`griffelib.ExtensionError`][]: Base class for errors raised by extensions.
- [`griffelib.ExtensionNotLoadedError`][]: Exception raised when an extension could not be loaded.
- [`griffelib.GitError`][]: Exception raised for errors related to Git.

# Expressions

Griffe stores snippets of code (attribute values, decorators, base class, type annotations) as expressions.
Expressions are basically abstract syntax trees (AST) with a few differences compared to the nodes returned by [`ast`][].
Griffe provides a few helpers to extract expressions from regular AST nodes.

- [`griffelib.get_annotation`][]: Get a type annotation as expression.
- [`griffelib.get_base_class`][]: Get a base class as expression.
- [`griffelib.get_class_keyword`][]: Get a class keyword as expression.
- [`griffelib.get_condition`][]: Get a condition as expression.
- [`griffelib.get_expression`][]: Get an expression from an AST node.
- [`griffelib.safe_get_annotation`][]: Get a type annotation as expression, safely (returns `None` on error).
- [`griffelib.safe_get_base_class`][]: Get a base class as expression, safely (returns `None` on error).
- [`griffelib.safe_get_class_keyword`][]: Get a class keyword as expression, safely (returns `None` on error).
- [`griffelib.safe_get_condition`][]: Get a condition as expression, safely (returns `None` on error).
- [`griffelib.safe_get_expression`][]: Get an expression from an AST node, safely (returns `None` on error).

The base class for expressions.

- [`griffelib.Expr`][]

Expression classes all start with `Expr`.

# Loggers

If you want to log messages from extensions, get a logger with `get_logger`.
The `logger` attribute is used by Griffe itself. You can use it to temporarily disable Griffe logging.

- [`griffelib.logger`][]: Our global logger, used throughout the library.
- [`griffelib.get_logger`][]: Create and return a new logger instance.

# Helpers

To test your Griffe extensions, or to load API data from code in memory, Griffe provides the following helpers.

- [`griffelib.temporary_pyfile`][]: Create a Python file containing the given code in a temporary directory.
- [`griffelib.temporary_pypackage`][]: Create a package containing the given modules in a temporary directory.
- [`griffelib.temporary_visited_module`][]: Create and visit a temporary module with the given code.
- [`griffelib.temporary_visited_package`][]: Create and visit a temporary package.
- [`griffelib.temporary_inspected_module`][]: Create and inspect a temporary module with the given code.
- [`griffelib.temporary_inspected_package`][]: Create and inspect a temporary package.
"""

from __future__ import annotations

from griffelib._internal.agents.inspector import Inspector, inspect
from griffelib._internal.agents.nodes.assignments import get_instance_names, get_name, get_names
from griffelib._internal.agents.nodes.ast import (
    ast_children,
    ast_first_child,
    ast_kind,
    ast_last_child,
    ast_next,
    ast_next_siblings,
    ast_previous,
    ast_previous_siblings,
    ast_siblings,
)
from griffelib._internal.agents.nodes.docstrings import get_docstring
from griffelib._internal.agents.nodes.exports import get__all__, safe_get__all__
from griffelib._internal.agents.nodes.imports import relative_to_absolute
from griffelib._internal.agents.nodes.parameters import ParametersType, get_parameters
from griffelib._internal.agents.nodes.runtime import ObjectNode
from griffelib._internal.agents.nodes.values import get_value, safe_get_value
from griffelib._internal.agents.visitor import Visitor, builtin_decorators, stdlib_decorators, typing_overload, visit
from griffelib._internal.c3linear import c3linear_merge
from griffecli._internal.cli import DEFAULT_LOG_LEVEL, check, dump, get_parser, main
from griffelib._internal.collections import LinesCollection, ModulesCollection
from griffelib._internal.diff import (
    AttributeChangedTypeBreakage,
    AttributeChangedValueBreakage,
    Breakage,
    ClassRemovedBaseBreakage,
    ObjectChangedKindBreakage,
    ObjectRemovedBreakage,
    ParameterAddedRequiredBreakage,
    ParameterChangedDefaultBreakage,
    ParameterChangedKindBreakage,
    ParameterChangedRequiredBreakage,
    ParameterMovedBreakage,
    ParameterRemovedBreakage,
    ReturnChangedTypeBreakage,
    find_breaking_changes,
)
from griffelib._internal.docstrings.auto import (
    AutoOptions,
    DocstringDetectionMethod,
    PerStyleOptions,
    infer_docstring_style,
    parse_auto,
)
from griffelib._internal.docstrings.google import GoogleOptions, parse_google
from griffelib._internal.docstrings.models import (
    DocstringAdmonition,
    DocstringAttribute,
    DocstringClass,
    DocstringDeprecated,
    DocstringElement,
    DocstringFunction,
    DocstringModule,
    DocstringNamedElement,
    DocstringParameter,
    DocstringRaise,
    DocstringReceive,
    DocstringReturn,
    DocstringSection,
    DocstringSectionAdmonition,
    DocstringSectionAttributes,
    DocstringSectionClasses,
    DocstringSectionDeprecated,
    DocstringSectionExamples,
    DocstringSectionFunctions,
    DocstringSectionModules,
    DocstringSectionOtherParameters,
    DocstringSectionParameters,
    DocstringSectionRaises,
    DocstringSectionReceives,
    DocstringSectionReturns,
    DocstringSectionText,
    DocstringSectionTypeAliases,
    DocstringSectionTypeParameters,
    DocstringSectionWarns,
    DocstringSectionYields,
    DocstringTypeAlias,
    DocstringTypeParameter,
    DocstringWarn,
    DocstringYield,
)
from griffelib._internal.docstrings.numpy import NumpyOptions, parse_numpy
from griffelib._internal.docstrings.parsers import (
    DocstringOptions,
    DocstringStyle,
    parse,
    parsers,
)
from griffelib._internal.docstrings.sphinx import SphinxOptions, parse_sphinx
from griffelib._internal.docstrings.utils import docstring_warning, parse_docstring_annotation
from griffelib._internal.encoders import JSONEncoder, json_decoder
from griffelib._internal.enumerations import (
    BreakageKind,
    DocstringSectionKind,
    ExplanationStyle,
    Kind,
    LogLevel,
    ObjectKind,
    ParameterKind,
    Parser,
    TypeParameterKind,
)
from griffelib._internal.exceptions import (
    AliasResolutionError,
    BuiltinModuleError,
    CyclicAliasError,
    ExtensionError,
    ExtensionNotLoadedError,
    GitError,
    GriffeError,
    LastNodeError,
    LoadingError,
    NameResolutionError,
    RootNodeError,
    UnhandledEditableModuleError,
    UnimportableModuleError,
)
from griffelib._internal.expressions import (
    Expr,
    ExprAttribute,
    ExprBinOp,
    ExprBoolOp,
    ExprCall,
    ExprCompare,
    ExprComprehension,
    ExprConstant,
    ExprDict,
    ExprDictComp,
    ExprExtSlice,
    ExprFormatted,
    ExprGeneratorExp,
    ExprIfExp,
    ExprJoinedStr,
    ExprKeyword,
    ExprLambda,
    ExprList,
    ExprListComp,
    ExprName,
    ExprNamedExpr,
    ExprParameter,
    ExprSet,
    ExprSetComp,
    ExprSlice,
    ExprSubscript,
    ExprTuple,
    ExprUnaryOp,
    ExprVarKeyword,
    ExprVarPositional,
    ExprYield,
    ExprYieldFrom,
    get_annotation,
    get_base_class,
    get_class_keyword,
    get_condition,
    get_expression,
    safe_get_annotation,
    safe_get_base_class,
    safe_get_class_keyword,
    safe_get_condition,
    safe_get_expression,
)
from griffelib._internal.extensions.base import (
    Extension,
    Extensions,
    LoadableExtensionType,
    builtin_extensions,
    load_extensions,
)
from griffelib._internal.extensions.dataclasses import DataclassesExtension
from griffelib._internal.extensions.unpack_typeddict import UnpackTypedDictExtension
from griffelib._internal.finder import ModuleFinder, NamePartsAndPathType, NamePartsType, NamespacePackage, Package
from griffelib._internal.git import GitInfo, KnownGitService
from griffelib._internal.importer import dynamic_import, sys_path
from griffelib._internal.loader import GriffeLoader, load, load_git, load_pypi
from griffelib._internal.logger import Logger, get_logger, logger, patch_loggers
from griffelib._internal.merger import merge_stubs
from griffelib._internal.mixins import (
    DelMembersMixin,
    GetMembersMixin,
    ObjectAliasMixin,
    SerializationMixin,
    SetMembersMixin,
)
from griffelib._internal.models import (
    Alias,
    Attribute,
    Class,
    Decorator,
    Docstring,
    Function,
    Module,
    Object,
    Parameter,
    Parameters,
    TypeAlias,
    TypeParameter,
    TypeParameters,
)
from griffelib._internal.stats import Stats
from griffelib._internal.tests import (
    TmpPackage,
    htree,
    module_vtree,
    temporary_inspected_module,
    temporary_inspected_package,
    temporary_pyfile,
    temporary_pypackage,
    temporary_visited_module,
    temporary_visited_package,
    vtree,
)

# Regenerate this list with the following Python snippet:
# import griffelib
# names = sorted(n for n in dir(griffelib) if not n.startswith("_") and n not in ("annotations",))
# print('__all__ = [\n    "' + '",\n    "'.join(names) + '",\n]')
__all__ = [
    "DEFAULT_LOG_LEVEL",
    "Alias",
    "AliasResolutionError",
    "Attribute",
    "AttributeChangedTypeBreakage",
    "AttributeChangedValueBreakage",
    "AutoOptions",
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
    "DocstringDetectionMethod",
    "DocstringElement",
    "DocstringFunction",
    "DocstringModule",
    "DocstringNamedElement",
    "DocstringOptions",
    "DocstringParameter",
    "DocstringRaise",
    "DocstringReceive",
    "DocstringReturn",
    "DocstringSection",
    "DocstringSectionAdmonition",
    "DocstringSectionAttributes",
    "DocstringSectionClasses",
    "DocstringSectionDeprecated",
    "DocstringSectionExamples",
    "DocstringSectionFunctions",
    "DocstringSectionKind",
    "DocstringSectionModules",
    "DocstringSectionOtherParameters",
    "DocstringSectionParameters",
    "DocstringSectionRaises",
    "DocstringSectionReceives",
    "DocstringSectionReturns",
    "DocstringSectionText",
    "DocstringSectionTypeAliases",
    "DocstringSectionTypeParameters",
    "DocstringSectionWarns",
    "DocstringSectionYields",
    "DocstringStyle",
    "DocstringTypeAlias",
    "DocstringTypeParameter",
    "DocstringWarn",
    "DocstringYield",
    "ExplanationStyle",
    "Expr",
    "ExprAttribute",
    "ExprBinOp",
    "ExprBoolOp",
    "ExprCall",
    "ExprCompare",
    "ExprComprehension",
    "ExprConstant",
    "ExprDict",
    "ExprDictComp",
    "ExprExtSlice",
    "ExprFormatted",
    "ExprGeneratorExp",
    "ExprIfExp",
    "ExprJoinedStr",
    "ExprKeyword",
    "ExprLambda",
    "ExprList",
    "ExprListComp",
    "ExprName",
    "ExprNamedExpr",
    "ExprParameter",
    "ExprSet",
    "ExprSetComp",
    "ExprSlice",
    "ExprSubscript",
    "ExprTuple",
    "ExprUnaryOp",
    "ExprVarKeyword",
    "ExprVarPositional",
    "ExprYield",
    "ExprYieldFrom",
    "Extension",
    "ExtensionError",
    "ExtensionNotLoadedError",
    "Extensions",
    "Function",
    "GetMembersMixin",
    "GitError",
    "GitInfo",
    "GoogleOptions",
    "GriffeError",
    "GriffeLoader",
    "Inspector",
    "JSONEncoder",
    "Kind",
    "KnownGitService",
    "LastNodeError",
    "LinesCollection",
    "LoadableExtensionType",
    "LoadingError",
    "LogLevel",
    "Logger",
    "Module",
    "ModuleFinder",
    "ModulesCollection",
    "NamePartsAndPathType",
    "NamePartsType",
    "NameResolutionError",
    "NamespacePackage",
    "NumpyOptions",
    "Object",
    "ObjectAliasMixin",
    "ObjectChangedKindBreakage",
    "ObjectKind",
    "ObjectNode",
    "ObjectRemovedBreakage",
    "Package",
    "Parameter",
    "ParameterAddedRequiredBreakage",
    "ParameterChangedDefaultBreakage",
    "ParameterChangedKindBreakage",
    "ParameterChangedRequiredBreakage",
    "ParameterKind",
    "ParameterMovedBreakage",
    "ParameterRemovedBreakage",
    "Parameters",
    "ParametersType",
    "Parser",
    "PerStyleOptions",
    "ReturnChangedTypeBreakage",
    "RootNodeError",
    "SerializationMixin",
    "SetMembersMixin",
    "SphinxOptions",
    "Stats",
    "TmpPackage",
    "TypeAlias",
    "TypeParameter",
    "TypeParameterKind",
    "TypeParameters",
    "UnhandledEditableModuleError",
    "UnimportableModuleError",
    "UnpackTypedDictExtension",
    "Visitor",
    "ast_children",
    "ast_first_child",
    "ast_kind",
    "ast_last_child",
    "ast_next",
    "ast_next_siblings",
    "ast_previous",
    "ast_previous_siblings",
    "ast_siblings",
    "builtin_decorators",
    "builtin_extensions",
    "c3linear_merge",
    "check",
    "docstring_warning",
    "dump",
    "dynamic_import",
    "find_breaking_changes",
    "get__all__",
    "get_annotation",
    "get_base_class",
    "get_class_keyword",
    "get_condition",
    "get_docstring",
    "get_expression",
    "get_instance_names",
    "get_logger",
    "get_name",
    "get_names",
    "get_parameters",
    "get_parser",
    "get_value",
    "htree",
    "infer_docstring_style",
    "inspect",
    "json_decoder",
    "load",
    "load_extensions",
    "load_git",
    "load_pypi",
    "logger",
    "main",
    "merge_stubs",
    "module_vtree",
    "parse",
    "parse_auto",
    "parse_docstring_annotation",
    "parse_google",
    "parse_numpy",
    "parse_sphinx",
    "parsers",
    "patch_loggers",
    "relative_to_absolute",
    "safe_get__all__",
    "safe_get_annotation",
    "safe_get_base_class",
    "safe_get_class_keyword",
    "safe_get_condition",
    "safe_get_expression",
    "safe_get_value",
    "stdlib_decorators",
    "sys_path",
    "temporary_inspected_module",
    "temporary_inspected_package",
    "temporary_pyfile",
    "temporary_pypackage",
    "temporary_visited_module",
    "temporary_visited_package",
    "typing_overload",
    "visit",
    "vtree",
]
