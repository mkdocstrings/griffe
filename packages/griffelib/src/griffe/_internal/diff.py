# SPDX-License-Identifier: ISC

# Copyright (c) 2021, Timothée Mazzucotelli and contributors

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# This module exports utilities to compute the differences between two versions of an API.
# The logic here is to iterate on objects and their members recursively.
#
# The breakage class definitions might sound a bit verbose,
# but declaring them this way helps with (de)serialization,
# which we don't use yet, but could use in the future.

from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from logging import DEBUG
from pathlib import Path
from typing import TYPE_CHECKING, Any

from griffe._internal.enumerations import BreakageKind, ChangeFlag, ChangeKind, ExplanationStyle, ParameterKind
from griffe._internal.exceptions import AliasResolutionError
from griffe._internal.git import _WORKTREE_PREFIX
from griffe._internal.logger import logger

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from griffe._internal.models import Alias, Attribute, Class, Function, Object, Parameter

_POSITIONAL = frozenset((ParameterKind.positional_only, ParameterKind.positional_or_keyword))
_KEYWORD = frozenset((ParameterKind.keyword_only, ParameterKind.positional_or_keyword))
_POSITIONAL_KEYWORD_ONLY = frozenset((ParameterKind.positional_only, ParameterKind.keyword_only))
_VARIADIC = frozenset((ParameterKind.var_positional, ParameterKind.var_keyword))


# Colors for terminal output.
class _ANSI:
    FG_BLACK = "\033[30m"
    FG_RED = "\033[31m"
    FG_GREEN = "\033[32m"
    FG_YELLOW = "\033[33m"
    FG_BLUE = "\033[34m"
    FG_MAGENTA = "\033[35m"
    FG_CYAN = "\033[36m"
    FG_WHITE = "\033[37m"
    FG_RESET = "\033[39m"
    FG_LIGHTBLACK_EX = "\033[90m"
    FG_LIGHTRED_EX = "\033[91m"
    FG_LIGHTGREEN_EX = "\033[92m"
    FG_LIGHTYELLOW_EX = "\033[93m"
    FG_LIGHTBLUE_EX = "\033[94m"
    FG_LIGHTMAGENTA_EX = "\033[95m"
    FG_LIGHTCYAN_EX = "\033[96m"
    FG_LIGHTWHITE_EX = "\033[97m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_RESET = "\033[49m"
    BG_LIGHTBLACK_EX = "\033[100m"
    BG_LIGHTRED_EX = "\033[101m"
    BG_LIGHTGREEN_EX = "\033[102m"
    BG_LIGHTYELLOW_EX = "\033[103m"
    BG_LIGHTBLUE_EX = "\033[104m"
    BG_LIGHTMAGENTA_EX = "\033[105m"
    BG_LIGHTCYAN_EX = "\033[106m"
    BG_LIGHTWHITE_EX = "\033[107m"
    BRIGHT = "\033[1m"
    DIM = "\033[2m"
    NORMAL = "\033[22m"
    RESET_ALL = "\033[0m"


@dataclass(kw_only=True, slots=True)
class Change:
    """A change between two versions of an API."""

    kind: ChangeKind
    """The kind of change."""
    obj: Object | Alias
    """The object related to the change."""
    old_value: Any = None
    """The value in the old API."""
    new_value: Any = None
    """The value in the new API."""
    flags: frozenset[ChangeFlag] = field(default_factory=frozenset)
    """Semantic flags attached to the change."""
    details: str = ""
    """Additional details about the change."""

    def __str__(self) -> str:
        return self.kind.value

    @property
    def is_breaking(self) -> bool:
        """Whether this change is backward-incompatible."""
        return ChangeFlag.BREAKING in self.flags

    def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        """Return this change's data as a dictionary.

        Parameters:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        data: dict[str, Any] = {
            "kind": self.kind,
            "object_path": self.obj.path,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "flags": sorted(self.flags, key=lambda flag: flag.value),
        }
        if self.details:
            data["details"] = self.details
        return data


class Breakage:
    """Breakages can explain what broke from a version to another."""

    kind: BreakageKind
    """The kind of breakage."""

    def __init__(self, obj: Object, old_value: Any, new_value: Any, details: str = "") -> None:
        """Initialize the breakage.

        Parameters:
            obj: The object related to the breakage.
            old_value: The old value.
            new_value: The new, incompatible value.
            details: Some details about the breakage.
        """
        self.obj = obj
        """The object related to the breakage."""
        self.old_value = old_value
        """The old value."""
        self.new_value = new_value
        """The new, incompatible value."""
        self.details = details
        """Some details about the breakage."""

    def __str__(self) -> str:
        return self.kind.value

    def __repr__(self) -> str:
        return self.kind.name

    def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
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

    @property
    def _filepath(self) -> Path:
        if self.obj.is_alias:
            return self.obj.parent.filepath  # ty:ignore[invalid-return-type, unresolved-attribute]
        return self.obj.filepath  # ty:ignore[invalid-return-type]

    @property
    def _relative_filepath(self) -> Path:
        if self.obj.is_alias:
            return self.obj.parent.relative_filepath  # ty:ignore[unresolved-attribute]
        return self.obj.relative_filepath

    @property
    def _relative_package_filepath(self) -> Path:
        if self.obj.is_alias:
            return self.obj.parent.relative_package_filepath  # ty:ignore[unresolved-attribute]
        return self.obj.relative_package_filepath

    @property
    def _location(self) -> Path:
        # Absolute file path probably means temporary worktree.
        # We use our worktree prefix to remove some components
        # of the path on the left (`/tmp/griffe-worktree-*/griffe_*/repo`).
        if self._relative_filepath.is_absolute():
            parts = self._relative_filepath.parts
            for index, part in enumerate(parts):
                if part.startswith(_WORKTREE_PREFIX):
                    return Path(*parts[index + 2 :])
        return self._relative_filepath

    @property
    def _canonical_path(self) -> str:
        if self.obj.is_alias:
            return self.obj.path
        return self.obj.canonical_path

    @property
    def _module_path(self) -> str:
        if self.obj.is_alias:
            return self.obj.parent.module.path  # ty:ignore[unresolved-attribute]
        return self.obj.module.path

    @property
    def _relative_path(self) -> str:
        return self._canonical_path[len(self._module_path) + 1 :] or "<module>"

    @property
    def _lineno(self) -> int:
        # If the object was removed, and we are able to get the location (file path)
        # as a relative path, then we use 0 instead of the original line number
        # (it helps when checking current sources, and avoids pointing to now missing contents).
        if self.kind is BreakageKind.OBJECT_REMOVED and self._relative_filepath != self._location:
            return 0
        if self.obj.is_alias:
            return self.obj.alias_lineno or 0  # ty:ignore[unresolved-attribute]
        return self.obj.lineno or 0

    def _format_location(self, *, colors: bool = True) -> str:
        bright = _ANSI.BRIGHT if colors else ""
        reset = _ANSI.RESET_ALL if colors else ""
        return f"{bright}{self._location}{reset}:{self._lineno}"

    def _format_title(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return self._relative_path

    def _format_kind(self, *, colors: bool = True) -> str:
        yellow = _ANSI.FG_YELLOW if colors else ""
        reset = _ANSI.FG_RESET if colors else ""
        return f"{yellow}{self.kind.value}{reset}"

    def _format_old_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return str(self.old_value)

    def _format_new_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
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

    def _explain_markdown(self) -> str:
        explanation = f"- `{self._relative_path}`: *{self.kind.value}*"
        old = self._format_old_value(colors=False)
        if old and old != "unset":
            old = f"`{old}`"
        new = self._format_new_value(colors=False)
        if new and new != "unset":
            new = f"`{new}`"
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

    def _explain_github(self) -> str:
        location = f"file={self._location},line={self._lineno}"
        title = f"title={self._format_title(colors=False)}"
        explanation = f"::warning {location},{title}::{self.kind.value}"
        old = self._format_old_value(colors=False)
        if old and old != "unset":
            old = f"`{old}`"
        new = self._format_new_value(colors=False)
        if new and new != "unset":
            new = f"`{new}`"
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

    def _explain_azdo(self) -> str:
        location = f"sourcepath={self._location},linenumber={self._lineno}"
        title = f"title={self._format_title(colors=False)}"
        explanation = f"###vso[task.logissue type=warning;{location},{title}]{self.kind.value}"
        old = self._format_old_value(colors=False)
        if old and old != "unset":
            old = f"`{old}`"
        new = self._format_new_value(colors=False)
        if new and new != "unset":
            new = f"`{new}`"
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


class ParameterMovedBreakage(Breakage):
    """Specific breakage class for moved parameters."""

    kind: BreakageKind = BreakageKind.PARAMETER_MOVED

    @property
    def _relative_path(self) -> str:
        return f"{super()._relative_path}({self.old_value.name})"

    def _format_title(self, *, colors: bool = True) -> str:
        blue = _ANSI.FG_BLUE if colors else ""
        reset = _ANSI.FG_RESET if colors else ""
        return f"{super()._relative_path}({blue}{self.old_value.name}{reset})"

    def _format_old_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return ""

    def _format_new_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return ""


class ParameterRemovedBreakage(Breakage):
    """Specific breakage class for removed parameters."""

    kind: BreakageKind = BreakageKind.PARAMETER_REMOVED

    @property
    def _relative_path(self) -> str:
        return f"{super()._relative_path}({self.old_value.name})"

    def _format_title(self, *, colors: bool = True) -> str:
        blue = _ANSI.FG_BLUE if colors else ""
        reset = _ANSI.FG_RESET if colors else ""
        return f"{super()._relative_path}({blue}{self.old_value.name}{reset})"

    def _format_old_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return ""

    def _format_new_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return ""


class ParameterChangedKindBreakage(Breakage):
    """Specific breakage class for parameters whose kind changed."""

    kind: BreakageKind = BreakageKind.PARAMETER_CHANGED_KIND

    @property
    def _relative_path(self) -> str:
        return f"{super()._relative_path}({self.old_value.name})"

    def _format_title(self, *, colors: bool = True) -> str:
        blue = _ANSI.FG_BLUE if colors else ""
        reset = _ANSI.FG_RESET if colors else ""
        return f"{super()._relative_path}({blue}{self.old_value.name}{reset})"

    def _format_old_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return str(self.old_value.kind.value)

    def _format_new_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return str(self.new_value.kind.value)


class ParameterChangedDefaultBreakage(Breakage):
    """Specific breakage class for parameters whose default value changed."""

    kind: BreakageKind = BreakageKind.PARAMETER_CHANGED_DEFAULT

    @property
    def _relative_path(self) -> str:
        return f"{super()._relative_path}({self.old_value.name})"

    def _format_title(self, *, colors: bool = True) -> str:
        blue = _ANSI.FG_BLUE if colors else ""
        reset = _ANSI.FG_RESET if colors else ""
        return f"{super()._relative_path}({blue}{self.old_value.name}{reset})"

    def _format_old_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return str(self.old_value.default)

    def _format_new_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return str(self.new_value.default)


class ParameterChangedRequiredBreakage(Breakage):
    """Specific breakage class for parameters which became required."""

    kind: BreakageKind = BreakageKind.PARAMETER_CHANGED_REQUIRED

    @property
    def _relative_path(self) -> str:
        return f"{super()._relative_path}({self.old_value.name})"

    def _format_title(self, *, colors: bool = True) -> str:
        blue = _ANSI.FG_BLUE if colors else ""
        reset = _ANSI.FG_RESET if colors else ""
        return f"{super()._relative_path}({blue}{self.old_value.name}{reset})"

    def _format_old_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return ""

    def _format_new_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return ""


class ParameterAddedRequiredBreakage(Breakage):
    """Specific breakage class for new parameters added as required."""

    kind: BreakageKind = BreakageKind.PARAMETER_ADDED_REQUIRED

    @property
    def _relative_path(self) -> str:
        return f"{super()._relative_path}({self.new_value.name})"

    def _format_title(self, *, colors: bool = True) -> str:
        blue = _ANSI.FG_BLUE if colors else ""
        reset = _ANSI.FG_RESET if colors else ""
        return f"{super()._relative_path}({blue}{self.new_value.name}{reset})"

    def _format_old_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return ""

    def _format_new_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return ""


class ReturnChangedTypeBreakage(Breakage):
    """Specific breakage class for return values which changed type."""

    kind: BreakageKind = BreakageKind.RETURN_CHANGED_TYPE


class ObjectRemovedBreakage(Breakage):
    """Specific breakage class for removed objects."""

    kind: BreakageKind = BreakageKind.OBJECT_REMOVED

    def _format_old_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return ""

    def _format_new_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return ""


class ObjectChangedKindBreakage(Breakage):
    """Specific breakage class for objects whose kind changed."""

    kind: BreakageKind = BreakageKind.OBJECT_CHANGED_KIND

    def _format_old_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return self.old_value.value

    def _format_new_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
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

    def _format_old_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return "[" + ", ".join(base.canonical_path for base in self.old_value) + "]"

    def _format_new_value(self, *, colors: bool = True) -> str:  # noqa: ARG002
        return "[" + ", ".join(base.canonical_path for base in self.new_value) + "]"


# Reused immutable flag sets avoid allocating a new set for every detected change.
_BREAKING = frozenset((ChangeFlag.BREAKING,))
_DEPRECATION = frozenset((ChangeFlag.DEPRECATION,))
_WARNING = frozenset((ChangeFlag.WARNING,))


def _values_are_equal(old_value: Any, new_value: Any) -> bool:
    if old_value is new_value:
        return True
    try:
        return bool(old_value == new_value)
    except Exception:  # noqa: BLE001 (equality checks sometimes fail, e.g. numpy arrays)
        return False


def _contains_value(values: Iterable[Any], value: Any) -> bool:
    return any(_values_are_equal(candidate, value) for candidate in values)


# TODO: Check decorators? Maybe resolved by extensions and/or dynamic analysis.
def _class_changes(
    old_class: Class,
    new_class: Class,
    *,
    seen_paths: set[str],
) -> Iterator[Change]:
    removed_base = any(not _contains_value(new_class.bases, base) for base in old_class.bases)
    if removed_base:
        yield Change(
            kind=ChangeKind.CLASS_BASE_REMOVED,
            obj=new_class,
            old_value=old_class.bases,
            new_value=new_class.bases,
            flags=_BREAKING,
        )

    added_base = any(not _contains_value(old_class.bases, base) for base in new_class.bases)
    if added_base:
        yield Change(
            kind=ChangeKind.CLASS_BASE_ADDED,
            obj=new_class,
            old_value=old_class.bases,
            new_value=new_class.bases,
            flags=_WARNING,
        )

    yield from _member_changes(old_class, new_class, seen_paths=seen_paths)


def _parameter_kind_is_incompatible(
    old_kind: ParameterKind | None,
    new_kind: ParameterKind | None,
    *,
    has_variadic_args: bool,
    has_variadic_kwargs: bool,
) -> bool:
    return any(
        (
            # Positional-only to keyword-only.
            old_kind is ParameterKind.positional_only and new_kind is ParameterKind.keyword_only,
            # Keyword-only to positional-only.
            old_kind is ParameterKind.keyword_only and new_kind is ParameterKind.positional_only,
            # Positional or keyword to positional-only/keyword-only.
            old_kind is ParameterKind.positional_or_keyword and new_kind in _POSITIONAL_KEYWORD_ONLY,
            # Not keyword-only to variadic keyword, without variadic positional.
            new_kind is ParameterKind.var_keyword
            and old_kind is not ParameterKind.keyword_only
            and not has_variadic_args,
            # Not positional-only to variadic positional, without variadic keyword.
            new_kind is ParameterKind.var_positional
            and old_kind is not ParameterKind.positional_only
            and not has_variadic_kwargs,
        ),
    )


def _parameter_is_required(parameter: Parameter) -> bool:
    return parameter.required and parameter.kind not in _VARIADIC


# TODO: Check decorators? Maybe resolved by extensions and/or dynamic analysis.
def _function_changes(old_function: Function, new_function: Function) -> Iterator[Change]:
    new_params = {}
    for index, param in enumerate(new_function.parameters):
        # Keep the first parameter with a given name, matching the behavior of `Parameters.__getitem__`.
        new_params.setdefault(param.name, (index, param))
    old_param_names = {param.name for param in old_function.parameters}
    param_kinds = {param.kind for param in new_function.parameters}
    has_variadic_args = ParameterKind.var_positional in param_kinds
    has_variadic_kwargs = ParameterKind.var_keyword in param_kinds

    for old_index, old_param in enumerate(old_function.parameters):
        try:
            new_index, new_param = new_params[old_param.name]
        except KeyError:
            swallowed = (
                (old_param.kind is ParameterKind.keyword_only and has_variadic_kwargs)
                or (old_param.kind is ParameterKind.positional_only and has_variadic_args)
                or (old_param.kind is ParameterKind.positional_or_keyword and has_variadic_args and has_variadic_kwargs)
            )
            yield Change(
                kind=ChangeKind.PARAMETER_REMOVED,
                obj=new_function,
                old_value=old_param,
                flags=_WARNING if swallowed else _BREAKING,
            )
            continue

        default_changed = not _values_are_equal(old_param.default, new_param.default)
        old_required = _parameter_is_required(old_param)
        new_required = _parameter_is_required(new_param)
        became_required = new_required and not old_required
        if became_required:
            yield Change(
                kind=ChangeKind.PARAMETER_CHANGED_DEFAULT,
                obj=new_function,
                old_value=old_param,
                new_value=new_param,
                flags=_BREAKING,
            )

        if old_param.kind in _POSITIONAL and new_param.kind in _POSITIONAL and new_index != old_index:
            details = f"position: from {old_index} to {new_index} ({new_index - old_index:+})"
            yield Change(
                kind=ChangeKind.PARAMETER_MOVED,
                obj=new_function,
                old_value=old_param,
                new_value=new_param,
                flags=_BREAKING,
                details=details,
            )

        if old_param.kind is not new_param.kind:
            incompatible_kind = _parameter_kind_is_incompatible(
                old_param.kind,
                new_param.kind,
                has_variadic_args=has_variadic_args,
                has_variadic_kwargs=has_variadic_kwargs,
            )
            yield Change(
                kind=ChangeKind.PARAMETER_CHANGED_KIND,
                obj=new_function,
                old_value=old_param,
                new_value=new_param,
                flags=_BREAKING if incompatible_kind else _WARNING,
            )

        if not _values_are_equal(old_param.annotation, new_param.annotation):
            yield Change(
                kind=ChangeKind.PARAMETER_CHANGED_TYPE,
                obj=new_function,
                old_value=old_param,
                new_value=new_param,
                flags=_WARNING,
            )

        non_variadic = old_param.kind not in _VARIADIC and new_param.kind not in _VARIADIC
        if default_changed and not became_required and non_variadic:
            non_required = not old_required and not new_required
            yield Change(
                kind=ChangeKind.PARAMETER_CHANGED_DEFAULT,
                obj=new_function,
                old_value=old_param,
                new_value=new_param,
                flags=_BREAKING if non_required else frozenset(),
            )

    for new_param in new_function.parameters:
        if new_param.name not in old_param_names:
            yield Change(
                kind=ChangeKind.PARAMETER_ADDED,
                obj=new_function,
                new_value=new_param,
                flags=_BREAKING if _parameter_is_required(new_param) else frozenset(),
            )

    if not _values_are_equal(old_function.returns, new_function.returns):
        yield Change(
            kind=ChangeKind.RETURN_CHANGED_TYPE,
            obj=new_function,
            old_value=old_function.returns,
            new_value=new_function.returns,
            flags=_BREAKING if not _returns_are_compatible(old_function, new_function) else _WARNING,
        )


def _attribute_changes(old_attribute: Attribute, new_attribute: Attribute) -> Iterator[Change]:
    if not _values_are_equal(old_attribute.annotation, new_attribute.annotation):
        yield Change(
            kind=ChangeKind.ATTRIBUTE_CHANGED_TYPE,
            obj=new_attribute,
            old_value=old_attribute.annotation,
            new_value=new_attribute.annotation,
            flags=_WARNING,
        )
    if not _values_are_equal(old_attribute.value, new_attribute.value):
        yield Change(
            kind=ChangeKind.ATTRIBUTE_CHANGED_VALUE,
            obj=new_attribute,
            old_value=old_attribute.value,
            new_value=new_attribute.value,
            flags=_BREAKING,
        )


def _alias_changes(
    old_obj: Object | Alias,
    new_obj: Object | Alias,
    *,
    seen_paths: set[str],
) -> Iterator[Change]:
    try:
        old_member = old_obj.target if old_obj.is_alias else old_obj  # ty:ignore[unresolved-attribute]
        new_member = new_obj.target if new_obj.is_alias else new_obj  # ty:ignore[unresolved-attribute]
    except AliasResolutionError:
        logger.debug("API check: %s | %s: skip alias with unknown target", old_obj.path, new_obj.path)
        return

    yield from _type_based_changes(old_member, new_member, seen_paths=seen_paths)


def _deprecation_changes(old_member: Object | Alias, new_member: Object | Alias) -> Iterator[Change]:
    old_deprecation = old_member.deprecated
    new_deprecation = new_member.deprecated
    if _values_are_equal(old_deprecation, new_deprecation):
        return
    old_is_deprecated = old_member.is_deprecated
    new_is_deprecated = new_member.is_deprecated
    if not old_is_deprecated and not new_is_deprecated:
        return
    if not old_is_deprecated and new_is_deprecated:
        kind = ChangeKind.OBJECT_DEPRECATED
        flags = _DEPRECATION
    elif old_is_deprecated and not new_is_deprecated:
        kind = ChangeKind.OBJECT_UNDEPRECATED
        flags = frozenset()
    else:
        kind = ChangeKind.OBJECT_CHANGED_DEPRECATION
        flags = _DEPRECATION
    yield Change(
        kind=kind,
        obj=new_member,
        old_value=old_deprecation,
        new_value=new_deprecation,
        flags=flags,
    )


def _member_changes(
    old_obj: Object | Alias,
    new_obj: Object | Alias,
    *,
    seen_paths: set[str] | None = None,
) -> Iterator[Change]:
    seen_paths = set() if seen_paths is None else seen_paths
    old_members = old_obj.all_members
    new_members = new_obj.all_members
    debug = logger.isEnabledFor(DEBUG)

    for name, old_member in old_members.items():
        if not old_member.is_public:
            if debug:
                logger.debug("API check: %s.%s: skip non-public object", old_obj.path, name)
            continue
        if debug:
            logger.debug("API check: %s.%s", old_obj.path, name)
        new_member = new_members.get(name)
        if new_member is None or not new_member.is_public:
            yield Change(
                kind=ChangeKind.OBJECT_REMOVED,
                obj=old_member,
                old_value=old_member,
                flags=_BREAKING,
            )
        else:
            yield from _deprecation_changes(old_member, new_member)
            yield from _type_based_changes(old_member, new_member, seen_paths=seen_paths)

    for name, new_member in new_members.items():
        if not new_member.is_public:
            continue
        old_member = old_members.get(name)
        if old_member is None or not old_member.is_public:
            yield Change(
                kind=ChangeKind.OBJECT_ADDED,
                obj=new_member,
                new_value=new_member,
            )


def _type_based_changes(
    old_member: Object | Alias,
    new_member: Object | Alias,
    *,
    seen_paths: set[str],
) -> Iterator[Change]:
    if old_member.path in seen_paths:
        return
    seen_paths.add(old_member.path)
    if old_member.is_alias or new_member.is_alias:
        # Should be first, since there can be the case where there is an alias and another kind of object,
        # which may not be a breaking change.
        yield from _alias_changes(
            old_member,
            new_member,
            seen_paths=seen_paths,
        )
    elif new_member.kind != old_member.kind:
        yield Change(
            kind=ChangeKind.OBJECT_CHANGED_KIND,
            obj=new_member,
            old_value=old_member.kind,
            new_value=new_member.kind,
            flags=_BREAKING,
        )
    elif old_member.is_module:
        yield from _member_changes(
            old_member,
            new_member,
            seen_paths=seen_paths,
        )
    elif old_member.is_class:
        yield from _class_changes(
            old_member,  # ty:ignore[invalid-argument-type]
            new_member,  # ty:ignore[invalid-argument-type]
            seen_paths=seen_paths,
        )
    elif old_member.is_function:
        yield from _function_changes(old_member, new_member)  # ty:ignore[invalid-argument-type]
    elif old_member.is_attribute:
        yield from _attribute_changes(old_member, new_member)  # ty:ignore[invalid-argument-type]


def _returns_are_compatible(old_function: Function, new_function: Function) -> bool:
    # We consider that a return value of `None` only is not a strong contract,
    # it just means that the function returns nothing. We don't expect users
    # to be asserting that the return value is `None`.
    # Therefore we don't consider it a breakage if the return changes from `None`
    # to something else: the function just gained a return value.
    if old_function.returns is None:
        return True

    if new_function.returns is None:
        # NOTE: Should it be configurable to allow/disallow removing a return type?
        return False

    with contextlib.suppress(AttributeError):
        if new_function.returns == old_function.returns:
            return True

    # TODO: Support annotation breaking changes.
    return True


def find_changes(
    old_obj: Object | Alias,
    new_obj: Object | Alias,
) -> Iterator[Change]:
    """Find changes between two versions of the same API.

    The function recursively compares public objects and yields every supported
    change. Semantic flags on each change indicate whether it is a warning,
    deprecation, or backward-incompatible change.

    Parameters:
        old_obj: The old version of an object.
        new_obj: The new version of an object.

    Yields:
        API changes.
    """
    yield from _member_changes(old_obj, new_obj)


_BREAKAGE_TYPES: dict[ChangeKind, type[Breakage]] = {
    ChangeKind.ATTRIBUTE_CHANGED_TYPE: AttributeChangedTypeBreakage,
    ChangeKind.ATTRIBUTE_CHANGED_VALUE: AttributeChangedValueBreakage,
    ChangeKind.CLASS_BASE_REMOVED: ClassRemovedBaseBreakage,
    ChangeKind.OBJECT_CHANGED_KIND: ObjectChangedKindBreakage,
    ChangeKind.OBJECT_REMOVED: ObjectRemovedBreakage,
    ChangeKind.PARAMETER_ADDED: ParameterAddedRequiredBreakage,
    ChangeKind.PARAMETER_CHANGED_DEFAULT: ParameterChangedDefaultBreakage,
    ChangeKind.PARAMETER_CHANGED_KIND: ParameterChangedKindBreakage,
    ChangeKind.PARAMETER_MOVED: ParameterMovedBreakage,
    ChangeKind.PARAMETER_REMOVED: ParameterRemovedBreakage,
    ChangeKind.RETURN_CHANGED_TYPE: ReturnChangedTypeBreakage,
}


def _change_as_breakage(change: Change) -> Breakage:
    breakage_type = _BREAKAGE_TYPES[change.kind]
    new_value = change.new_value
    if change.kind is ChangeKind.ATTRIBUTE_CHANGED_VALUE and new_value is None:
        new_value = "unset"
    elif (
        change.kind is ChangeKind.PARAMETER_CHANGED_DEFAULT
        and _parameter_is_required(change.new_value)
        and not _parameter_is_required(change.old_value)
    ):
        breakage_type = ParameterChangedRequiredBreakage
    return breakage_type(change.obj, change.old_value, new_value, details=change.details)  # ty:ignore[invalid-argument-type]


def find_breaking_changes(
    old_obj: Object | Alias,
    new_obj: Object | Alias,
) -> Iterator[Breakage]:
    """Find breaking changes between two versions of the same API.

    The function will iterate recursively on all objects
    and yield breaking changes with detailed information.

    Parameters:
        old_obj: The old version of an object.
        new_obj: The new version of an object.

    Yields:
        Breaking changes.

    Examples:
        >>> import sys, griffe
        >>> new = griffe.load("pkg")
        >>> old = griffe.load_git("pkg", "1.2.3")
        >>> for breakage in griffe.find_breaking_changes(old, new)
        ...     print(breakage.explain(), file=sys.stderr)
    """
    for change in find_changes(old_obj, new_obj):
        if change.is_breaking:
            yield _change_as_breakage(change)
