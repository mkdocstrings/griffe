"""This module contains utilities to compute loading statistics."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from griffe.exceptions import BuiltinModuleError

if TYPE_CHECKING:
    from griffe.loader import GriffeLoader


def _direct(objects):
    return [obj for obj in objects if not obj.is_alias]


def _n_modules(module):
    submodules = _direct(module.modules.values())
    return len(submodules) + sum(_n_modules(mod) for mod in submodules)


def _n_classes(module_or_class):
    submodules = _direct(module_or_class.modules.values())
    subclasses = _direct(module_or_class.classes.values())
    mods_or_classes = [mc for mc in (*submodules, *subclasses) if not mc.is_alias]
    return len(subclasses) + sum(_n_classes(mod_or_class) for mod_or_class in mods_or_classes)


def _n_functions(module_or_class):
    submodules = _direct(module_or_class.modules.values())
    subclasses = _direct(module_or_class.classes.values())
    functions = _direct(module_or_class.functions.values())
    mods_or_classes = [*submodules, *subclasses]
    return len(functions) + sum(_n_functions(mod_or_class) for mod_or_class in mods_or_classes)


def _n_attributes(module_or_class):
    submodules = _direct(module_or_class.modules.values())
    subclasses = _direct(module_or_class.classes.values())
    attributes = _direct(module_or_class.attributes.values())
    mods_or_classes = [*submodules, *subclasses]
    return len(attributes) + sum(_n_attributes(mod_or_class) for mod_or_class in mods_or_classes)


def _merge_exts(exts1, exts2):
    for ext, value in exts2.items():
        exts1[ext] += value
    return exts1


def _sum_extensions(exts, module):
    current_exts = defaultdict(int)
    try:
        suffix = module.filepath.suffix
    except BuiltinModuleError:
        current_exts[""] = 1
    except AttributeError:
        suffix = ""
    else:
        if suffix:
            current_exts[suffix] = 1
        for submodule in _direct(module.modules.values()):
            _sum_extensions(current_exts, submodule)
    _merge_exts(exts, current_exts)


def stats(loader: GriffeLoader) -> dict:
    """Return some loading statistics.

    Parameters:
        loader: The loader to compute stats from.

    Returns:
        Some statistics.
    """
    modules_by_extension = defaultdict(
        int,
        {
            "": 0,
            ".py": 0,
            ".pyi": 0,
            ".pyc": 0,
            ".pyo": 0,
            ".pyd": 0,
            ".so": 0,
        },
    )
    top_modules = loader.modules_collection.members.values()
    for module in top_modules:
        _sum_extensions(modules_by_extension, module)
    n_lines = sum(len(lines) for lines in loader.lines_collection.values())
    return {
        "packages": len(top_modules),
        "modules": len(top_modules) + sum(_n_modules(mod) for mod in top_modules),
        "classes": sum(_n_classes(mod) for mod in top_modules),
        "functions": sum(_n_functions(mod) for mod in top_modules),
        "attributes": sum(_n_attributes(mod) for mod in top_modules),
        "modules_by_extension": modules_by_extension,
        "lines": n_lines,
    }
