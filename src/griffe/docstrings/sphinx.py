"""Deprecated. Import from `griffe` directly."""

from __future__ import annotations

import warnings
from typing import Any

import griffe


def __getattr__(name: str) -> Any:
    warnings.warn(
        "Importing from `griffe.docstrings.sphinx` is deprecated. Import from `griffe` directly instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if name == "parse":
        warnings.warn(
            "The 'parse' function was renamed 'parse_sphinx'.",
            DeprecationWarning,
            stacklevel=2,
        )
        return griffe.parse_sphinx
    return getattr(griffe, name)
