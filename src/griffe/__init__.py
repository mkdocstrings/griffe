# This top-level module imports all public names from the package,
# and exposes them as public objects. We have tests to make sure
# no object is forgotten in this list.

"""Griffe package.

Signatures for entire Python programs.
Extract the structure, the frame, the skeleton of your project,
to generate API documentation or find breaking changes in your API.

The entirety of the public API is exposed here, in the top-level `griffe` module.

All messages written to standard output or error are logged using the `logging` module.
Our logger's name is set to `"griffe"` and is public (you can rely on it).
You can obtain the logger from the standard `logging` module: `logging.getLogger("griffe")`.
Actual logging messages are not part of the public API (they might change without notice).

Raised exceptions throughout the package are part of the public API (you can rely on them).
Their actual messages are not part of the public API (they might change without notice).

The following paragraphs will help you discover the package's content.

## CLI entrypoints

Griffe provides a command-line interface (CLI) to interact with the package. The CLI entrypoints can be called from Python code.

- [`griffe.main`][]: Run the main program.
- [`griffe.check`][]: Check for API breaking changes in two versions of the same package.
- [`griffe.dump`][]: Load packages data and dump it as JSON.

## Loaders

To load API data, Griffe provides several high-level functions.

- [`griffe.load`][]: Load and return a Griffe object.
- [`griffe.load_git`][]: Load and return a module from a specific Git reference.
- [`griffe.load_pypi`][]: Load and return a module from a specific package version downloaded using pip.

## Models

The data loaded by Griffe is represented by several classes.

- [`griffe.Module`][]: The class representing a Python module.
- [`griffe.Class`][]: The class representing a Python class.
- [`griffe.Function`][]: The class representing a Python function or method.
- [`griffe.Attribute`][]: The class representing a Python attribute.
- [`griffe.Alias`][]: This class represents an alias, or indirection, to an object declared in another module.

Additional classes are available to represent other concepts.

- [`griffe.Decorator`][]: This class represents a decorator.
- [`griffe.Parameters`][]: This class is a container for parameters.
- [`griffe.Parameter`][]: This class represent a function parameter.

## Agents

Griffe is able to analyze code both statically and dynamically, using the following "agents".
However most of the time you will only need to use the loaders above.

- [`griffe.visit`][]: Parse and visit a module file.
- [`griffe.inspect`][]: Inspect a module.

## Serializers

Griffe can serizalize data to dictionary and JSON.

- [`griffe.Object.as_json`][griffe.Object.as_json]
- [`griffe.Object.from_json`][griffe.Object.from_json]
- [`griffe.JSONEncoder`][]: JSON encoder for Griffe objects.
- [`griffe.json_decoder`][]: JSON decoder for Griffe objects.

## API checks

Griffe can compare two versions of the same package to find breaking changes.

- [`griffe.find_breaking_changes`][]: Find breaking changes between two versions of the same API.
- [`griffe.Breakage`][]: Breakage classes can explain what broke from a version to another.

## Extensions

Griffe supports extensions. You can create your own extension by subclassing the `griffe.Extension` class.

- [`griffe.load_extensions`][]: Load configured extensions.
- [`griffe.Extension`][]: Base class for Griffe extensions.

## Docstrings

Griffe can parse docstrings into structured data.

Main class:

- [`griffe.Docstring`][]: This class represents docstrings.

Docstring section and element classes all start with `Docstring`.

Docstring parsers:

- [`griffe.parse`][]: Parse the docstring.
- [`griffe.parse_auto`][]: Parse a docstring by automatically detecting the style it uses.
- [`griffe.parse_google`][]: Parse a Google-style docstring.
- [`griffe.parse_numpy`][]: Parse a Numpydoc-style docstring.
- [`griffe.parse_sphinx`][]: Parse a Sphinx-style docstring.

## Exceptions

Griffe uses several exceptions to signal errors.

- [`griffe.GriffeError`][]: The base exception for all Griffe errors.
- [`griffe.LoadingError`][]: Exception for loading errors.
- [`griffe.NameResolutionError`][]: Exception for names that cannot be resolved in a object scope.
- [`griffe.UnhandledEditableModuleError`][]: Exception for unhandled editables modules, when searching modules.
- [`griffe.UnimportableModuleError`][]: Exception for modules that cannot be imported.
- [`griffe.AliasResolutionError`][]: Exception for aliases that cannot be resolved.
- [`griffe.CyclicAliasError`][]: Exception raised when a cycle is detected in aliases.
- [`griffe.LastNodeError`][]: Exception raised when trying to access a next or previous node.
- [`griffe.RootNodeError`][]: Exception raised when trying to use siblings properties on a root node.
- [`griffe.BuiltinModuleError`][]: Exception raised when trying to access the filepath of a builtin module.
- [`griffe.ExtensionError`][]: Base class for errors raised by extensions.
- [`griffe.ExtensionNotLoadedError`][]: Exception raised when an extension could not be loaded.
- [`griffe.GitError`][]: Exception raised for errors related to Git.

# Expressions

Griffe stores snippets of code (attribute values, decorators, base class, type annotations) as expressions.
Expressions are basically abstract syntax trees (AST) with a few differences compared to the nodes returned by [`ast`][].
Griffe provides a few helpers to extract expressions from regular AST nodes.

- [`griffe.get_annotation`][]: Get a type annotation as expression.
- [`griffe.get_base_class`][]: Get a base class as expression.
- [`griffe.get_condition`][]: Get a condition as expression.
- [`griffe.get_expression`][]: Get an expression from an AST node.
- [`griffe.safe_get_annotation`][]: Get a type annotation as expression, safely (returns `None` on error).
- [`griffe.safe_get_base_class`][]: Get a base class as expression, safely (returns `None` on error).
- [`griffe.safe_get_condition`][]: Get a condition as expression, safely (returns `None` on error).
- [`griffe.safe_get_expression`][]: Get an expression from an AST node, safely (returns `None` on error).

The base class for expressions.

- [`griffe.Expr`][]

Expression classes all start with `Expr`.

# Loggers

If you want to log messages from extensions, get a logger with `get_logger`.
The `logger` attribute is used by Griffe itself. You can use it to temporarily disable Griffe logging.

- [`griffe.logger`][]: Our global logger, used throughout the library.
- [`griffe.get_logger`][]: Create and return a new logger instance.

# Helpers

To test your Griffe extensions, or to load API data from code in memory, Griffe provides the following helpers.

- [`griffe.temporary_pyfile`][]: Create a Python file containing the given code in a temporary directory.
- [`griffe.temporary_pypackage`][]: Create a package containing the given modules in a temporary directory.
- [`griffe.temporary_visited_module`][]: Create and visit a temporary module with the given code.
- [`griffe.temporary_visited_package`][]: Create and visit a temporary package.
- [`griffe.temporary_inspected_module`][]: Create and inspect a temporary module with the given code.
- [`griffe.temporary_inspected_package`][]: Create and inspect a temporary package.
"""

from __future__ import annotations

from _griffe.agents.inspector import Inspector, inspect
from _griffe.agents.nodes.assignments import get_instance_names, get_name, get_names
from _griffe.agents.nodes.ast import (
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
from _griffe.agents.nodes.docstrings import get_docstring

# YORE: Bump 2: Replace `ExportedName, ` with `` within line.
from _griffe.agents.nodes.exports import ExportedName, get__all__, safe_get__all__
from _griffe.agents.nodes.imports import relative_to_absolute
from _griffe.agents.nodes.parameters import ParametersType, get_parameters
from _griffe.agents.nodes.runtime import ObjectNode
from _griffe.agents.nodes.values import get_value, safe_get_value
from _griffe.agents.visitor import Visitor, builtin_decorators, stdlib_decorators, typing_overload, visit
from _griffe.c3linear import c3linear_merge
from _griffe.cli import DEFAULT_LOG_LEVEL, check, dump, get_parser, main
from _griffe.collections import LinesCollection, ModulesCollection
from _griffe.diff import (
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
from _griffe.docstrings.google import parse_google
from _griffe.docstrings.models import (
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
    DocstringSectionWarns,
    DocstringSectionYields,
    DocstringWarn,
    DocstringYield,
)
from _griffe.docstrings.numpy import parse_numpy
from _griffe.docstrings.parsers import (
    DocstringDetectionMethod,
    DocstringStyle,
    infer_docstring_style,
    parse,
    parse_auto,
    parsers,
)
from _griffe.docstrings.sphinx import parse_sphinx
from _griffe.docstrings.utils import docstring_warning, parse_docstring_annotation
from _griffe.encoders import JSONEncoder, json_decoder
from _griffe.enumerations import (
    BreakageKind,
    DocstringSectionKind,
    ExplanationStyle,
    Kind,
    LogLevel,
    ObjectKind,
    ParameterKind,
    Parser,
)
from _griffe.exceptions import (
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
from _griffe.expressions import (
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
    get_condition,
    get_expression,
    safe_get_annotation,
    safe_get_base_class,
    safe_get_condition,
    safe_get_expression,
)
from _griffe.extensions.base import (
    Extension,
    Extensions,
    LoadableExtensionType,
    builtin_extensions,
    load_extensions,
)
from _griffe.extensions.dataclasses import DataclassesExtension
from _griffe.finder import ModuleFinder, NamePartsAndPathType, NamePartsType, NamespacePackage, Package
from _griffe.git import assert_git_repo, get_latest_tag, get_repo_root, tmp_worktree
from _griffe.importer import dynamic_import, sys_path
from _griffe.loader import GriffeLoader, load, load_git, load_pypi
from _griffe.logger import Logger, get_logger, logger, patch_loggers
from _griffe.merger import merge_stubs
from _griffe.mixins import (
    DelMembersMixin,
    GetMembersMixin,
    ObjectAliasMixin,
    SerializationMixin,
    SetMembersMixin,
)
from _griffe.models import (
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
)
from _griffe.stats import Stats
from _griffe.tests import (
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
# import griffe
# names = sorted(n for n in dir(griffe) if not n.startswith("_") and n not in ("annotations", "lazy_importing"))
# print('__all__ = [\n    "' + '",\n    "'.join(names) + '",\n]')
__all__ = [
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
    "DocstringDetectionMethod",
    "DocstringElement",
    "DocstringFunction",
    "DocstringModule",
    "DocstringNamedElement",
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
    "DocstringSectionWarns",
    "DocstringSectionYields",
    "DocstringStyle",
    "DocstringWarn",
    "DocstringYield",
    "ExplanationStyle",
    # YORE: Bump 2: Remove line.
    "ExportedName",
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
    "GriffeError",
    "GriffeLoader",
    "Inspector",
    "JSONEncoder",
    "Kind",
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
    "ReturnChangedTypeBreakage",
    "RootNodeError",
    "SerializationMixin",
    "SetMembersMixin",
    "Stats",
    "TmpPackage",
    "UnhandledEditableModuleError",
    "UnimportableModuleError",
    "Visitor",
    "assert_git_repo",
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
    "get_condition",
    "get_docstring",
    "get_expression",
    "get_instance_names",
    "get_latest_tag",
    "get_logger",
    "get_name",
    "get_names",
    "get_parameters",
    "get_parser",
    "get_repo_root",
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
    "tmp_worktree",
    "typing_overload",
    "visit",
    "vtree",
]
