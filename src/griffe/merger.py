"""This module contains utilities to merge data together."""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from griffe.exceptions import AliasResolutionError, CyclicAliasError
from griffe.logger import get_logger

if TYPE_CHECKING:
    from griffe.dataclasses import Attribute, Class, Function, Module, Object


logger = get_logger(__name__)


def _merge_module_stubs(module: Module, stubs: Module) -> None:
    _merge_stubs_docstring(module, stubs)
    _merge_stubs_overloads(module, stubs)
    _merge_stubs_members(module, stubs)


def _merge_class_stubs(class_: Class, stubs: Class) -> None:
    _merge_stubs_docstring(class_, stubs)
    _merge_stubs_overloads(class_, stubs)
    _merge_stubs_members(class_, stubs)


def _merge_function_stubs(function: Function, stubs: Function) -> None:
    _merge_stubs_docstring(function, stubs)
    for parameter in stubs.parameters:
        with suppress(KeyError):
            function.parameters[parameter.name].annotation = parameter.annotation
    function.returns = stubs.returns


def _merge_attribute_stubs(attribute: Attribute, stubs: Attribute) -> None:
    _merge_stubs_docstring(attribute, stubs)
    attribute.annotation = stubs.annotation


def _merge_stubs_docstring(obj: Object, stubs: Object) -> None:
    if not obj.docstring and stubs.docstring:
        obj.docstring = stubs.docstring


def _merge_stubs_overloads(obj: Module | Class, stubs: Module | Class) -> None:
    for function_name, overloads in list(stubs.overloads.items()):
        if overloads:
            with suppress(KeyError):
                obj[function_name].overloads = overloads
        del stubs.overloads[function_name]  # noqa: WPS420


def _merge_stubs_members(obj: Module | Class, stubs: Module | Class) -> None:  # noqa: WPS231
    for member_name, stub_member in stubs.members.items():
        if member_name in obj.members:
            obj_member = obj[member_name]
            with suppress(AliasResolutionError, CyclicAliasError):
                if obj_member.kind is not stub_member.kind:
                    logger.debug(f"Cannot merge stubs of kind {stub_member.kind} into object of kind {obj_member.kind}")
                elif obj_member.is_class:
                    _merge_class_stubs(obj_member, stub_member)  # type: ignore[arg-type]
                elif obj_member.is_function:
                    _merge_function_stubs(obj_member, stub_member)  # type: ignore[arg-type]
                elif obj_member.is_attribute:
                    _merge_attribute_stubs(obj_member, stub_member)  # type: ignore[arg-type]
        else:
            stub_member.runtime = False
            obj[member_name] = stub_member


def merge_stubs(mod1: Module, mod2: Module) -> Module:
    """Merge stubs into a module.

    Parameters:
        mod1: A regular module or stubs module.
        mod2: A regular module or stubs module.

    Raises:
        ValueError: When both modules are regular modules (no stubs is passed).

    Returns:
        The regular module.
    """
    logger.debug(f"Trying to merge {mod1.filepath} and {mod2.filepath}")
    if mod1.filepath.suffix == ".pyi":  # type: ignore[union-attr]
        stubs = mod1
        module = mod2
    elif mod2.filepath.suffix == ".pyi":  # type: ignore[union-attr]
        stubs = mod2
        module = mod1
    else:
        raise ValueError("cannot merge regular (non-stubs) modules together")
    _merge_module_stubs(module, stubs)
    return module
