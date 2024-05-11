"""Helpers for tests."""

import sys


def clear_sys_modules(name: str) -> None:
    """Clear `sys.modules` of a module and its submodules.

    Use this function after having used `temporary_pypackage` and `inspect` together.

    Parameters:
        name: A top-level module name.
    """
    for module in list(sys.modules.keys()):
        if module == name or module.startswith(f"{name}."):
            sys.modules.pop(module, None)
