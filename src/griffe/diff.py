"""This module exports "breaking changes" related utilities."""

from __future__ import annotations

import contextlib
import enum
from typing import Any, Iterable, Iterator

from colorama import Fore, Style

from griffe.dataclasses import Alias, Attribute, Class, Function, Object, ParameterKind
from griffe.logger import get_logger

POSITIONAL = frozenset((ParameterKind.positional_only, ParameterKind.positional_or_keyword))
KEYWORD = frozenset((ParameterKind.keyword_only, ParameterKind.positional_or_keyword))
POSITIONAL_KEYWORD_ONLY = frozenset((ParameterKind.positional_only, ParameterKind.keyword_only))

logger = get_logger(__name__)


class ExplanationStyle(enum.Enum):
    """An enumeration of the possible styles for explanations."""

    ONE_LINE: str = "oneline"
    VERBOSE: str = "verbose"


class BreakageKind(enum.Enum):
    """An enumeration of the possible breakages."""

    PARAMETER_MOVED: str = "Positional parameter was moved"
    PARAMETER_REMOVED: str = "Parameter was removed"
    PARAMETER_CHANGED_KIND: str = "Parameter kind was changed"
    PARAMETER_CHANGED_DEFAULT: str = "Parameter default was changed"
    PARAMETER_CHANGED_REQUIRED: str = "Parameter is now required"
    PARAMETER_ADDED_REQUIRED: str = "Parameter was added as required"
    RETURN_CHANGED_TYPE: str = "Return types are incompatible"
    OBJECT_REMOVED: str = "Public object was removed"
    OBJECT_CHANGED_KIND: str = "Public object points to a different kind of object"
    ATTRIBUTE_CHANGED_TYPE: str = "Attribute types are incompatible"
    ATTRIBUTE_CHANGED_VALUE: str = "Attribute value was changed"
    CLASS_REMOVED_BASE: str = "Base class was removed"


class Breakage:
    """Breakages can explain what broke from a version to another."""

    kind: BreakageKind

    def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
        """Initialize the breakage.

        Parameters:
            obj: The object related to the breakage.
            old_value: The old value.
            new_value: The new, incompatible value.
            details: Some details about the breakage.
        """
        self.obj = obj
        self.old_value = old_value
        self.new_value = new_value
        self.details = details

    def __str__(self) -> str:
        return f"{self.kind.value}"

    def __repr__(self) -> str:
        return f"<{self.kind.name}>"

    def as_dict(self, full: bool = False, **kwargs: Any) -> dict[str, Any]:
        """Return this object's data as a dictionary.

        Parameters:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        return {
            "kind": self.kind,
            "object_path": self.obj.path,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }

    def explain(self, style: ExplanationStyle = ExplanationStyle.ONE_LINE) -> str:
        """Explain the breakage by showing old and new value.

        Parameters:
            style: The explanation style to use.

        Returns:
            An explanation.
        """
        return getattr(self, f"_explain_{style.value}")()

    def _relative_path(self) -> str:
        return self.obj.canonical_path[len(self.obj.module.canonical_path) + 1 :]

    def _format_location(self) -> str:
        return f"{Style.BRIGHT}{self.obj.filepath}{Style.RESET_ALL}:{self.obj.lineno}"

    def _format_title(self) -> str:
        return self._relative_path()

    def _format_kind(self) -> str:
        return f"{Fore.YELLOW}{self.kind.value}{Fore.RESET}"

    def _format_old_value(self) -> str:
        return str(self.old_value)

    def _format_new_value(self) -> str:
        return str(self.new_value)

    def _explain_oneline(self) -> str:
        explanation = f"{self._format_location()}: {self._format_title()}: {self._format_kind()}"
        old = self._format_old_value()
        new = self._format_new_value()
        if old and new:
            change = f"{old} -> {new}"
        elif old:
            change = old
        elif new:
            change = new
        else:
            change = ""
        if change:
            return f"{explanation}: {change}"
        return explanation

    def _explain_verbose(self) -> str:
        lines = [f"{self._format_location()}: {self._format_title()}:"]
        kind = self._format_kind()
        old = self._format_old_value()
        new = self._format_new_value()
        if old or new:
            lines.append(f"{kind}:")
        else:
            lines.append(kind)
        if old:
            lines.append(f"  Old: {old}")
        if new:
            lines.append(f"  New: {new}")
        if self.details:
            lines.append(f"  Details: {self.details}")
        lines.append("")
        return "\n".join(lines)


class ParameterMovedBreakage(Breakage):
    """Specific breakage class for moved parameters."""

    kind: BreakageKind = BreakageKind.PARAMETER_MOVED

    def _format_title(self) -> str:
        return f"{self._relative_path()}({Fore.BLUE}{self.old_value.name}{Fore.RESET})"

    def _format_old_value(self) -> str:
        return ""

    def _format_new_value(self) -> str:
        return ""


class ParameterRemovedBreakage(Breakage):
    """Specific breakage class for removed parameters."""

    kind: BreakageKind = BreakageKind.PARAMETER_REMOVED

    def _format_title(self) -> str:
        return f"{self._relative_path()}({Fore.BLUE}{self.old_value.name}{Fore.RESET})"

    def _format_old_value(self) -> str:
        return ""

    def _format_new_value(self) -> str:
        return ""


class ParameterChangedKindBreakage(Breakage):
    """Specific breakage class for parameters whose kind changed."""

    kind: BreakageKind = BreakageKind.PARAMETER_CHANGED_KIND

    def _format_title(self) -> str:
        return f"{self._relative_path()}({Fore.BLUE}{self.old_value.name}{Fore.RESET})"

    def _format_old_value(self) -> str:
        return str(self.old_value.kind.value)

    def _format_new_value(self) -> str:
        return str(self.new_value.kind.value)


class ParameterChangedDefaultBreakage(Breakage):
    """Specific breakage class for parameters whose default value changed."""

    kind: BreakageKind = BreakageKind.PARAMETER_CHANGED_DEFAULT

    def _format_title(self) -> str:
        return f"{self._relative_path()}({Fore.BLUE}{self.old_value.name}{Fore.RESET})"

    def _format_old_value(self) -> str:
        return str(self.old_value.default)

    def _format_new_value(self) -> str:
        return str(self.new_value.default)


class ParameterChangedRequiredBreakage(Breakage):
    """Specific breakage class for parameters which became required."""

    kind: BreakageKind = BreakageKind.PARAMETER_CHANGED_REQUIRED

    def _format_title(self) -> str:
        return f"{self._relative_path()}({Fore.BLUE}{self.old_value.name}{Fore.RESET})"

    def _format_old_value(self) -> str:
        return ""

    def _format_new_value(self) -> str:
        return ""


class ParameterAddedRequiredBreakage(Breakage):
    """Specific breakage class for new parameters added as required."""

    kind: BreakageKind = BreakageKind.PARAMETER_ADDED_REQUIRED

    def _format_title(self) -> str:
        return f"{self._relative_path()}({Fore.BLUE}{self.new_value.name}{Fore.RESET})"

    def _format_old_value(self) -> str:
        return ""

    def _format_new_value(self) -> str:
        return ""


class ReturnChangedTypeBreakage(Breakage):
    """Specific breakage class for return values which changed type."""

    kind: BreakageKind = BreakageKind.RETURN_CHANGED_TYPE


class ObjectRemovedBreakage(Breakage):
    """Specific breakage class for removed objects."""

    kind: BreakageKind = BreakageKind.OBJECT_REMOVED

    def _format_old_value(self) -> str:
        return ""

    def _format_new_value(self) -> str:
        return ""


class ObjectChangedKindBreakage(Breakage):
    """Specific breakage class for objects whose kind changed."""

    kind: BreakageKind = BreakageKind.OBJECT_CHANGED_KIND

    def _format_old_value(self) -> str:
        return self.old_value.value

    def _format_new_value(self) -> str:
        return self.new_value.value


class AttributeChangedTypeBreakage(Breakage):
    """Specific breakage class for attributes whose type changed."""

    kind: BreakageKind = BreakageKind.ATTRIBUTE_CHANGED_TYPE


class AttributeChangedValueBreakage(Breakage):
    """Specific breakage class for attributes whose value changed."""

    kind: BreakageKind = BreakageKind.ATTRIBUTE_CHANGED_VALUE


class ClassRemovedBaseBreakage(Breakage):
    """Specific breakage class for removed base classes."""

    kind: BreakageKind = BreakageKind.CLASS_REMOVED_BASE

    def _format_old_value(self) -> str:
        return "[" + ", ".join(base.full for base in self.old_value) + "]"

    def _format_new_value(self) -> str:
        return "[" + ", ".join(base.full for base in self.new_value) + "]"


# TODO: decorators!
def _class_incompatibilities(old_class: Class, new_class: Class, ignore_private: bool = True) -> Iterable[Breakage]:
    yield from ()  # noqa: WPS353
    if new_class.bases != old_class.bases:
        if len(new_class.bases) < len(old_class.bases):
            yield ClassRemovedBaseBreakage(new_class, old_class.bases, new_class.bases)
        else:
            # TODO: check mro
            ...
    yield from _member_incompatibilities(old_class, new_class, ignore_private=ignore_private)


# TODO: decorators!
def _function_incompatibilities(old_function: Function, new_function: Function) -> Iterator[Breakage]:  # noqa: WPS231
    new_param_names = [param.name for param in new_function.parameters]
    param_kinds = {param.kind for param in new_function.parameters}
    has_variadic_args = ParameterKind.var_positional in param_kinds
    has_variadic_kwargs = ParameterKind.var_keyword in param_kinds

    for old_index, old_param in enumerate(old_function.parameters):
        # checking if parameter was removed
        if old_param.name not in new_function.parameters:
            swallowed = (
                (old_param.kind is ParameterKind.keyword_only and has_variadic_kwargs)  # noqa: WPS222,WPS408
                or (old_param.kind is ParameterKind.positional_only and has_variadic_args)
                or (old_param.kind is ParameterKind.positional_or_keyword and has_variadic_args and has_variadic_kwargs)
            )
            if not swallowed:
                yield ParameterRemovedBreakage(new_function, old_param, None)
            continue

        # checking if parameter became required
        new_param = new_function.parameters[old_param.name]
        if new_param.required and not old_param.required:
            yield ParameterChangedRequiredBreakage(new_function, old_param, new_param)

        # checking if parameter was moved
        if old_param.kind in POSITIONAL and new_param.kind in POSITIONAL:
            new_index = new_param_names.index(old_param.name)
            if new_index != old_index:
                details = f"position: from {old_index} to {new_index} ({new_index - old_index:+})"
                yield ParameterMovedBreakage(new_function, old_param, new_param, details=details)

        # checking if parameter changed kind
        if old_param.kind is not new_param.kind:
            incompatible_kind = any(
                (
                    # positional-only to keyword-only
                    old_param.kind is ParameterKind.positional_only and new_param.kind is ParameterKind.keyword_only,
                    # keyword-only to positional-only
                    old_param.kind is ParameterKind.keyword_only and new_param.kind is ParameterKind.positional_only,
                    # positional or keyword to positional-only/keyword-only
                    old_param.kind is ParameterKind.positional_or_keyword and new_param.kind in POSITIONAL_KEYWORD_ONLY,
                    # not keyword-only to variadic keyword, without variadic positional
                    new_param.kind is ParameterKind.var_keyword
                    and old_param.kind is not ParameterKind.keyword_only
                    and not has_variadic_args,
                    # not positional-only to variadic positional, without variadic keyword
                    new_param.kind is ParameterKind.var_positional
                    and old_param.kind is not ParameterKind.positional_only
                    and not has_variadic_kwargs,
                )
            )
            if incompatible_kind:
                yield ParameterChangedKindBreakage(new_function, old_param, new_param)

        # checking if parameter changed default
        breakage = ParameterChangedDefaultBreakage(new_function, old_param, new_param)
        try:
            if old_param.default is not None and old_param.default != new_param.default:
                yield breakage
        except Exception:  # equality checks sometimes fail, e.g. numpy arrays
            # TODO: emitting breakage on a failed comparison could be a preference
            yield breakage

    # checking if required parameters were added
    for new_param in new_function.parameters:  # noqa: WPS440
        if new_param.name not in old_function.parameters and new_param.required:
            yield ParameterAddedRequiredBreakage(new_function, None, new_param)

    if not _returns_are_compatible(old_function, new_function):
        yield ReturnChangedTypeBreakage(new_function, old_function.returns, new_function.returns)


def _attribute_incompatibilities(old_attribute: Attribute, new_attribute: Attribute) -> Iterable[Breakage]:
    # TODO: use beartype.peps.resolve_pep563 and beartype.door.is_subhint?
    # if old_attribute.annotation is not None and new_attribute.annotation is not None:
    #     if not is_subhint(new_attribute.annotation, old_attribute.annotation):
    #         yield AttributeChangedTypeBreakage(new_attribute, old_attribute.annotation, new_attribute.annotation)
    if old_attribute.value != new_attribute.value:
        yield AttributeChangedValueBreakage(new_attribute, old_attribute.value, new_attribute.value)


def _member_incompatibilities(  # noqa: WPS231
    old_obj: Object | Alias,
    new_obj: Object | Alias,
    ignore_private: bool = True,
) -> Iterator[Breakage]:
    for name, old_member in old_obj.members.items():
        if ignore_private and name.startswith("_"):
            logger.debug(f"API check: {old_obj.path}.{name}: skip private object")
            continue

        if old_member.is_alias:
            logger.debug(f"API check: {old_obj.path}.{name}: skip alias")
            continue  # TODO

        logger.debug(f"API check: {old_obj.path}.{name}")
        try:
            new_member = new_obj.members[name]
        except KeyError:
            if old_member.is_exported(explicitely=False):
                yield ObjectRemovedBreakage(old_member, old_member, None)  # type: ignore[arg-type]
            continue

        if new_member.kind != old_member.kind:
            yield ObjectChangedKindBreakage(new_member, old_member.kind, new_member.kind)  # type: ignore[arg-type]
        elif old_member.is_module:
            yield from _member_incompatibilities(old_member, new_member, ignore_private=ignore_private)  # type: ignore[arg-type]
        elif old_member.is_class:
            yield from _class_incompatibilities(old_member, new_member, ignore_private=ignore_private)  # type: ignore[arg-type]
        elif old_member.is_function:
            yield from _function_incompatibilities(old_member, new_member)  # type: ignore[arg-type]
        elif old_member.is_attribute:
            yield from _attribute_incompatibilities(old_member, new_member)  # type: ignore[arg-type]


def _returns_are_compatible(old_function: Function, new_function: Function) -> bool:
    if old_function.returns is None:
        return True
    if new_function.returns is None:
        # TODO: it should be configurable to allow/disallow removing a return type
        return False

    with contextlib.suppress(AttributeError):
        if new_function.returns == old_function.returns:
            return True

    # TODO: use beartype.peps.resolve_pep563 and beartype.door.is_subhint?
    return True


find_breaking_changes = _member_incompatibilities
