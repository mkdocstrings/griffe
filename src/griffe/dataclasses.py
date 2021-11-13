"""This module contains the data classes that represent Python objects.

The different objects are modules, classes, functions, and attribute
(variables like module/class/instance attributes).
"""

from __future__ import annotations

import enum
import inspect
from functools import cached_property
from pathlib import Path
from textwrap import dedent
from typing import Any

from griffe.collections import lines_collection
from griffe.docstrings.dataclasses import DocstringSection
from griffe.docstrings.parsers import Parser, parse  # noqa: WPS347


class ParameterKind(enum.Enum):
    """Enumeration of the different parameter kinds.

    Attributes:
        positional_only: Positional-only parameter.
        positional_or_keyword: Positional or keyword parameter.
        var_positional: Variadic positional parameter.
        keyword_only: Keyword-only parameter.
        var_keyword: Variadic keyword parameter.
    """

    positional_only: str = "positional-only"
    positional_or_keyword: str = "positional or keyword"
    var_positional: str = "variadic positional"
    keyword_only: str = "keyword-only"
    var_keyword: str = "variadic keyword"


class Decorator:
    """This class represents decorators.

    Attributes:
        lineno: The starting line number.
        endlineno: The ending line number.
    """

    def __init__(self, lineno: int | None, endlineno: int | None) -> None:
        """Initialize the decorator.

        Parameters:
            lineno: The starting line number.
            endlineno: The ending line number.
        """
        self.lineno: int | None = lineno
        self.endlineno: int | None = endlineno

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this decorator's data as a dictionary.

        Parameters:
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
        *,
        lineno: int | None,
        endlineno: int | None,
        parent: Module | Class | Function | Attribute | None = None,
        parser: Parser | None = None,
        parser_options: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the docstring.

        Parameters:
            value: The docstring value.
            lineno: The starting line number.
            endlineno: The ending line number.
            parent: The parent object on which this docstring is attached.
            parser: The docstring parser to use. By default, no parsing is done.
            parser_options: Additional docstring parsing options.
        """
        self.value: str = inspect.cleandoc(value)
        self.lineno: int | None = lineno
        self.endlineno: int | None = endlineno
        self.parent: Module | Class | Function | Attribute | None = parent
        self.parser: Parser | None = parser
        self.parser_options: dict[str, Any] = parser_options or {}

    def __bool__(self):
        return bool(self.value)

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
            The parsed docstring as a list of sections.
        """
        return self.parse()

    def parse(self, parser: Parser | None = None, **options: Any) -> list[DocstringSection]:
        """Parse the docstring into structured data.

        Parameters:
            parser: The docstring parser to use.
                In order: use the given parser, or the self parser, or no parser (return a single text section).
            **options: Additional docstring parsing options.

        Returns:
            The parsed docstring as a list of sections.
        """
        return parse(self, parser or self.parser, **(options or self.parser_options))

    def as_dict(self, full: bool = False, docstring_parser: Parser | None = None, **kwargs: Any) -> dict[str, Any]:
        """Return this docstring's data as a dictionary.

        Parameters:
            full: Whether to return full info, or just base info.
            docstring_parser: The docstring parser to parse the docstring with. By default, no parsing is done.
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


class Parameter:
    """This class represent a function parameter.

    Attributes:
        name: The parameter name.
        annotation: The parameter annotation, if any.
        kind: The parameter kind.
        default: The parameter default, if any.
    """

    def __init__(
        self,
        name: str,
        *,
        annotation: str | None = None,
        kind: ParameterKind | None = None,
        default: str | None = None,
    ) -> None:
        """Initialize the parameter.

        Parameters:
            name: The parameter name.
            annotation: The parameter annotation, if any.
            kind: The parameter kind.
            default: The parameter default, if any.
        """
        self.name: str = name
        self.annotation: str | None = annotation
        self.kind: ParameterKind | None = kind
        self.default: str | None = default

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this parameter's data as a dictionary.

        Parameters:
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


class Parameters:
    """This class is a container for parameters.

    It allows to get parameters using their position (index) or their name.
    """

    def __init__(self, *parameters: Parameter) -> None:
        """Initialize the parameters container.

        Parameters:
            *parameters: The initial parameters to add to the container.
        """
        self._parameters_list: list[Parameter] = []
        self._parameters_dict: dict[str, Parameter] = {}
        for parameter in parameters:
            self.add(parameter)

    def __getitem__(self, name_or_index: int | str) -> Parameter:
        if isinstance(name_or_index, int):
            return self._parameters_list[name_or_index]
        return self._parameters_dict[name_or_index]

    def __len__(self):
        return len(self._parameters_list)

    def __iter__(self):
        return iter(self._parameters_list)

    def add(self, parameter: Parameter) -> None:
        """Add a parameter to the container.

        Parameters:
            parameter: The function parameter to add.

        Raises:
            ValueError: When a parameter with the same name is already present.
        """
        if parameter.name not in self._parameters_dict:
            self._parameters_dict[parameter.name] = parameter
            self._parameters_list.append(parameter)
        else:
            raise ValueError(f"parameter {parameter.name} already present")


class Kind(enum.Enum):
    """Enumeration of the different objects kinds.

    Attributes:
        MODULE: The module kind.
        CLASS: The class kind.
        FUNCTION: The function kind.
        ATTRIBUTE: The attribute kind.
    """

    MODULE: str = "module"
    CLASS: str = "class"
    FUNCTION: str = "function"
    ATTRIBUTE: str = "attribute"


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
        *,
        lineno: int | None = None,
        endlineno: int | None = None,
        docstring: Docstring | None = None,
        parent: Module | Class | None = None,
    ) -> None:
        """Initialize the object.

        Parameters:
            name: The object name, as declared in the code.
            lineno: The object starting line, or None for modules. Lines start at 1.
            endlineno: The object ending line (inclusive), or None for modules.
            docstring: The object docstring.
            parent: The object parent.
        """
        self.name: str = name
        self.lineno: int | None = lineno
        self.endlineno: int | None = endlineno
        self.docstring: Docstring | None = docstring
        self.parent: Module | Class | None = parent
        self.members: dict[str, Module | Class | Function | Attribute] = {}
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

    def __bool__(self):
        return bool(self.docstring) or any(self.members.values())

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
        if self.parent is not None:
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
    def filepath(self) -> Path:
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
    def relative_filepath(self) -> Path:
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

    @cached_property
    def source(self) -> str:
        """Return the source code of this object.

        Returns:
            The source code.
        """
        return dedent("\n".join(lines_collection[self.filepath][self.lineno - 1 : self.endlineno]))

    @property
    def modules(self) -> dict[str, Module]:
        return {name: member for name, member in self.members.items() if member.kind is Kind.MODULE}

    @property
    def classes(self) -> dict[str, Class]:
        return {name: member for name, member in self.members.items() if member.kind is Kind.CLASS}

    @property
    def functions(self) -> dict[str, Function]:
        return {name: member for name, member in self.members.items() if member.kind is Kind.FUNCTION}

    @property
    def attributes(self) -> dict[str, Attribute]:
        return {name: member for name, member in self.members.items() if member.kind is Kind.ATTRIBUTE}

    def as_dict(self, full: bool = False, **kwargs: Any) -> dict[str, Any]:
        """Return this object's data as a dictionary.

        Parameters:
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

    def __init__(self, *args: Any, filepath: Path, **kwargs: Any) -> None:
        """Initialize the module.

        Parameters:
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

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore
        """Return this module's data as a dictionary.

        Parameters:
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
        *args: Any,
        bases: list[str] | None = None,
        decorators: list[Decorator] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the class.

        Parameters:
            *args: See [`griffe.dataclasses.Object`][].
            bases: The list of base classes, if any.
            decorators: The class decorators, if any.
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self.bases = bases or []
        self.decorators = decorators or []

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore
        """Return this class' data as a dictionary.

        Parameters:
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
        *args: Any,
        parameters: Parameters | None = None,
        returns: str | None = None,
        decorators: list[Decorator] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the function.

        Parameters:
            *args: See [`griffe.dataclasses.Object`][].
            parameters: The function parameters.
            returns: The function return annotation.
            decorators: The function decorators, if any.
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self.parameters: Parameters = parameters or Parameters()
        self.returns = returns
        self.decorators: list[Decorator] = decorators or []

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore
        """Return this function's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = super().as_dict(**kwargs)
        base["decorators"] = [dec.as_dict(**kwargs) for dec in self.decorators]
        base["parameters"] = [param.as_dict(**kwargs) for param in self.parameters]
        base["returns"] = self.returns
        return base


class Attribute(Object):
    """The class representing a Python module/class/instance attribute."""

    kind = Kind.ATTRIBUTE

    def __init__(
        self,
        *args: Any,
        value: str | None = None,
        annotation: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the function.

        Parameters:
            *args: See [`griffe.dataclasses.Object`][].
            value: The attribute value, if any.
            annotation: The attribute annotation, if any.
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self.value: str | None = value
        self.annotation: str | None = annotation

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore
        """Return this function's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = super().as_dict(**kwargs)
        if self.value is not None:
            base["value"] = self.value
        if self.annotation is not None:
            base["annotation"] = self.annotation
        return base
