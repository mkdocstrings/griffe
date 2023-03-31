"""Deprecated. Import from `griffe.extensions` instead."""

import warnings
from typing import Any

from griffe import extensions


def __getattr__(name: str) -> Any:
    warnings.warn(
        "The `griffe.agents.extensions` module "
        "is deprecated in favor of the `griffe.extensions` module. "
        "Please import from the new module instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return getattr(extensions, name)
