"""Deprecated. Import from `griffe` directly."""

from __future__ import annotations

import warnings
from typing import Any

import griffe


def __getattr__(name: str) -> Any:
    warnings.warn(
        "Importing from `griffe.stats` is deprecated. Import from `griffe` directly instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if name == "stats":
        warnings.warn(
            "The 'stats' function was made into a class and renamed 'Stats'.",
            DeprecationWarning,
            stacklevel=2,
        )
        return griffe.Stats
    return getattr(griffe, name)
