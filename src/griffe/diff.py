"""Deprecated. Import from `griffe` directly."""

from __future__ import annotations

import warnings
from typing import Any

import griffe


def __getattr__(name: str) -> Any:
    warnings.warn(
        "Importing from `griffe.diff` is deprecated. Import from `griffe` directly instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return getattr(griffe, name)
