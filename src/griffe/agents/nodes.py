"""Deprecated. Import from `griffe` directly."""

from __future__ import annotations

import warnings
from typing import Any

import griffe


def __getattr__(name: str) -> Any:
    warnings.warn(
        "Importing from `griffe.agents.nodes` is deprecated. Import from `griffe` directly instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if name == "Name":
        warnings.warn(
            "The `Name` class was renamed `ExportedName`.",
            DeprecationWarning,
            stacklevel=2,
        )
        return griffe.ExportedName
    return getattr(griffe, name)
