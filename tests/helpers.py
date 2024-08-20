"""Helpers for tests."""

from __future__ import annotations

import os
import sys
from tempfile import gettempdir

from _griffe.tests import _TMPDIR_PREFIX


def clear_sys_modules(name: str | None = None) -> None:
    """Clear `sys.modules` of a module and its submodules.

    Use this function after having used `temporary_pypackage` and `inspect` together.
    Better yet, use `temporary_inspected_package` and `temporary_inspected_module`
    which will automatically clear `sys.modules` when exiting.

    Parameters:
        name: A top-level module name. If None, clear all temporary inspected modules
            (located in the OS' default temporary directory).
    """
    if name:
        for module_name in tuple(sys.modules.keys()):
            if module_name == name or module_name.startswith(f"{name}."):
                sys.modules.pop(module_name, None)
    else:
        prefix = os.path.join(gettempdir(), _TMPDIR_PREFIX)  # noqa: PTH118
        for module_name, module in tuple(sys.modules.items()):
            if (
                (file := getattr(module, "__file__", ""))
                and file.startswith(prefix)
                or (paths := getattr(module, "__path__", ()))
                and any(path.startswith(prefix) for path in paths)
            ):
                sys.modules.pop(module_name, None)
