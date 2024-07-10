"""Deprecated. Import from `griffe` directly."""

from __future__ import annotations

import warnings
from typing import Any

import griffe


def __getattr__(name: str) -> Any:
    warnings.warn(
        "Importing from `griffe.docstrings.google` is deprecated. Import from `griffe` directly instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if name == "parse":
        warnings.warn(
            "The 'parse' function was renamed 'parse_google'.",
            DeprecationWarning,
            stacklevel=2,
        )
        return griffe.parse_google
    return getattr(griffe, name)
