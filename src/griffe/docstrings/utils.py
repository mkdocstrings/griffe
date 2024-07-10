"""Deprecated. Import from `griffe` directly."""

from __future__ import annotations

import warnings
from typing import Any

import griffe


def __getattr__(name: str) -> Any:
    warnings.warn(
        "Importing from `griffe.docstrings.utils` is deprecated. Import from `griffe` directly instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if name == "WarningCallable":
        warnings.warn(
            "The 'WarningCallable' class was renamed 'DocstringWarningCallable'.",
            DeprecationWarning,
            stacklevel=2,
        )
        return griffe.DocstringWarningCallable
    if name == "warning":
        warnings.warn(
            "The 'warning' function was renamed 'docstring_warning'.",
            DeprecationWarning,
            stacklevel=2,
        )
        return griffe.docstring_warning
    if name == "parse_annotation":
        warnings.warn(
            "The 'parse_annotation' function was renamed 'parse_docstring_annotation'.",
            DeprecationWarning,
            stacklevel=2,
        )
        return griffe.parse_docstring_annotation
    return getattr(griffe, name)
