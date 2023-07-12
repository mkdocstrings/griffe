"""This module contains utilities to compute loading statistics."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Iterable, Union, cast

from griffe.dataclasses import Class, Module
from griffe.exceptions import BuiltinModuleError

if TYPE_CHECKING:
    from griffe.dataclasses import Alias, Object
    from griffe.loader import GriffeLoader


def _direct(objects: Iterable[Object | Alias]) -> list[Object | Alias]:
    return [obj for obj in objects if not obj.is_alias]


def _n_modules(module: Module) -> int:
    submodules = _direct(module.modules.values())
    return len(submodules) + sum(_n_modules(cast(Module, mod)) for mod in submodules)


def _n_classes(module_or_class: Module | Class) -> int:
    submodules = _direct(module_or_class.modules.values())
    subclasses = _direct(module_or_class.classes.values())
    mods_or_classes = [mc for mc in (*submodules, *subclasses) if not mc.is_alias]
    return len(subclasses) + sum(
        _n_classes(cast(Union[Module, Class], mod_or_class)) for mod_or_class in mods_or_classes
    )


def _n_functions(module_or_class: Module | Class) -> int:
    submodules = _direct(module_or_class.modules.values())
    subclasses = _direct(module_or_class.classes.values())
    functions = _direct(module_or_class.functions.values())
    mods_or_classes = [*submodules, *subclasses]
    return len(functions) + sum(
        _n_functions(cast(Union[Module, Class], mod_or_class)) for mod_or_class in mods_or_classes
    )


def _n_attributes(module_or_class: Module | Class) -> int:
    submodules = _direct(module_or_class.modules.values())
    subclasses = _direct(module_or_class.classes.values())
    attributes = _direct(module_or_class.attributes.values())
    mods_or_classes = [*submodules, *subclasses]
    return len(attributes) + sum(
        _n_attributes(cast(Union[Module, Class], mod_or_class)) for mod_or_class in mods_or_classes
    )


def _merge_exts(exts1: dict[str, int], exts2: dict[str, int]) -> dict[str, int]:
    for ext, value in exts2.items():
        exts1[ext] += value
    return exts1


def _sum_extensions(exts: dict[str, int], module: Module) -> None:
    current_exts = defaultdict(int)
    try:
        suffix = module.filepath.suffix  # type: ignore[union-attr]
    except BuiltinModuleError:
        current_exts[""] = 1
    except AttributeError:
        suffix = ""
    else:
        if suffix:
            current_exts[suffix] = 1
        for submodule in _direct(module.modules.values()):
            _sum_extensions(current_exts, cast(Module, submodule))
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


def _format_stats(stats: dict) -> str:
    lines = []
    packages = stats["packages"]
    modules = stats["modules"]
    classes = stats["classes"]
    functions = stats["functions"]
    attributes = stats["attributes"]
    objects = sum((modules, classes, functions, attributes))
    lines.append("Statistics")
    lines.append("---------------------")
    lines.append("Number of loaded objects")
    lines.append(f"  Modules: {modules}")
    lines.append(f"  Classes: {classes}")
    lines.append(f"  Functions: {functions}")
    lines.append(f"  Attributes: {attributes}")
    lines.append(f"  Total: {objects} across {packages} packages")
    per_ext = stats["modules_by_extension"]
    builtin = per_ext[""]
    regular = per_ext[".py"]
    stubs = per_ext[".pyi"]
    compiled = modules - builtin - regular - stubs
    lines.append("")
    lines.append(f"Total number of lines: {stats['lines']}")
    lines.append("")
    lines.append("Modules")
    lines.append(f"  Builtin: {builtin}")
    lines.append(f"  Compiled: {compiled}")
    lines.append(f"  Regular: {regular}")
    lines.append(f"  Stubs: {stubs}")
    lines.append("  Per extension:")
    for ext, number in sorted(per_ext.items()):
        if ext:
            lines.append(f"    {ext}: {number}")
    visit_time = stats["time_spent_visiting"] / 1000
    inspect_time = stats["time_spent_inspecting"] / 1000
    total_time = visit_time + inspect_time
    visit_percent = visit_time / total_time * 100
    inspect_percent = inspect_time / total_time * 100
    try:
        visit_time_per_module = visit_time / regular
    except ZeroDivisionError:
        visit_time_per_module = 0
    inspected_modules = builtin + compiled
    try:
        inspect_time_per_module = visit_time / inspected_modules
    except ZeroDivisionError:
        inspect_time_per_module = 0
    lines.append("")
    lines.append(
        f"Time spent visiting modules ({regular}): "
        f"{visit_time}ms, {visit_time_per_module:.02f}ms/module ({visit_percent:.02f}%)",
    )
    lines.append(
        f"Time spent inspecting modules ({inspected_modules}): "
        f"{inspect_time}ms, {inspect_time_per_module:.02f}ms/module ({inspect_percent:.02f}%)",
    )
    serialize_time = stats["time_spent_serializing"] / 1000
    serialize_time_per_module = serialize_time / modules
    lines.append(f"Time spent serializing: {serialize_time}ms, {serialize_time_per_module:.02f}ms/module")
    return "\n".join(lines)


__all__ = ["stats"]
