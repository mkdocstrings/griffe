"""This module contains the data classes that represent Python objects.

The different objects are modules, classes, functions, and attribute
(variables like module/class/instance attributes).
"""

from __future__ import annotations

import enum
import inspect
import sys
from collections import defaultdict
from contextlib import suppress
from pathlib import Path
from textwrap import dedent
from typing import Any, Callable, Union, cast

from griffe.collections import LinesCollection, ModulesCollection
from griffe.docstrings.dataclasses import DocstringSection
from griffe.docstrings.parsers import Parser, parse  # noqa: WPS347
from griffe.exceptions import AliasResolutionError, BuiltinModuleError, CyclicAliasError, NameResolutionError
from griffe.expressions import Expression, Name
from griffe.mixins import GetMembersMixin, ObjectAliasMixin, SerializationMixin, SetMembersMixin

# TODO: remove once Python 3.7 support is dropped
if sys.version_info < (3, 8):
    from cached_property import cached_property
else:
    from functools import cached_property  # noqa: WPS440


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

    def __init__(self, value: str, *, lineno: int | None, endlineno: int | None) -> None:
        """Initialize the decorator.

        Parameters:
            value: The decorator code.
            lineno: The starting line number.
            endlineno: The ending line number.
        """
        self.value: str = value
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
            "value": self.value,
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
        lineno: int | None = None,
        endlineno: int | None = None,
        parent: Object | None = None,
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
        self.value: str = inspect.cleandoc(value.rstrip())
        self.lineno: int | None = lineno
        self.endlineno: int | None = endlineno
        self.parent: Object | None = parent
        self.parser: Parser | None = parser
        self.parser_options: dict[str, Any] = parser_options or {}

    def __bool__(self) -> bool:
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
        annotation: str | Name | Expression | None = None,
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
        self.annotation: str | Name | Expression | None = annotation
        self.kind: ParameterKind | None = kind
        self.default: str | None = default

    def __str__(self) -> str:
        param = f"{self.name}: {self.annotation} = {self.default}"
        if self.kind:
            return f"[{self.kind.value}] {param}"
        return param

    @property
    def required(self) -> bool:
        """Tell if this parameter is required.

        Returns:
            True or False.
        """
        return self.default is None

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
        return self._parameters_dict[name_or_index.lstrip("*")]

    def __len__(self):
        return len(self._parameters_list)

    def __iter__(self):
        return iter(self._parameters_list)

    def __contains__(self, param_name: str):
        return param_name.lstrip("*") in self._parameters_dict

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
    ALIAS: str = "alias"


class Object(GetMembersMixin, SetMembersMixin, ObjectAliasMixin, SerializationMixin):  # noqa: WPS215
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
    is_alias: bool = False
    is_collection: bool = False

    def __init__(
        self,
        name: str,
        *,
        lineno: int | None = None,
        endlineno: int | None = None,
        runtime: bool = True,
        docstring: Docstring | None = None,
        parent: Module | Class | None = None,
        lines_collection: LinesCollection | None = None,
        modules_collection: ModulesCollection | None = None,
    ) -> None:
        """Initialize the object.

        Parameters:
            name: The object name, as declared in the code.
            lineno: The object starting line, or None for modules. Lines start at 1.
            endlineno: The object ending line (inclusive), or None for modules.
            runtime: Whether this object is present at runtime or not.
            docstring: The object docstring.
            parent: The object parent.
            lines_collection: A collection of source code lines.
            modules_collection: A collection of modules.
        """
        self.name: str = name
        self.lineno: int | None = lineno
        self.endlineno: int | None = endlineno
        self.docstring: Docstring | None = docstring
        self.parent: Module | Class | None = parent
        self.members: dict[str, Object | Alias] = {}
        self.labels: set[str] = set()
        self.imports: dict[str, str] = {}
        self.exports: set[str] | list[str | Name] | None = None
        self.aliases: dict[str, Alias] = {}
        self.runtime: bool = runtime
        self._lines_collection: LinesCollection | None = lines_collection
        self._modules_collection: ModulesCollection | None = modules_collection

        # attach the docstring to this object
        if docstring:
            docstring.parent = self

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.name!r}, {self.lineno!r}, {self.endlineno!r})>"

    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return len(self.members) + sum(len(member) for member in self.members.values())

    @property
    def has_docstring(self) -> bool:
        """Tell if this object has a non-empty docstring."""
        return bool(self.docstring)  # noqa: DAR201

    @property
    def has_docstrings(self) -> bool:
        """Tell if this object or any of its members has a non-empty docstring."""
        if self.has_docstring:  # noqa: DAR201
            return True
        for member in self.members.values():
            if member.has_docstrings:  # type: ignore[union-attr]
                return True
        return False

    def member_is_exported(self, member: Object | Alias, explicitely: bool = True) -> bool:
        """Tell if a member of this object is "exported".

        By exported, we mean that the object is included in the `__all__` attribute
        of its parent module or class. When `_all__` is not defined,
        we consider the member to be *implicitely* exported,
        unless it's a module and it was not imported,
        and unless it's not defined at runtime.

        Parameters:
            member: The member to verify.
            explicitely: Whether to only return True when `__all__` is defined.

        Returns:
            True or False.
        """
        if not member.runtime:
            return False
        if self.exports is None:
            return not explicitely and (member.is_alias or not member.is_module or member.name in self.imports)
        return member.name in self.exports

    def is_kind(self, kind: str | Kind | set[str | Kind]) -> bool:
        """Tell if this object is of the given kind.

        Parameters:
            kind: An instance or set of kinds (strings or enumerations).

        Raises:
            ValueError: When an empty set is given as argument.

        Returns:
            True or False.
        """
        if isinstance(kind, set):
            if not kind:
                raise ValueError("kind must not be an empty set")
            return self.kind in (knd if isinstance(knd, Kind) else Kind(knd) for knd in kind)  # noqa: WPS509,WPS510
        if isinstance(kind, str):
            kind = Kind(kind)
        return self.kind is kind

    @property
    def is_module(self) -> bool:
        """Tell if this object is a module."""
        return self.kind is Kind.MODULE  # noqa: DAR201

    @property
    def is_class(self) -> bool:
        """Tell if this object is a class."""
        return self.kind is Kind.CLASS  # noqa: DAR201

    @property
    def is_function(self) -> bool:
        """Tell if this object is a function."""
        return self.kind is Kind.FUNCTION  # noqa: DAR201

    @property
    def is_attribute(self) -> bool:
        """Tell if this object is an attribute."""
        return self.kind is Kind.ATTRIBUTE  # noqa: DAR201

    def has_labels(self, labels: set[str]) -> bool:
        """Tell if this object has all the given labels.

        Parameters:
            labels: A set of labels.

        Returns:
            True or False.
        """
        return all(label in self.labels for label in labels)

    def filter_members(self, *predicates: Callable[[Object | Alias], bool]) -> dict[str, Object | Alias]:
        """Filter and return members based on predicates.

        Parameters:
            *predicates: A list of predicates, i.e. callables accepting a member as argument and returning a boolean.

        Returns:
            A dictionary of members.
        """
        if not predicates:
            return self.members
        members: dict[str, Object | Alias] = {}
        for name, member in self.members.items():
            if all(predicate(member) for predicate in predicates):
                members[name] = member
        return members

    @property
    def modules(self) -> dict[str, Module]:
        """Return the module members.

        Returns:
            A dictionary of modules.
        """
        return {name: member for name, member in self.members.items() if member.kind is Kind.MODULE}  # type: ignore[misc]

    @property
    def classes(self) -> dict[str, Class]:
        """Return the class members.

        Returns:
            A dictionary of classes.
        """
        return {name: member for name, member in self.members.items() if member.kind is Kind.CLASS}  # type: ignore[misc]

    @property
    def functions(self) -> dict[str, Function]:
        """Return the function members.

        Returns:
            A dictionary of functions.
        """
        return {name: member for name, member in self.members.items() if member.kind is Kind.FUNCTION}  # type: ignore[misc]

    @property
    def attributes(self) -> dict[str, Attribute]:
        """Return the attribute members.

        Returns:
            A dictionary of attributes.
        """
        return {name: member for name, member in self.members.items() if member.kind is Kind.ATTRIBUTE}  # type: ignore[misc]

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
            module = module.parent  # type: ignore[assignment]  # always a module
        return module

    @cached_property
    def filepath(self) -> Path | list[Path]:
        """Return the file path where this object was defined.

        Returns:
            A file path or a list of directories.
        """
        return self.module.filepath

    @cached_property  # noqa: WPS231
    def relative_filepath(self) -> Path:  # noqa: WPS231
        """Return the file path where this object was defined, relative to the top module path.

        Raises:
            ValueError: When the relative path could not be computed.

        Returns:
            A file path.
        """
        package_path = self.package.filepath
        if isinstance(self.module.filepath, list):
            if isinstance(package_path, list):
                for pkg_path in package_path:
                    for self_path in self.module.filepath:
                        with suppress(ValueError):
                            return self_path.relative_to(pkg_path.parent)
            else:
                for self_path in self.module.filepath:  # noqa: WPS440
                    with suppress(ValueError):
                        return self_path.relative_to(package_path.parent.parent)
            raise ValueError
        if isinstance(package_path, list):
            for pkg_path in package_path:  # noqa: WPS440
                with suppress(ValueError):
                    return self.module.filepath.relative_to(pkg_path.parent)
            raise ValueError
        return self.module.filepath.relative_to(package_path.parent.parent)

    @cached_property
    def path(self) -> str:
        """Return the dotted path of this object.

        On regular objects (not aliases), the path is the canonical path.

        Returns:
            A dotted path.
        """
        return self.canonical_path

    @cached_property
    def canonical_path(self) -> str:
        """Return the full dotted path of this object.

        The canonical path is the path where the object was defined (not imported).

        Returns:
            A dotted path.
        """
        if self.parent is None:
            return self.name
        return ".".join((self.parent.path, self.name))

    @cached_property
    def modules_collection(self) -> ModulesCollection:
        """Return the modules collection attached to this object or its parents.

        Raises:
            ValueError: When no modules collection can be found in the object or its parents.

        Returns:
            A modules collection.
        """
        if self._modules_collection is not None:
            return self._modules_collection
        if self.parent is None:
            raise ValueError("no modules collection in this object or its parents")
        return self.parent.modules_collection

    @cached_property
    def lines_collection(self) -> LinesCollection:
        """Return the lines collection attached to this object or its parents.

        Raises:
            ValueError: When no modules collection can be found in the object or its parents.

        Returns:
            A lines collection.
        """
        if self._lines_collection is not None:
            return self._lines_collection
        if self.parent is None:
            raise ValueError("no lines collection in this object or its parents")
        return self.parent.lines_collection

    @cached_property
    def lines(self) -> list[str]:
        """Return the lines containing the source of this object.

        Returns:
            A list of lines.
        """
        try:
            filepath = self.filepath
        except BuiltinModuleError:
            return []
        if isinstance(filepath, list):
            return []

        # TODO: remove once Python 3.7 support is dropped
        if self.lineno and self.endlineno is None and sys.version_info < (3, 8):
            self.endlineno = self._endlineno

        try:
            lines = self.lines_collection[filepath]
        except KeyError:
            return []
        if self.lineno is None or self.endlineno is None:
            return lines
        return lines[self.lineno - 1 : self.endlineno]

    @cached_property
    def source(self) -> str:
        """Return the source code of this object.

        Returns:
            The source code.
        """
        return dedent("\n".join(self.lines))

    def resolve(self, name: str) -> str:
        """Resolve a name within this object's and parents' scope.

        Parameters:
            name: The name to resolve.

        Raises:
            NameResolutionError: When the name could not be resolved.

        Returns:
            The resolved name.
        """
        if name in self.members:
            if self.members[name].is_alias:
                return self.members[name].target_path  # type: ignore[union-attr]
            return self.members[name].path
        if name in self.imports:
            return self.imports[name]
        if self.parent is None:
            # could be a built-in
            raise NameResolutionError(f"{name} could not be resolved in the scope of {self.path}")
        if name == self.parent.name and not self.parent.is_module:
            return self.parent.path
        return self.parent.resolve(name)

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

    # TODO: remove once Python 3.7 support is dropped
    @property
    def _endlineno(self) -> int | None:
        if self.kind is Kind.MODULE:
            if isinstance(self.filepath, list):
                return 0
            return len(self.lines_collection[self.filepath])
        if isinstance(self.filepath, list):
            return None
        tokens, tokens_by_line = self.lines_collection.tokens(self.filepath)
        first_token_index = tokens_by_line[self.lineno][0]
        blockfinder = inspect.BlockFinder()
        with suppress(inspect.EndOfBlock, IndentationError):
            for token in tokens[first_token_index:]:
                blockfinder.tokeneater(*token)
        return blockfinder.last


class Alias(ObjectAliasMixin):  # noqa: WPS338
    """This class represents an alias, or indirection, to an object declared in another module.

    Aliases represent objects that are in the scope of a module or class,
    but were imported from another module.

    They behave almost exactly like regular objects, to a few exceptions:

    - line numbers are those of the alias, not the target
    - the path is the alias path, not the canonical one
    - the name can be different from the target's
    - if the target can be resolved, the kind is the target's kind
    - if the target cannot be resolved, the kind becomes [Kind.ALIAS][griffe.dataclasses.Kind]

    Attributes:
        name: The alias name.
        lineno: The alias starting line number.
        endlineno: The alias ending line number.
        parent: The alias parent.
        target_path: The alias target path.
    """

    is_alias: bool = True
    is_collection: bool = False

    def __init__(
        self,
        name: str,
        target: str | Object | Alias,
        *,
        lineno: int | None = None,
        endlineno: int | None = None,
        runtime: bool = True,
        parent: Module | Class | None = None,
    ) -> None:
        """Initialize the alias.

        Parameters:
            name: The alias name.
            target: If it's a string, the target resolution is delayed until accessing the target property.
                If it's an object, or even another alias, the target is immediately set.
            lineno: The alias starting line number.
            endlineno: The alias ending line number.
            runtime: Whether this alias is present at runtime or not.
            parent: The alias parent.
        """
        self.name: str = name
        self.alias_lineno: int | None = lineno
        self.alias_endlineno: int | None = endlineno
        self.runtime: bool = runtime
        self._parent: Module | Class | None = parent
        self._passed_through: bool = False
        if isinstance(target, str):
            self._target: Object | Alias | None = None
            self.target_path: str = target
        else:
            self._target = target
            self.target_path = target.path
            self._update_target_aliases()

    def __repr__(self) -> str:
        return f"<Alias({self.name!r}, {self.target_path!r})>"

    def __getitem__(self, key):
        # not handled by __getattr__
        return self.target[key]

    def __setitem__(self, key, value):
        # not handled by __getattr__
        self.target[key] = value

    def __len__(self) -> int:
        return 1

    # SPECIAL PROXIES -------------------------------

    @property
    def kind(self) -> Kind:
        """Return the target's kind, or Kind.ALIAS if the target cannot be resolved.

        Returns:
            A kind.
        """
        # custom behavior to avoid raising exceptions
        try:
            return self.target.kind
        except (AliasResolutionError, CyclicAliasError):
            return Kind.ALIAS

    @property
    def lineno(self) -> int | None:
        """Return the target lineno or the alias lineno.

        Returns:
            The target lineno or the alias lineno.
        """
        if self.resolved:
            return self.target.lineno
        return self.alias_lineno

    @property
    def endlineno(self) -> int | None:
        """Return the target endlineno or the alias endlineno.

        Returns:
            The target endlineno or the alias endlineno.
        """
        if self.resolved:
            return self.target.endlineno
        return self.alias_endlineno

    @property
    def has_docstring(self) -> bool:
        """Tell if this alias' target has a non-empty docstring."""
        return self.resolved and self.target.has_docstring  # noqa: DAR201

    @property
    def has_docstrings(self) -> bool:
        """Tell if this alias' target or any of its members has a non-empty docstring."""
        return self.resolved and self.target.has_docstrings  # noqa: DAR201

    @property
    def parent(self) -> Module | Class | None:
        """Return the parent of this alias.

        Returns:
            The parent.
        """
        return self._parent

    @parent.setter
    def parent(self, value: Module | Class) -> None:
        self._parent = value
        self._update_target_aliases()

    @cached_property
    def path(self) -> str:
        """Return the dotted path / import path of this object.

        Returns:
            A dotted path.
        """
        return ".".join((self.parent.path, self.name))  # type: ignore[union-attr]  # we assume there's always a parent

    @cached_property
    def modules_collection(self) -> ModulesCollection:
        """Return the modules collection attached to the alias parents.

        Returns:
            A modules collection.
        """
        # no need to forward to the target
        return self.parent.modules_collection  # type: ignore[union-attr]  # we assume there's always a parent

    # GENERIC OBJECT PROXIES --------------------------------

    @property
    def docstring(self):  # noqa: D102
        return self.target.docstring

    @property
    def members(self):  # noqa: D102
        return self.target.members

    @property
    def labels(self):  # noqa: D102
        return self.target.labels

    @property
    def imports(self):  # noqa: D102
        return self.target.imports

    @property
    def exports(self):  # noqa: D102
        return self.target.exports

    @property
    def aliases(self):  # noqa: D102
        return self.target.aliases

    def member_is_exported(self, member: Object | Alias, explicitely: bool = True) -> bool:  # noqa: D102
        return self.target.member_is_exported(member, explicitely)

    def is_kind(self, kind: str | Kind | set[str | Kind]) -> bool:  # noqa: D102
        return self.target.is_kind(kind)

    @property
    def is_module(self):  # noqa: D102
        return self.target.is_module

    @property
    def is_class(self):  # noqa: D102
        return self.target.is_class

    @property
    def is_function(self):  # noqa: D102
        return self.target.is_function

    @property
    def is_attribute(self):  # noqa: D102
        return self.target.is_attribute

    def has_labels(self, labels: set[str]) -> bool:  # noqa: D102
        return self.target.has_labels(labels)

    def filter_members(self, *predicates: Callable[[Object | Alias], bool]) -> dict[str, Object | Alias]:  # noqa: D102
        return self.target.filter_members(*predicates)

    @property
    def modules(self):  # noqa: D102
        return self.target.modules

    @property
    def classes(self):  # noqa: D102
        return self.target.classes

    @property
    def functions(self):  # noqa: D102
        return self.target.functions

    @property
    def attributes(self):  # noqa: D102
        return self.target.attributes

    @property
    def module(self):  # noqa: D102
        return self.target.module

    @property
    def package(self):  # noqa: D102
        return self.target.package

    @property
    def filepath(self):  # noqa: D102
        return self.target.filepath

    @property
    def relative_filepath(self):  # noqa: D102
        return self.target.relative_filepath

    @property
    def canonical_path(self):  # noqa: D102
        return self.target.canonical_path

    @property
    def lines_collection(self):  # noqa: D102
        return self.target.lines_collection

    @property
    def lines(self):  # noqa: D102
        return self.target.lines

    @property
    def source(self):  # noqa: D102
        return self.target.source

    def resolve(self, name: str) -> str:  # noqa: D102
        return self.target.resolve(name)

    # SPECIFIC MODULE/CLASS/FUNCTION/ATTRIBUTE PROXIES ---------------

    @property
    def _filepath(self) -> Path | list[Path] | None:  # noqa: D102
        return cast(Module, self.target)._filepath  # noqa: WPS437

    @property
    def bases(self) -> list[Name | Expression | str]:  # noqa: D102
        return cast(Class, self.target).bases

    @property
    def decorators(self) -> list[Decorator]:  # noqa: D102
        return cast(Union[Class, Function], self.target).decorators

    @property
    def overloads(self) -> dict[str, list[Function]] | list[Function] | None:  # noqa: D102
        return cast(Union[Module, Class, Function], self.target).overloads

    @overloads.setter
    def overloads(self, overloads: list[Function] | None) -> None:
        cast(Union[Module, Class, Function], self.target).overloads = overloads

    @property
    def parameters(self) -> Parameters:  # noqa: D102
        return cast(Function, self.target).parameters

    @property
    def returns(self) -> str | Name | Expression | None:  # noqa: D102
        return cast(Function, self.target).returns

    @returns.setter
    def returns(self, returns: str | Name | Expression | None) -> None:
        cast(Function, self.target).returns = returns

    @property
    def setter(self) -> Function | None:  # noqa: D102
        return cast(Function, self.target).setter

    @property
    def deleter(self) -> Function | None:  # noqa: D102
        return cast(Function, self.target).deleter

    @property
    def value(self) -> str | None:  # noqa: D102
        return cast(Attribute, self.target).value

    @property
    def annotation(self) -> str | Name | Expression | None:  # noqa: D102
        return cast(Attribute, self.target).annotation

    @annotation.setter
    def annotation(self, annotation: str | Name | Expression | None) -> None:
        cast(Attribute, self.target).annotation = annotation

    # SPECIFIC ALIAS METHOD AND PROPERTIES -----------------

    @property
    def target(self) -> Object | Alias:
        """Resolve and return the target, if possible.

        Upon accessing this property, if the target is not already resolved,
        a lookup is done using the modules collection to find the target.

        Returns:
            The resolved target.
        """
        if not self.resolved:
            self.resolve_target()
        return self._target  # type: ignore[return-value]  # cannot return None, exception is raised

    @target.setter
    def target(self, value: Object | Alias) -> None:
        if value is self or value.path == self.path:
            raise CyclicAliasError([self.target_path])
        self._target = value
        self.target_path = value.path
        if self.parent is not None:
            self._target.aliases[self.path] = self

    def resolve_target(self) -> None:  # noqa: WPS231,WPS238
        """Resolve the target.

        Raises:
            AliasResolutionError: When the target cannot be resolved.
                It happens when the target does not exist,
                or could not be loaded (unhandled dynamic object?),
                or when the target is from a module that was not loaded
                and added to the collection.
            CyclicAliasError: When the resolved target is the alias itself.
        """
        if self._passed_through:
            raise CyclicAliasError([self.target_path])
        self._passed_through = True
        try:  # noqa: WPS501
            self._resolve_target()
        finally:
            self._passed_through = False

    def _resolve_target(self) -> None:
        try:
            resolved = self.modules_collection[self.target_path]
        except KeyError as error:
            raise AliasResolutionError(self.target_path) from error
        if resolved is self:
            raise CyclicAliasError([self.target_path])
        if resolved.is_alias and not resolved.resolved:
            try:
                resolved.resolve_target()
            except CyclicAliasError as error:  # noqa: WPS440
                raise CyclicAliasError([self.target_path] + error.chain)
        self._target = resolved
        if self.parent is not None:
            self._target.aliases[self.path] = self  # type: ignore[union-attr]  # we just set the target

    def _update_target_aliases(self) -> None:
        with suppress(AttributeError, AliasResolutionError, CyclicAliasError):
            self._target.aliases[self.path] = self  # type: ignore[union-attr]

    @property
    def resolved(self) -> bool:
        """Tell whether this alias' target is resolved.

        Returns:
            True or False.
        """
        return self._target is not None  # type: ignore[union-attr]

    @cached_property
    def wildcard(self) -> str | None:
        """Return the module on which the wildcard import is performed (if any).

        Returns:
            The wildcard imported module, or None.
        """
        if self.name.endswith("/*"):
            return self.target_path
        return None

    def as_dict(self, full: bool = False, **kwargs: Any) -> dict[str, Any]:
        """Return this alias' data as a dictionary.

        Parameters:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = {
            "kind": Kind.ALIAS,
            "name": self.name,
            "target_path": self.target_path,
        }

        if full:
            base["path"] = self.path

        if self.lineno:
            base["lineno"] = self.lineno
        if self.endlineno:
            base["endlineno"] = self.endlineno

        return base


class Module(Object):
    """The class representing a Python module."""

    kind = Kind.MODULE

    def __init__(self, *args: Any, filepath: Path | list[Path] | None = None, **kwargs: Any) -> None:
        """Initialize the module.

        Parameters:
            *args: See [`griffe.dataclasses.Object`][].
            filepath: The module file path (directory for namespace [sub]packages, none for builtin modules).
            **kwargs: See [`griffe.dataclasses.Object`][].
        """
        super().__init__(*args, **kwargs)
        self._filepath: Path | list[Path] | None = filepath
        self.overloads: dict[str, list[Function]] = defaultdict(list)

    def __repr__(self) -> str:
        try:
            return f"<Module({self.filepath!r})>"
        except BuiltinModuleError:
            return f"<Module({self.name!r})>"

    @property
    def filepath(self) -> Path | list[Path]:
        """Get the file path of this module.

        Raises:
            BuiltinModuleError: When the instance filepath is None.

        Returns:
            The module's file path.
        """
        if self._filepath is None:
            raise BuiltinModuleError(self.name)
        return self._filepath

    @cached_property
    def is_init_module(self) -> bool:
        """Tell if this module is an `__init__.py` module.

        Returns:
            True or False.
        """
        if isinstance(self.filepath, list):
            return False
        try:
            return self.filepath.name.split(".", 1)[0] == "__init__"
        except BuiltinModuleError:
            return False

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
        try:
            return self.parent is None and isinstance(self.filepath, list)
        except BuiltinModuleError:
            return False

    @cached_property
    def is_namespace_subpackage(self) -> bool:
        """Tell if this module is a namespace subpackage.

        Returns:
            True or False.
        """
        try:
            return (
                self.parent is not None
                and isinstance(self.filepath, list)
                and (
                    cast(Module, self.parent).is_namespace_package or cast(Module, self.parent).is_namespace_subpackage
                )
            )
        except BuiltinModuleError:
            return False

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore[override]
        """Return this module's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = super().as_dict(**kwargs)
        base["filepath"] = str(self._filepath) if self._filepath else None
        return base


class Class(Object):
    """The class representing a Python class."""

    kind = Kind.CLASS

    def __init__(
        self,
        *args: Any,
        bases: list[Name | Expression | str] | None = None,
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
        self.bases: list[Name | Expression | str] = bases or []
        self.decorators: list[Decorator] = decorators or []
        self.overloads: dict[str, list[Function]] = defaultdict(list)

    @property
    def parameters(self) -> Parameters:
        """Return the parameters of this class' `__init__` method, if any.

        Returns:
            The parameters containter.
        """
        try:
            return self.members["__init__"].parameters  # type: ignore[union-attr]
        except KeyError:
            if "dataclass" in self.labels:
                return Parameters(
                    *[
                        Parameter(attr.name, annotation=attr.annotation, default=attr.value)
                        for attr in self.attributes.values()
                    ]
                )
            return Parameters()

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore[override]
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
        returns: str | Name | Expression | None = None,
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
        self.returns: str | Name | Expression | None = returns
        self.decorators: list[Decorator] = decorators or []
        self.setter: Function | None = None
        self.deleter: Function | None = None
        self.overloads: list[Function] | None = None

    @property
    def annotation(self) -> str | Name | Expression | None:
        """Return the return annotation.

        Returns:
            The function return annotation.
        """
        return self.returns

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore[override]
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
        annotation: str | Name | Expression | None = None,
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
        self.annotation: str | Name | Expression | None = annotation

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore[override]
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
