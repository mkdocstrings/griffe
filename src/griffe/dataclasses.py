"""This module contains the data classes that represent Python objects.

The different objects are modules, classes, functions, and data
(variables like module/class/instance attributes).
"""

from __future__ import annotations

import enum
from pathlib import Path


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
        lineno: The object starting line, or None for modules. Lines start at 1..
        endlineno: The object ending line (inclusive), or None for modules..
        parent: The object parent, or None if it is the top module.
        members: The object members.
        labels: The object labels.
    """

    kind: Kind

    def __init__(self, name: str, lineno: int | None = None, endlineno: int | None = None) -> None:
        """Initialize the object.

        Arguments:
            name: The object name, as declared in the code.
            lineno: The object starting line, or None for modules. Lines start at 1.
            endlineno: The object ending line (inclusive), or None for modules.
        """
        self.name: str = name
        self.lineno: int | None = lineno
        self.endlineno: int | None = endlineno
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

    @property
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

    @property
    def path(self) -> str:
        """Return the dotted path / import path of this object.

        Returns:
            A dotted path.
        """
        if not self.parent:
            return self.name
        return ".".join((self.parent.path, self.name))

    def as_dict(self, full: bool = False) -> dict:
        """Return this object's data as a dictionary.

        Arguments:
            full: Whether to return full info, or just base info.

        Returns:
            A dictionary.
        """
        base = {
            "name": self.name,
            "members": [member.as_dict(full) for member in self.members.values()],
            "labels": self.labels,
            "kind": self.kind,
        }
        if self.lineno:
            base["lineno"] = self.lineno
        if self.endlineno:
            base["endlineno"] = self.endlineno

        if full:
            base.update(
                {
                    "filepath": str(self.filepath),
                    "path": self.path,
                }
            )

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

    def as_dict(self, full: bool = False) -> dict:
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


class Data(Object):
    """The class representing a Python module/class/instance attribute."""

    kind = Kind.DATA
