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

If you need to alter our logger, do so temporarily and restore it to its original state,
for example using [context managers][contextlib.contextmanager].
Actual logging messages are not part of the public API (they might change without notice).

Raised exceptions throughout the package are part of the public API (you can rely on them).
Their actual messages are not part of the public API (they might change without notice).
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
from _griffe.docstrings.parsers import parse, parsers
from _griffe.docstrings.sphinx import parse_sphinx
from _griffe.docstrings.utils import DocstringWarningCallable, docstring_warning, parse_docstring_annotation
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
    # YORE: Bump 1: Remove line.
    When,
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
    # YORE: Bump 1: Remove line.
    ExtensionType,
    # YORE: Bump 1: Remove line.
    InspectorExtension,
    LoadableExtensionType,
    # YORE: Bump 1: Remove line.
    VisitorExtension,
    builtin_extensions,
    load_extensions,
)
from _griffe.extensions.dataclasses import DataclassesExtension

# YORE: Bump 1: Remove line.
from _griffe.extensions.hybrid import HybridExtension
from _griffe.finder import ModuleFinder, NamePartsAndPathType, NamePartsType, NamespacePackage, Package
from _griffe.git import assert_git_repo, get_latest_tag, get_repo_root, tmp_worktree
from _griffe.importer import dynamic_import, sys_path
from _griffe.loader import GriffeLoader, load, load_git

# YORE: Bump 1: Replace `get_logger` with `logger` within line.
# YORE: Bump 1: Replace `, patch_loggers` with `` within line.
from _griffe.logger import Logger, get_logger, patch_logger, patch_loggers
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
    "DEFAULT_LOG_LEVEL",
    "DataclassesExtension",
    "Decorator",
    "DelMembersMixin",
    "Docstring",
    "DocstringAdmonition",
    "DocstringAttribute",
    "DocstringClass",
    "DocstringDeprecated",
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
    "DocstringWarn",
    # YORE: Bump 1: Remove line.
    "DocstringWarningCallable",
    "DocstringYield",
    "ExplanationStyle",
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
    # YORE: Bump 1: Remove line.
    "ExtensionType",
    "Extensions",
    "Function",
    "GetMembersMixin",
    "GitError",
    "GriffeError",
    "GriffeLoader",
    # YORE: Bump 1: Remove line.
    "HybridExtension",
    "Inspector",
    # YORE: Bump 1: Remove line.
    "InspectorExtension",
    "JSONEncoder",
    "Kind",
    "LastNodeError",
    "LinesCollection",
    "LoadableExtensionType",
    "LoadingError",
    "Logger",
    "LogLevel",
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
    # YORE: Bump 1: Remove line.
    "VisitorExtension",
    # YORE: Bump 1: Remove line.
    "When",
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
    "dump",
    "docstring_warning",
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
    # YORE: Bump 1: Remove line.
    "get_logger",
    "get_name",
    "get_names",
    "get_parameters",
    "get_parser",
    "get_repo_root",
    "get_value",
    "htree",
    "inspect",
    "json_decoder",
    "load",
    "load_extensions",
    "load_git",
    # YORE: Bump 1: Uncomment line.
    # "logger",
    "main",
    "merge_stubs",
    "module_vtree",
    "parse",
    "parse_docstring_annotation",
    "parse_google",
    "parse_numpy",
    "parse_sphinx",
    "parsers",
    "patch_logger",
    # YORE: Bump 1: Remove line.
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
    "temporary_pyfile",
    "temporary_pypackage",
    "temporary_visited_module",
    "temporary_visited_package",
    "tmp_worktree",
    "typing_overload",
    "visit",
    "vtree",
]
