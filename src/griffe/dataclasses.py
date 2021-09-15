"""This module contains the data classes that represent Python objects.

The different objects are modules, classes, functions, and data
(variables like module/class/instance attributes).
"""

from __future__ import annotations

import enum
import inspect
from pathlib import Path
from typing import Any

ParameterKind = inspect._ParameterKind  # noqa: WPS437


class Docstring:
    """This class represents docstrings.

    Attributes:
        value: The actual documentation string, cleaned up.
        lineno: The starting line number.
        endlineno: The ending line number.
    """

    def __init__(self, value: str, lineno: int | None, endlineno: int | None) -> None:
        """Initialize the docstring.

        Arguments:
            value: The docstring value.
            lineno: The starting line number.
            endlineno: The ending line number.
        """
        self.value: str = inspect.cleandoc(value)
        self.lineno: int | None = lineno
        self.endlineno: int | None = endlineno

    def as_dict(self, full=False) -> dict[str, Any]:
        """Return this docstring's data as a dictionary.

        Arguments:
            full: Whether to return full info, or just base info.

        Returns:
            A dictionary.
        """
        return {
            "value": self.value,
            "lineno": self.lineno,
            "endlineno": self.endlineno,
        }


class Argument:
    """This class represent a function argument.

    Attributes:
        name: The argument name.
        annotation: The argument annotation, if any.
        kind: The argument kind (see [`inspect.Parameter.kind`][]).
        default: The argument default, if any.
    """

    def __init__(self, name: str, annotation: str | None, kind: ParameterKind, default: str | None) -> None:
        """Initialize the argument.

        Arguments:
            name: The argument name.
            annotation: The argument annotation, if any.
            kind: The argument kind (see [`inspect.Parameter.kind`][]).
            default: The argument default, if any.
        """
        self.name: str = name
        self.annotation: str | None = annotation
        self.kind: ParameterKind = kind
        self.default: str | None = default

    def as_dict(self, full=False) -> dict[str, Any]:
        """Return this argument's data as a dictionary.

        Arguments:
            full: Whether to return full info, or just base info.

        Returns:
            A dictionary.
        """
        return {
            "name": self.name,
            "annotation": self.annotation,
            "kind": self.kind,
            "default": self.default,
        }


class Kind(enum.Enum):
    """Enumeration of the different objects kinds.

    Attributes:
        MODULE: The module kind.
        CLASS: The class kind.
        FUNCTION: The function kind.
        DATA: The data kind.
    """

    MODULE: str = "module"
    CLASS: str = "class"
    FUNCTION: str = "function"
    DATA: str = "data"


class Object:
    """An abstract class representing a Python object.

    Attributes:
        kind: The object kind.
        name: The object name.
        lineno: The object starting line, or None for modules. Lines start at 1.
        endlineno: The object ending line (inclusive), or None for modules.
        docstring: The object docstring.
        parent: The object parent, or None if it is the top module.
        members: The object members.
        labels: The object labels.
    """

    kind: Kind

    def __init__(
        self,
        name: str,
        lineno: int | None = None,
        endlineno: int | None = None,
        docstring: Docstring | None = None,
    ) -> None:
        """Initialize the object.

        Arguments:
            name: The object name, as declared in the code.
            lineno: The object starting line, or None for modules. Lines start at 1.
            endlineno: The object ending line (inclusive), or None for modules.
            docstring: The object docstring.
        """
        self.name: str = name
        self.lineno: int | None = lineno
        self.endlineno: int | None = endlineno
        self.docstring: Docstring | None = docstring
        self.parent: Module | Class | None = None
        self.members: dict[str, Module | Class | Function | Data] = {}
        self.labels: set[str] = set()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.name!r}, {self.lineno!r}, {self.endlineno!r})>"

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if not key:
                raise ValueError("cannot set self (empty key)")
            parts = key.split(".", 1)
        else:
            parts = key
        if not parts:
            raise ValueError("cannot set self (empty parts)")
        if len(parts) == 1:
            self.members[parts[0]] = value
            value.parent = self
        else:
            self.members[parts[0]][parts[1]] = value

    def __getitem__(self, key):
        if isinstance(key, str):
            if not key:
                return self
            parts = key.split(".", 1)
        else:
            parts = key
        if not parts:
            return self
        if len(parts) == 1:
            return self.members[parts[0]]
        return self.members[parts[0]][parts[1]]

    @property
    def module(self) -> Module:
        """Return the parent module of this object.

        Raises:
            ValueError: When the object is not a module and does not have a parent.

        Returns:
            The parent module.
        """
        if isinstance(self, Module):
            return self
        if self.parent:
            return self.parent.module
        raise ValueError

    @cached_property
    def package(self) -> Module:
        """Return the absolute top module (the package) of this object.

        Returns:
            The parent module.
        """
        module = self.module
        while module.parent:
            module = module.parent  # type: ignore
        return module

    def filepath(self) -> Path | None:
        """Return the file path where this object was defined.

        It should never return None for non-module objects,
        as they should always have a parent module.
        If not, `self.module` would trigger a `ValueError` anyway.
        If it _does_ return None, it means the tree was not built correctly.

        Returns:
            A file path.
        """
        return self.module.filepath

    @cached_property
    def relative_filepath(self) -> Path | None:
        """Return the file path where this object was defined, relative to the top module path.

        Returns:
            A file path.
        """
        return self.module.filepath.relative_to(self.package.filepath.parent.parent)  # type: ignore

    def path(self) -> str:
        """Return the dotted path / import path of this object.

        Returns:
            A dotted path.
        """
        if not self.parent:
            return self.name
        return ".".join((self.parent.path, self.name))

    def as_dict(self, full: bool = False) -> dict[str, Any]:
        """Return this object's data as a dictionary.

        Arguments:
            full: Whether to return full info, or just base info.

        Returns:
            A dictionary.
        """
        base = {
            "kind": self.kind,
            "name": self.name,
        }

        if full:
            base.update(
                {
                    "path": self.path,
                    "relative_filepath": self.relative_filepath,
                }
            )

        if self.lineno:
            base["lineno"] = self.lineno
        if self.endlineno:
            base["endlineno"] = self.endlineno
        if self.docstring:
            base["docstring"] = self.docstring

        # doing this last for a prettier JSON dump
        base["labels"] = self.labels
        base["members"] = [member.as_dict(full) for member in self.members.values()]

        return base


class Module(Object):
    """The class representing a Python module."""

    kind = Kind.MODULE

    def __init__(self, *args, filepath: Path | None = None, **kwargs) -> None:
        """Initialize the module.

        Arguments:
            *args: See [`griffe.dataclasses.Object`][].
            filepath: The module file path. It can be null for namespace packages or non-importable folders.
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self._filepath = filepath

    def __repr__(self) -> str:
        return f"<Module({self._filepath!r})>"

    @property
    def filepath(self) -> Path | None:
        """Get the file path of this module.

        Returns:
            The module's file path.
        """
        return self._filepath

    @property
    def is_init_module(self) -> bool:
        """Tell if this module is an `__init__.py` module.

        Returns:
            True or False.
        """
        return bool(self.filepath) and self.filepath.name == "__init__.py"  # type: ignore

    @property
    def is_folder(self) -> bool:
        """Tell if this module is a non-importable folder.

        Returns:
            True or False.
        """
        return bool(self.parent) and not self.filepath

    @property
    def is_package(self) -> bool:
        """Tell if this module is a package (top module).

        Returns:
            True or False.
        """
        return not bool(self.parent) and self.is_init_module

    @property
    def is_subpackage(self) -> bool:
        """Tell if this module is a subpackage.

        Returns:
            True or False.
        """
        return bool(self.parent) and self.is_init_module

    @property
    def is_namespace_package(self) -> bool:
        """Tell if this module is a namespace package (top folder, no `__init__.py`).

        Returns:
            True or False.
        """
        return not self.parent and not self.filepath

    @property
    def is_namespace_subpackage(self) -> bool:
        """Tell if this module is a namespace subpackage.

        Returns:
            True or False.
        """
        return (
            self.parent
            and not self.filepath
            and self.parent.is_namespace_subpackage  # type: ignore  # modules parents are always modules
            or self.parent.is_namespace_package  # type: ignore  # modules parents are always modules
        )

    def as_dict(self, full: bool = False) -> dict[str, Any]:
        """Return this module's data as a dictionary.

        Arguments:
            full: Whether to return full info, or just base info.

        Returns:
            A dictionary.
        """
        base = super().as_dict(full=full)
        base["filepath"] = str(self.filepath) if self.filepath else None
        return base


class Class(Object):
    """The class representing a Python class."""

    kind = Kind.CLASS


class Function(Object):
    """The class representing a Python function."""

    kind = Kind.FUNCTION

    def __init__(self, *args, arguments: list[Argument] | None = None, returns: str | None = None, **kwargs) -> None:
        """Initialize the module.

        Arguments:
            *args: See [`griffe.dataclasses.Object`][].
            arguments: The function arguments.
            returns: The function return annotation.
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self.arguments = arguments or []
        self.returns = returns

    def as_dict(self, full: bool = False) -> dict[str, Any]:
        """Return this function's data as a dictionary.

        Arguments:
            full: Whether to return full info, or just base info.

        Returns:
            A dictionary.
        """
        base = super().as_dict(full=full)
        base["arguments"] = [arg.as_dict(full=full) for arg in self.arguments]
        base["returns"] = self.returns
        return base


class Data(Object):
    """The class representing a Python module/class/instance attribute."""

    kind = Kind.DATA
