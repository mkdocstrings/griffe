"""This module contains the data classes that represent Python objects.

The different objects are modules, classes, functions, and data
(variables like module/class/instance attributes).
"""

from __future__ import annotations

import enum
import inspect
from functools import cached_property
from pathlib import Path
from typing import Any

from griffe.docstrings.dataclasses import DocstringSection
from griffe.docstrings.parsers import Parser, parse  # noqa: WPS347

ParameterKind = inspect._ParameterKind  # noqa: WPS437


class Decorator:
    """This class represents decorators.

    Attributes:
        lineno: The starting line number.
        endlineno: The ending line number.
    """

    def __init__(self, lineno: int | None, endlineno: int | None) -> None:
        """Initialize the decorator.

        Arguments:
            lineno: The starting line number.
            endlineno: The ending line number.
        """
        self.lineno: int | None = lineno
        self.endlineno: int | None = endlineno

    def as_dict(self, **kwargs) -> dict[str, Any]:
        """Return this decorator's data as a dictionary.

        Arguments:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        return {
            "lineno": self.lineno,
            "endlineno": self.endlineno,
        }


class Docstring:
    """This class represents docstrings.

    Attributes:
        value: The actual documentation string, cleaned up.
        lineno: The starting line number.
        endlineno: The ending line number.
        parent: The parent object on which this docstring is attached.
    """

    def __init__(
        self,
        value: str,
        lineno: int | None,
        endlineno: int | None,
        parent: Module | Class | Function | Data | None = None,
    ) -> None:
        """Initialize the docstring.

        Arguments:
            value: The docstring value.
            lineno: The starting line number.
            endlineno: The ending line number.
            parent: The parent object on which this docstring is attached.
        """
        self.value: str = inspect.cleandoc(value)
        self.lineno: int | None = lineno
        self.endlineno: int | None = endlineno
        self.parent: Module | Class | Function | Data | None = parent

    @cached_property
    def lines(self) -> list[str]:
        """Returns the lines of the docstring.

        Returns:
            The docstring's lines.
        """
        return self.value.split("\n")

    @cached_property
    def parsed(self) -> list[DocstringSection]:
        """Return the docstring, parsed into structured data.

        Returns:
            The parsed docstring.
        """
        return self.parse()

    def parse(self, docstring_parser: Parser = Parser.google, **options) -> list[DocstringSection]:
        """Parse the docstring into structured data.

        Arguments:
            docstring_parser: The docstring parser to use.
            **options: Additional docstring parsing options.

        Returns:
            The parsed docstring.
        """
        return parse(self, docstring_parser, **options)

    def as_dict(self, full: bool = False, docstring_parser: Parser = Parser.google, **kwargs) -> dict[str, Any]:
        """Return this docstring's data as a dictionary.

        Arguments:
            full: Whether to return full info, or just base info.
            docstring_parser: The docstring docstring_parser to parse the docstring with.
            **kwargs: Additional serialization or docstring parsing options.

        Returns:
            A dictionary.
        """
        base: dict[str, Any] = {
            "value": self.value,
            "lineno": self.lineno,
            "endlineno": self.endlineno,
        }
        if full:
            base["parsed"] = self.parse(docstring_parser, **kwargs)
        return base


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

    def as_dict(self, **kwargs) -> dict[str, Any]:
        """Return this argument's data as a dictionary.

        Arguments:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        return {
            "name": self.name,
            "annotation": self.annotation,
            "kind": self.kind,
            "default": self.default,
        }


class Arguments:
    """This class is a container for arguments.

    It allows to get arguments using their position (index) or their name.
    """

    def __init__(self) -> None:
        """Initialize the arguments container."""
        self._arguments_list: list[Argument] = []
        self._arguments_dict: dict[str, Argument] = {}

    def __getitem__(self, name_or_index: int | str) -> Argument:
        if isinstance(name_or_index, int):
            return self._arguments_list[name_or_index]
        return self._arguments_dict[name_or_index]

    def __len__(self):
        return len(self._arguments_list)

    def __iter__(self):
        return iter(self._arguments_list)

    def add(self, argument: Argument) -> None:
        """Add an argument to the container.

        Arguments:
            argument: The function argument to add.

        Raises:
            ValueError: When an argument with the same name is already present.
        """
        if argument.name not in self._arguments_dict:
            self._arguments_dict[argument.name] = argument
            self._arguments_list.append(argument)
        else:
            raise ValueError(f"argument {argument.name} already present")


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

        # attach the docstring to this object
        if docstring:
            docstring.parent = self  # type: ignore

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

    @cached_property
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

    @cached_property
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

    @cached_property
    def path(self) -> str:
        """Return the dotted path / import path of this object.

        Returns:
            A dotted path.
        """
        if not self.parent:
            return self.name
        return ".".join((self.parent.path, self.name))

    def as_dict(self, full: bool = False, **kwargs) -> dict[str, Any]:
        """Return this object's data as a dictionary.

        Arguments:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options.

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
                    "filepath": self.filepath,
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
        base["members"] = [member.as_dict(full=full, **kwargs) for member in self.members.values()]

        return base


class Module(Object):
    """The class representing a Python module."""

    kind = Kind.MODULE

    def __init__(self, *args, filepath: Path, **kwargs) -> None:
        """Initialize the module.

        Arguments:
            *args: See [`griffe.dataclasses.Object`][].
            filepath: The module file path. It can be null for namespace packages.
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self._filepath: Path = filepath

    def __repr__(self) -> str:
        return f"<Module({self._filepath!r})>"

    @property
    def filepath(self) -> Path:
        """Get the file path of this module.

        Returns:
            The module's file path.
        """
        return self._filepath

    @cached_property
    def is_init_module(self) -> bool:
        """Tell if this module is an `__init__.py` module.

        Returns:
            True or False.
        """
        return self.filepath.name == "__init__.py"  # type: ignore

    @cached_property
    def is_package(self) -> bool:
        """Tell if this module is a package (top module).

        Returns:
            True or False.
        """
        return not bool(self.parent) and self.is_init_module

    @cached_property
    def is_subpackage(self) -> bool:
        """Tell if this module is a subpackage.

        Returns:
            True or False.
        """
        return bool(self.parent) and self.is_init_module

    @cached_property
    def is_namespace_package(self) -> bool:
        """Tell if this module is a namespace package (top folder, no `__init__.py`).

        Returns:
            True or False.
        """
        return not self.parent and self.filepath.is_dir()

    @cached_property
    def is_namespace_subpackage(self) -> bool:
        """Tell if this module is a namespace subpackage.

        Returns:
            True or False.
        """
        return (
            self.parent
            and self.filepath.is_dir()
            and self.parent.is_namespace_package  # type: ignore  # modules parents are always modules
            or self.parent.is_namespace_subpackage  # type: ignore  # modules parents are always modules
        )

    def as_dict(self, **kwargs) -> dict[str, Any]:  # type: ignore
        """Return this module's data as a dictionary.

        Arguments:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = super().as_dict(**kwargs)
        base["filepath"] = str(self.filepath) if self.filepath else None
        return base


class Class(Object):
    """The class representing a Python class."""

    kind = Kind.CLASS

    def __init__(
        self,
        *args,
        bases: list[str] | None = None,
        decorators: list[Decorator] | None = None,
        **kwargs,
    ) -> None:
        """Initialize the class.

        Arguments:
            *args: See [`griffe.dataclasses.Object`][].
            bases: The list of base classes, if any.
            decorators: The class decorators, if any.
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self.bases = bases or []
        self.decorators = decorators or []

    def as_dict(self, **kwargs) -> dict[str, Any]:  # type: ignore
        """Return this class' data as a dictionary.

        Arguments:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = super().as_dict(**kwargs)
        base["bases"] = self.bases
        base["decorators"] = [dec.as_dict(**kwargs) for dec in self.decorators]
        return base


class Function(Object):
    """The class representing a Python function."""

    kind = Kind.FUNCTION

    def __init__(
        self,
        *args,
        arguments: Arguments | None = None,
        returns: str | None = None,
        decorators: list[Decorator] | None = None,
        **kwargs,
    ) -> None:
        """Initialize the function.

        Arguments:
            *args: See [`griffe.dataclasses.Object`][].
            arguments: The function arguments.
            returns: The function return annotation.
            decorators: The function decorators, if any.
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self.arguments = arguments or Arguments()
        self.returns = returns
        self.decorators = decorators or []

    def as_dict(self, **kwargs) -> dict[str, Any]:  # type: ignore
        """Return this function's data as a dictionary.

        Arguments:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = super().as_dict(**kwargs)
        base["decorators"] = [dec.as_dict(**kwargs) for dec in self.decorators]
        base["arguments"] = [arg.as_dict(**kwargs) for arg in self.arguments]
        base["returns"] = self.returns
        return base


class Data(Object):
    """The class representing a Python module/class/instance attribute."""

    kind = Kind.DATA
