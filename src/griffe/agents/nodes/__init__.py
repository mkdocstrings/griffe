"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

from griffe.agents.nodes._all import get__all__, safe_get__all__
from griffe.agents.nodes._ast import (
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
from griffe.agents.nodes._docstrings import get_docstring
from griffe.agents.nodes._imports import relative_to_absolute
from griffe.agents.nodes._names import get_instance_names, get_name, get_names
from griffe.agents.nodes._parameters import get_call_keyword_arguments
from griffe.agents.nodes._runtime import ObjectKind, ObjectNode
from griffe.agents.nodes._values import get_value, safe_get_value
from griffe.expressions import (
    get_annotation,
    get_base_class,
    get_condition,
    get_expression,
    safe_get_annotation,
    safe_get_base_class,
    safe_get_condition,
    safe_get_expression,
)

__all__ = [
    "ast_children",
    "ast_first_child",
    "ast_kind",
    "ast_last_child",
    "ast_next",
    "ast_next_siblings",
    "ast_previous",
    "ast_previous_siblings",
    "ast_siblings",
    "get__all__",
    "get_annotation",
    "get_base_class",
    "get_call_keyword_arguments",
    "get_condition",
    "get_docstring",
    "get_expression",
    "get_instance_names",
    "get_name",
    "get_names",
    "get_value",
    "ObjectKind",
    "ObjectNode",
    "relative_to_absolute",
    "safe_get__all__",
    "safe_get_annotation",
    "safe_get_base_class",
    "safe_get_condition",
    "safe_get_expression",
    "safe_get_value",
]
