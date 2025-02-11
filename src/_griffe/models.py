# This module contains our models definitions,
# to represent Python objects (and other aspects of Python APIs)... in Python.

from __future__ import annotations

import inspect
from collections import defaultdict
from contextlib import suppress
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Callable, Union, cast

from _griffe.c3linear import c3linear_merge
from _griffe.docstrings.parsers import DocstringStyle, parse
from _griffe.enumerations import Kind, ParameterKind, Parser
from _griffe.exceptions import AliasResolutionError, BuiltinModuleError, CyclicAliasError, NameResolutionError
from _griffe.expressions import ExprCall, ExprName
from _griffe.logger import logger
from _griffe.mixins import ObjectAliasMixin

if TYPE_CHECKING:
    from collections.abc import Sequence

    from _griffe.collections import LinesCollection, ModulesCollection
    from _griffe.docstrings.models import DocstringSection
    from _griffe.expressions import Expr

from functools import cached_property


class Decorator:
    """This class represents decorators."""

    def __init__(self, value: str | Expr, *, lineno: int | None, endlineno: int | None) -> None:
        """Initialize the decorator.

        Parameters:
            value: The decorator code.
            lineno: The starting line number.
            endlineno: The ending line number.
        """
        self.value: str | Expr = value
        """The decorator value (as a Griffe expression or string)."""
        self.lineno: int | None = lineno
        """The starting line number of the decorator."""
        self.endlineno: int | None = endlineno
        """The ending line number of the decorator."""

    @property
    def callable_path(self) -> str:
        """The path of the callable used as decorator."""
        value = self.value.function if isinstance(self.value, ExprCall) else self.value
        return value if isinstance(value, str) else value.canonical_path

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
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
    """This class represents docstrings."""

    def __init__(
        self,
        value: str,
        *,
        lineno: int | None = None,
        endlineno: int | None = None,
        parent: Object | None = None,
        parser: DocstringStyle | Parser | None = None,
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
        """The original value of the docstring, cleaned by `inspect.cleandoc`.

        See also: [`source`][griffe.Docstring.source].
        """

        self.lineno: int | None = lineno
        """The starting line number of the docstring.

        See also: [`endlineno`][griffe.Docstring.endlineno]."""

        self.endlineno: int | None = endlineno
        """The ending line number of the docstring.

        See also: [`lineno`][griffe.Docstring.lineno]."""

        self.parent: Object | None = parent
        """The object this docstring is attached to."""

        self.parser: DocstringStyle | Parser | None = parser
        """The selected docstring parser.

        See also: [`parser_options`][griffe.Docstring.parser_options],
        [`parse`][griffe.Docstring.parse].
        """

        self.parser_options: dict[str, Any] = parser_options or {}
        """The configured parsing options.

        See also: [`parser`][griffe.Docstring.parser],
        [`parse`][griffe.Docstring.parse].
        """

    @property
    def lines(self) -> list[str]:
        """The lines of the docstring.

        See also: [`source`][griffe.Docstring.source].
        """
        return self.value.split("\n")

    @property
    def source(self) -> str:
        """The original, uncleaned value of the docstring as written in the source.

        See also: [`value`][griffe.Docstring.value].
        """
        if self.parent is None:
            raise ValueError("Cannot get original docstring without parent object")
        if isinstance(self.parent.filepath, list):
            raise ValueError("Cannot get original docstring for namespace package")  # noqa: TRY004
        if self.lineno is None or self.endlineno is None:
            raise ValueError("Cannot get original docstring without line numbers")
        return "\n".join(self.parent.lines_collection[self.parent.filepath][self.lineno - 1 : self.endlineno])

    @cached_property
    def parsed(self) -> list[DocstringSection]:
        """The docstring sections, parsed into structured data."""
        return self.parse()

    def parse(
        self,
        parser: DocstringStyle | Parser | None = None,
        **options: Any,
    ) -> list[DocstringSection]:
        """Parse the docstring into structured data.

        See also: [`parser`][griffe.Docstring.parser],
        [`parser_options`][griffe.Docstring.parser_options].

        Parameters:
            parser: The docstring parser to use.
                In order: use the given parser, or the self parser, or no parser (return a single text section).
            **options: Additional docstring parsing options.

        Returns:
            The parsed docstring as a list of sections.
        """
        return parse(self, parser or self.parser, **(options or self.parser_options))

    def as_dict(
        self,
        *,
        full: bool = False,
        **kwargs: Any,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Return this docstring's data as a dictionary.

        Parameters:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base: dict[str, Any] = {
            "value": self.value,
            "lineno": self.lineno,
            "endlineno": self.endlineno,
        }
        if full:
            base["parsed"] = self.parsed
        return base


class Parameter:
    """This class represent a function parameter.

    See also: [`Parameters`][griffe.Parameters].
    """

    def __init__(
        self,
        name: str,
        *,
        annotation: str | Expr | None = None,
        kind: ParameterKind | None = None,
        default: str | Expr | None = None,
        docstring: Docstring | None = None,
    ) -> None:
        """Initialize the parameter.

        Parameters:
            name: The parameter name, without leading stars (`*` or `**`).
            annotation: The parameter annotation, if any.
            kind: The parameter kind.
            default: The parameter default, if any.
            docstring: The parameter docstring.
        """
        self.name: str = name
        """The parameter name."""
        self.annotation: str | Expr | None = annotation
        """The parameter type annotation."""
        self.kind: ParameterKind | None = kind
        """The parameter kind."""
        self.default: str | Expr | None = default
        """The parameter default value."""
        self.docstring: Docstring | None = docstring
        """The parameter docstring."""
        # The parent function is set in `Function.__init__`,
        # when the parameters are assigned to the function.
        self.function: Function | None = None
        """The parent function of the parameter."""

    def __str__(self) -> str:
        param = f"{self.name}: {self.annotation} = {self.default}"
        if self.kind:
            return f"[{self.kind.value}] {param}"
        return param

    def __repr__(self) -> str:
        return f"Parameter(name={self.name!r}, annotation={self.annotation!r}, kind={self.kind!r}, default={self.default!r})"

    def __eq__(self, value: object, /) -> bool:
        """Parameters are equal if all their attributes except `docstring` and `function` are equal."""
        if not isinstance(value, Parameter):
            return NotImplemented
        return (
            self.name == value.name
            and self.annotation == value.annotation
            and self.kind == value.kind
            and self.default == value.default
        )

    @property
    def required(self) -> bool:
        """Whether this parameter is required."""
        return self.default is None

    def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        """Return this parameter's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base: dict[str, Any] = {
            "name": self.name,
            "annotation": self.annotation,
            "kind": self.kind,
            "default": self.default,
        }
        if self.docstring:
            base["docstring"] = self.docstring.as_dict(full=full)
        return base


class Parameters:
    """This class is a container for parameters.

    It allows to get parameters using their position (index) or their name:

    ```pycon
    >>> parameters = Parameters(Parameter("hello"))
    >>> parameters[0] is parameters["hello"]
    True
    ```

    See also: [`Parameter`][griffe.Parameter].
    """

    def __init__(self, *parameters: Parameter) -> None:
        """Initialize the parameters container.

        Parameters:
            *parameters: The initial parameters to add to the container.
        """
        self._params: list[Parameter] = list(parameters)

    def __repr__(self) -> str:
        return f"Parameters({', '.join(repr(param) for param in self._params)})"

    def __getitem__(self, name_or_index: int | str) -> Parameter:
        """Get a parameter by index or name."""
        if isinstance(name_or_index, int):
            return self._params[name_or_index]
        name = name_or_index.lstrip("*")
        try:
            return next(param for param in self._params if param.name == name)
        except StopIteration as error:
            raise KeyError(f"parameter {name_or_index} not found") from error

    def __setitem__(self, name_or_index: int | str, parameter: Parameter) -> None:
        """Set a parameter by index or name."""
        if isinstance(name_or_index, int):
            self._params[name_or_index] = parameter
        else:
            name = name_or_index.lstrip("*")
            try:
                index = next(idx for idx, param in enumerate(self._params) if param.name == name)
            except StopIteration:
                self._params.append(parameter)
            else:
                self._params[index] = parameter

    def __delitem__(self, name_or_index: int | str) -> None:
        """Delete a parameter by index or name."""
        if isinstance(name_or_index, int):
            del self._params[name_or_index]
        else:
            name = name_or_index.lstrip("*")
            try:
                index = next(idx for idx, param in enumerate(self._params) if param.name == name)
            except StopIteration as error:
                raise KeyError(f"parameter {name_or_index} not found") from error
            del self._params[index]

    def __len__(self):
        """The number of parameters."""
        return len(self._params)

    def __iter__(self):
        """Iterate over the parameters, in order."""
        return iter(self._params)

    def __contains__(self, param_name: str):
        """Whether a parameter with the given name is present."""
        try:
            next(param for param in self._params if param.name == param_name.lstrip("*"))
        except StopIteration:
            return False
        return True

    def add(self, parameter: Parameter) -> None:
        """Add a parameter to the container.

        Parameters:
            parameter: The function parameter to add.

        Raises:
            ValueError: When a parameter with the same name is already present.
        """
        if parameter.name in self:
            raise ValueError(f"parameter {parameter.name} already present")
        self._params.append(parameter)


class Object(ObjectAliasMixin):
    """An abstract class representing a Python object."""

    kind: Kind
    """The object kind."""
    is_alias: bool = False
    """Always false for objects."""
    is_collection: bool = False
    """Always false for objects."""
    inherited: bool = False
    """Always false for objects.

    Only aliases can be marked as inherited.
    """

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
        """The object name."""

        self.lineno: int | None = lineno
        """The starting line number of the object.

        See also: [`endlineno`][griffe.Object.endlineno].
        """

        self.endlineno: int | None = endlineno
        """The ending line number of the object.

        See also: [`lineno`][griffe.Object.lineno].
        """

        self.docstring: Docstring | None = docstring
        """The object docstring.

        See also: [`has_docstring`][griffe.Object.has_docstring],
        [`has_docstrings`][griffe.Object.has_docstrings].
        """

        self.parent: Module | Class | None = parent
        """The parent of the object (none if top module)."""

        self.members: dict[str, Object | Alias] = {}
        """The object members (modules, classes, functions, attributes).

        See also: [`inherited_members`][griffe.Object.inherited_members],
        [`get_member`][griffe.Object.get_member],
        [`set_member`][griffe.Object.set_member],
        [`filter_members`][griffe.Object.filter_members].
        """

        self.labels: set[str] = set()
        """The object labels (`property`, `dataclass`, etc.).

        See also: [`has_labels`][griffe.Object.has_labels]."""

        self.imports: dict[str, str] = {}
        """The other objects imported by this object.

        Keys are the names within the object (`from ... import ... as AS_NAME`),
        while the values are the actual names of the objects (`from ... import REAL_NAME as ...`).
        """

        self.exports: set[str] | list[str | ExprName] | None = None
        """The names of the objects exported by this (module) object through the `__all__` variable.

        Exports can contain string (object names) or resolvable names,
        like other lists of exports coming from submodules:

        ```python
        from .submodule import __all__ as submodule_all

        __all__ = ["hello", *submodule_all]
        ```

        Exports get expanded by the loader before it expands wildcards and resolves aliases.

        See also: [`GriffeLoader.expand_exports`][griffe.GriffeLoader.expand_exports].
        """

        self.aliases: dict[str, Alias] = {}
        """The aliases pointing to this object."""

        self.runtime: bool = runtime
        """Whether this object is available at runtime.

        Typically, type-guarded objects (under an `if TYPE_CHECKING` condition)
        are not available at runtime.
        """

        self.extra: dict[str, dict[str, Any]] = defaultdict(dict)
        """Namespaced dictionaries storing extra metadata for this object, used by extensions."""

        self.public: bool | None = None
        """Whether this object is public."""

        self.deprecated: bool | str | None = None
        """Whether this object is deprecated (boolean or deprecation message)."""

        self._lines_collection: LinesCollection | None = lines_collection
        self._modules_collection: ModulesCollection | None = modules_collection

        # attach the docstring to this object
        if docstring:
            docstring.parent = self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r}, {self.lineno!r}, {self.endlineno!r})"

    # Prevent using `__len__`.
    def __bool__(self) -> bool:
        """An object is always true-ish."""
        return True

    def __len__(self) -> int:
        """The number of members in this object, recursively."""
        return len(self.members) + sum(len(member) for member in self.members.values())

    @property
    def has_docstring(self) -> bool:
        """Whether this object has a docstring (empty or not).

        See also: [`docstring`][griffe.Object.docstring],
        [`has_docstrings`][griffe.Object.has_docstrings].
        """
        return bool(self.docstring)

    # NOTE: (pawamoy) I'm not happy with `has_docstrings`.
    # It currently recurses into submodules, but that doesn't make sense
    # if downstream projects use it to know if they should render an init module
    # while not rendering submodules too: the property could tell them there are
    # docstrings, but they could be in submodules, not in the init module.
    # Maybe we should derive it into new properties: `has_local_docstrings`,
    # `has_docstrings`, `has_public_docstrings`... Maybe we should make it a function?`
    # For now it's used in mkdocstrings-python so we must be careful with changes.
    @property
    def has_docstrings(self) -> bool:
        """Whether this object or any of its members has a docstring (empty or not).

        Inherited members are not considered. Imported members are not considered,
        unless they are also public.

        See also: [`docstring`][griffe.Object.docstring],
        [`has_docstring`][griffe.Object.has_docstring].
        """
        if self.has_docstring:
            return True
        for member in self.members.values():
            try:
                if (not member.is_imported or member.is_public) and member.has_docstrings:
                    return True
            except AliasResolutionError:
                continue
        return False

    def is_kind(self, kind: str | Kind | set[str | Kind]) -> bool:
        """Tell if this object is of the given kind.

        See also: [`is_module`][griffe.Object.is_module],
        [`is_class`][griffe.Object.is_class],
        [`is_function`][griffe.Object.is_function],
        [`is_attribute`][griffe.Object.is_attribute],
        [`is_alias`][griffe.Object.is_alias].

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
            return self.kind in (knd if isinstance(knd, Kind) else Kind(knd) for knd in kind)
        if isinstance(kind, str):
            kind = Kind(kind)
        return self.kind is kind

    @property
    def inherited_members(self) -> dict[str, Alias]:
        """Members that are inherited from base classes.

        This method is part of the consumer API:
        do not use when producing Griffe trees!

        See also: [`members`][griffe.Object.members].
        """
        if not isinstance(self, Class):
            return {}
        try:
            mro = self.mro()
        except ValueError as error:
            logger.debug(error)
            return {}
        inherited_members = {}
        for base in reversed(mro):
            for name, member in base.members.items():
                if name not in self.members:
                    inherited_members[name] = Alias(name, member, parent=self, inherited=True)
        return inherited_members

    @property
    def is_module(self) -> bool:
        """Whether this object is a module.

        See also:  [`is_init_module`][griffe.Object.is_init_module].
        [`is_class`][griffe.Object.is_class],
        [`is_function`][griffe.Object.is_function],
        [`is_attribute`][griffe.Object.is_attribute],
        [`is_alias`][griffe.Object.is_alias],
        [`is_kind`][griffe.Object.is_kind].
        """
        return self.kind is Kind.MODULE

    @property
    def is_class(self) -> bool:
        """Whether this object is a class.

        See also:  [`is_module`][griffe.Object.is_module].
        [`is_function`][griffe.Object.is_function],
        [`is_attribute`][griffe.Object.is_attribute],
        [`is_alias`][griffe.Object.is_alias],
        [`is_kind`][griffe.Object.is_kind].
        """
        return self.kind is Kind.CLASS

    @property
    def is_function(self) -> bool:
        """Whether this object is a function.

        See also:  [`is_module`][griffe.Object.is_module].
        [`is_class`][griffe.Object.is_class],
        [`is_attribute`][griffe.Object.is_attribute],
        [`is_alias`][griffe.Object.is_alias],
        [`is_kind`][griffe.Object.is_kind].
        """
        return self.kind is Kind.FUNCTION

    @property
    def is_attribute(self) -> bool:
        """Whether this object is an attribute.

        See also:  [`is_module`][griffe.Object.is_module].
        [`is_class`][griffe.Object.is_class],
        [`is_function`][griffe.Object.is_function],
        [`is_alias`][griffe.Object.is_alias],
        [`is_kind`][griffe.Object.is_kind].
        """
        return self.kind is Kind.ATTRIBUTE

    @property
    def is_init_module(self) -> bool:
        """Whether this object is an `__init__.py` module.

        See also:  [`is_module`][griffe.Object.is_module].
        """
        return False

    @property
    def is_package(self) -> bool:
        """Whether this object is a package (top module).

        See also:  [`is_subpackage`][griffe.Object.is_subpackage].
        """
        return False

    @property
    def is_subpackage(self) -> bool:
        """Whether this object is a subpackage.

        See also:  [`is_package`][griffe.Object.is_package].
        """
        return False

    @property
    def is_namespace_package(self) -> bool:
        """Whether this object is a namespace package (top folder, no `__init__.py`).

        See also:  [`is_namespace_subpackage`][griffe.Object.is_namespace_subpackage].
        """
        return False

    @property
    def is_namespace_subpackage(self) -> bool:
        """Whether this object is a namespace subpackage.

        See also:  [`is_namespace_package`][griffe.Object.is_namespace_package].
        """
        return False

    def has_labels(self, *labels: str) -> bool:
        """Tell if this object has all the given labels.

        See also: [`labels`][griffe.Object.labels].

        Parameters:
            *labels: Labels that must be present.

        Returns:
            True or False.
        """
        return set(labels).issubset(self.labels)

    def filter_members(self, *predicates: Callable[[Object | Alias], bool]) -> dict[str, Object | Alias]:
        """Filter and return members based on predicates.

        See also: [`members`][griffe.Object.members].

        Parameters:
            *predicates: A list of predicates, i.e. callables accepting a member as argument and returning a boolean.

        Returns:
            A dictionary of members.
        """
        if not predicates:
            return self.members
        members: dict[str, Object | Alias] = {
            name: member for name, member in self.members.items() if all(predicate(member) for predicate in predicates)
        }
        return members

    @property
    def module(self) -> Module:
        """The parent module of this object.

        See also: [`package`][griffe.Object.package].

        Examples:
            >>> import griffe
            >>> markdown = griffe.load("markdown")
            >>> markdown["core.Markdown.references"].module
            Module(PosixPath('~/project/.venv/lib/python3.11/site-packages/markdown/core.py'))
            >>> # The `module` of a module is itself.
            >>> markdown["core"].module
            Module(PosixPath('~/project/.venv/lib/python3.11/site-packages/markdown/core.py'))

        Raises:
            ValueError: When the object is not a module and does not have a parent.
        """
        if isinstance(self, Module):
            return self
        if self.parent is not None:
            return self.parent.module
        raise ValueError(f"Object {self.name} does not have a parent module")

    @property
    def package(self) -> Module:
        """The absolute top module (the package) of this object.

        See also: [`module`][griffe.Object.module].

        Examples:
            >>> import griffe
            >>> markdown = griffe.load("markdown")
            >>> markdown["core.Markdown.references"].package
            Module(PosixPath('~/project/.venv/lib/python3.11/site-packages/markdown/__init__.py'))
        """
        module = self.module
        while module.parent:
            module = module.parent  # type: ignore[assignment]  # always a module
        return module

    @property
    def filepath(self) -> Path | list[Path]:
        """The file path (or directory list for namespace packages) where this object was defined.

        See also: [`relative_filepath`][griffe.Object.relative_filepath],
        [`relative_package_filepath`][griffe.Object.relative_package_filepath].

        Examples:
            >>> import griffe
            >>> markdown = griffe.load("markdown")
            >>> markdown.filepath
            PosixPath('~/project/.venv/lib/python3.11/site-packages/markdown/__init__.py')
        """
        return self.module.filepath

    @property
    def relative_package_filepath(self) -> Path:
        """The file path where this object was defined, relative to the top module path.

        See also: [`filepath`][griffe.Object.filepath],
        [`relative_filepath`][griffe.Object.relative_filepath].

        Raises:
            ValueError: When the relative path could not be computed.
        """
        package_path = self.package.filepath

        # Current "module" is a namespace package.
        if isinstance(self.filepath, list):
            # Current package is a namespace package.
            if isinstance(package_path, list):
                for pkg_path in package_path:
                    for self_path in self.filepath:
                        with suppress(ValueError):
                            return self_path.relative_to(pkg_path.parent)

            # Current package is a regular package.
            # NOTE: Technically it makes no sense to have a namespace package
            # under a non-namespace one, so we should never enter this branch.
            else:
                for self_path in self.filepath:
                    with suppress(ValueError):
                        return self_path.relative_to(package_path.parent.parent)
            raise ValueError

        # Current package is a namespace package,
        # and current module is a regular module or package.
        if isinstance(package_path, list):
            for pkg_path in package_path:
                with suppress(ValueError):
                    return self.filepath.relative_to(pkg_path.parent)
            raise ValueError

        # Current package is a regular package,
        # and current module is a regular module or package,
        # try to compute the path relative to the parent folder
        # of the package (search path).
        return self.filepath.relative_to(package_path.parent.parent)

    @property
    def relative_filepath(self) -> Path:
        """The file path where this object was defined, relative to the current working directory.

        If this object's file path is not relative to the current working directory, return its absolute path.

        See also: [`filepath`][griffe.Object.filepath],
        [`relative_package_filepath`][griffe.Object.relative_package_filepath].

        Raises:
            ValueError: When the relative path could not be computed.
        """
        cwd = Path.cwd()
        if isinstance(self.filepath, list):
            for self_path in self.filepath:
                with suppress(ValueError):
                    return self_path.relative_to(cwd)
            raise ValueError(f"No directory in {self.filepath!r} is relative to the current working directory {cwd}")
        try:
            return self.filepath.relative_to(cwd)
        except ValueError:
            return self.filepath

    @property
    def path(self) -> str:
        """The dotted path of this object.

        On regular objects (not aliases), the path is the canonical path.

        See also: [`canonical_path`][griffe.Object.canonical_path].

        Examples:
            >>> import griffe
            >>> markdown = griffe.load("markdown")
            >>> markdown["core.Markdown.references"].path
            'markdown.core.Markdown.references'
        """
        return self.canonical_path

    @property
    def canonical_path(self) -> str:
        """The full dotted path of this object.

        The canonical path is the path where the object was defined (not imported).

        See also: [`path`][griffe.Object.path].
        """
        if self.parent is None:
            return self.name
        return f"{self.parent.path}.{self.name}"

    @property
    def modules_collection(self) -> ModulesCollection:
        """The modules collection attached to this object or its parents.

        Raises:
            ValueError: When no modules collection can be found in the object or its parents.
        """
        if self._modules_collection is not None:
            return self._modules_collection
        if self.parent is None:
            raise ValueError("no modules collection in this object or its parents")
        return self.parent.modules_collection

    @property
    def lines_collection(self) -> LinesCollection:
        """The lines collection attached to this object or its parents.

        See also: [`lines`][griffe.Object.lines],
        [`source`][griffe.Object.source].

        Raises:
            ValueError: When no modules collection can be found in the object or its parents.
        """
        if self._lines_collection is not None:
            return self._lines_collection
        if self.parent is None:
            raise ValueError("no lines collection in this object or its parents")
        return self.parent.lines_collection

    @property
    def lines(self) -> list[str]:
        """The lines containing the source of this object.

        See also: [`lines_collection`][griffe.Object.lines_collection],
        [`source`][griffe.Object.source].
        """
        try:
            filepath = self.filepath
        except BuiltinModuleError:
            return []
        if isinstance(filepath, list):
            return []
        try:
            lines = self.lines_collection[filepath]
        except KeyError:
            return []
        if self.is_module:
            return lines
        if self.lineno is None or self.endlineno is None:
            return []
        return lines[self.lineno - 1 : self.endlineno]

    @property
    def source(self) -> str:
        """The source code of this object.

        See also: [`lines`][griffe.Object.lines],
        [`lines_collection`][griffe.Object.lines_collection].
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
        # TODO: Better match Python's own scoping rules?
        # Also, maybe return regular paths instead of canonical ones?

        # Name is a member this object.
        if name in self.members:
            if self.members[name].is_alias:
                return self.members[name].target_path  # type: ignore[union-attr]
            return self.members[name].path

        # Name unknown and no more parent scope.
        if self.parent is None:
            # could be a built-in
            raise NameResolutionError(f"{name} could not be resolved in the scope of {self.path}")

        # Name is parent, non-module object.
        if name == self.parent.name and not self.parent.is_module:
            return self.parent.path

        # Recurse in parent.
        return self.parent.resolve(name)

    def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:
        """Return this object's data as a dictionary.

        See also: [`as_json`][griffe.Object.as_json].

        Parameters:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base: dict[str, Any] = {
            "kind": self.kind,
            "name": self.name,
        }

        if full:
            base.update(
                {
                    "path": self.path,
                    "filepath": self.filepath,
                    "relative_filepath": self.relative_filepath,
                    "relative_package_filepath": self.relative_package_filepath,
                },
            )

        if self.lineno is not None:
            base["lineno"] = self.lineno
        if self.endlineno is not None:
            base["endlineno"] = self.endlineno
        if self.docstring:
            base["docstring"] = self.docstring

        base["labels"] = self.labels
        base["members"] = {name: member.as_dict(full=full, **kwargs) for name, member in self.members.items()}

        return base


class Alias(ObjectAliasMixin):
    """This class represents an alias, or indirection, to an object declared in another module.

    Aliases represent objects that are in the scope of a module or class,
    but were imported from another module.

    They behave almost exactly like regular objects, to a few exceptions:

    - line numbers are those of the alias, not the target
    - the path is the alias path, not the canonical one
    - the name can be different from the target's
    - if the target can be resolved, the kind is the target's kind
    - if the target cannot be resolved, the kind becomes [Kind.ALIAS][griffe.Kind]
    """

    is_alias: bool = True
    """Always true for aliases."""
    is_collection: bool = False
    """Always false for aliases.

    See also: [`ModulesCollection`][griffe.ModulesCollection].
    """

    def __init__(
        self,
        name: str,
        target: str | Object | Alias,
        *,
        lineno: int | None = None,
        endlineno: int | None = None,
        runtime: bool = True,
        parent: Module | Class | Alias | None = None,
        inherited: bool = False,
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
            inherited: Whether this alias wraps an inherited member.
        """
        self.name: str = name
        """The alias name."""

        self.alias_lineno: int | None = lineno
        """The starting line number of the alias."""

        self.alias_endlineno: int | None = endlineno
        """The ending line number of the alias."""

        self.runtime: bool = runtime
        """Whether this alias is available at runtime."""

        self.inherited: bool = inherited
        """Whether this alias represents an inherited member."""

        self.public: bool | None = None
        """Whether this alias is public."""

        self.deprecated: str | bool | None = None
        """Whether this alias is deprecated (boolean or deprecation message)."""

        self._parent: Module | Class | Alias | None = parent
        self._passed_through: bool = False

        self.target_path: str
        """The path of this alias' target."""

        if isinstance(target, str):
            self._target: Object | Alias | None = None
            self.target_path = target
        else:
            self._target = target
            self.target_path = target.path
            self._update_target_aliases()

    def __repr__(self) -> str:
        return f"Alias({self.name!r}, {self.target_path!r})"

    # Prevent using `__len__`.
    def __bool__(self) -> bool:
        """An alias is always true-ish."""
        return True

    def __len__(self) -> int:
        """The length of an alias is always 1."""
        return 1

    # SPECIAL PROXIES -------------------------------
    # The following methods and properties exist on the target(s),
    # but we must handle them in a special way.

    @property
    def kind(self) -> Kind:
        """The target's kind, or `Kind.ALIAS` if the target cannot be resolved.

        See also: [`is_kind`][griffe.Alias.is_kind].
        """
        # custom behavior to avoid raising exceptions
        try:
            return self.final_target.kind
        except (AliasResolutionError, CyclicAliasError):
            return Kind.ALIAS

    @property
    def has_docstring(self) -> bool:
        """Whether this alias' target has a non-empty docstring.

        See also: [`has_docstrings`][griffe.Alias.has_docstrings],
        [`docstring`][griffe.Alias.docstring].
        """
        try:
            return self.final_target.has_docstring
        except (AliasResolutionError, CyclicAliasError):
            return False

    @property
    def has_docstrings(self) -> bool:
        """Whether this alias' target or any of its members has a non-empty docstring.

        See also: [`has_docstring`][griffe.Alias.has_docstring],
        [`docstring`][griffe.Alias.docstring].
        """
        try:
            return self.final_target.has_docstrings
        except (AliasResolutionError, CyclicAliasError):
            return False

    @property
    def parent(self) -> Module | Class | Alias | None:
        """The parent of this alias."""
        return self._parent

    @parent.setter
    def parent(self, value: Module | Class | Alias) -> None:
        self._parent = value
        self._update_target_aliases()

    @property
    def path(self) -> str:
        """The dotted path / import path of this object.

        See also: [`canonical_path`][griffe.Alias.canonical_path].
        """
        return f"{self.parent.path}.{self.name}"  # type: ignore[union-attr]  # we assume there's always a parent

    @property
    def modules_collection(self) -> ModulesCollection:
        """The modules collection attached to the alias parents."""
        # no need to forward to the target
        return self.parent.modules_collection  # type: ignore[union-attr]  # we assume there's always a parent

    @property
    def members(self) -> dict[str, Object | Alias]:
        """The target's members (modules, classes, functions, attributes).

        See also: [`inherited_members`][griffe.Alias.inherited_members],
        [`get_member`][griffe.Alias.get_member],
        [`set_member`][griffe.Alias.set_member],
        [`filter_members`][griffe.Alias.filter_members].
        """
        final_target = self.final_target

        # We recreate aliases to maintain a correct hierarchy,
        # and therefore correct paths. The path of an alias member
        # should be the path of the alias plus the member's name,
        # not the original member's path.
        return {
            name: Alias(name, target=member, parent=self, inherited=False)
            for name, member in final_target.members.items()
        }

    @property
    def inherited_members(self) -> dict[str, Alias]:
        """Members that are inherited from base classes.

        Each inherited member of the target will be wrapped in an alias,
        to preserve correct object access paths.

        This method is part of the consumer API:
        do not use when producing Griffe trees!

        See also: [`members`][griffe.Alias.members].
        """
        final_target = self.final_target

        # We recreate aliases to maintain a correct hierarchy,
        # and therefore correct paths. The path of an alias member
        # should be the path of the alias plus the member's name,
        # not the original member's path.
        return {
            name: Alias(name, target=member, parent=self, inherited=True)
            for name, member in final_target.inherited_members.items()
        }

    def as_json(self, *, full: bool = False, **kwargs: Any) -> str:
        """Return this target's data as a JSON string.

        See also: [`as_dict`][griffe.Alias.as_dict].

        Parameters:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options passed to encoder.

        Returns:
            A JSON string.
        """
        try:
            return self.final_target.as_json(full=full, **kwargs)
        except (AliasResolutionError, CyclicAliasError):
            return super().as_json(full=full, **kwargs)

    # GENERIC OBJECT PROXIES --------------------------------
    # The following methods and properties exist on the target(s).
    # We first try to reach the final target, triggering alias resolution errors
    # and cyclic aliases errors early. We avoid recursing in the alias chain.

    @property
    def extra(self) -> dict:
        """Namespaced dictionaries storing extra metadata for this object, used by extensions."""
        return self.final_target.extra

    @property
    def lineno(self) -> int | None:
        """The starting line number of the target object.

        See also: [`endlineno`][griffe.Alias.endlineno].
        """
        return self.final_target.lineno

    @property
    def endlineno(self) -> int | None:
        """The ending line number of the target object.

        See also: [`lineno`][griffe.Alias.lineno].
        """
        return self.final_target.endlineno

    @property
    def docstring(self) -> Docstring | None:
        """The target docstring.

        See also: [`has_docstring`][griffe.Alias.has_docstring],
        [`has_docstrings`][griffe.Alias.has_docstrings].
        """
        return self.final_target.docstring

    @docstring.setter
    def docstring(self, docstring: Docstring | None) -> None:
        self.final_target.docstring = docstring

    @property
    def labels(self) -> set[str]:
        """The target labels (`property`, `dataclass`, etc.).

        See also: [`has_labels`][griffe.Alias.has_labels].
        """
        return self.final_target.labels

    @property
    def imports(self) -> dict[str, str]:
        """The other objects imported by this alias' target.

        Keys are the names within the object (`from ... import ... as AS_NAME`),
        while the values are the actual names of the objects (`from ... import REAL_NAME as ...`).

        See also: [`is_imported`][griffe.Alias.is_imported].
        """
        return self.final_target.imports

    @property
    def exports(self) -> set[str] | list[str | ExprName] | None:
        """The names of the objects exported by this (module) object through the `__all__` variable.

        Exports can contain string (object names) or resolvable names,
        like other lists of exports coming from submodules:

        ```python
        from .submodule import __all__ as submodule_all

        __all__ = ["hello", *submodule_all]
        ```

        Exports get expanded by the loader before it expands wildcards and resolves aliases.

        See also: [`GriffeLoader.expand_exports`][griffe.GriffeLoader.expand_exports].
        """
        return self.final_target.exports

    @property
    def aliases(self) -> dict[str, Alias]:
        """The aliases pointing to this object."""
        return self.final_target.aliases

    def is_kind(self, kind: str | Kind | set[str | Kind]) -> bool:
        """Tell if this object is of the given kind.

        See also: [`is_module`][griffe.Alias.is_module],
        [`is_class`][griffe.Alias.is_class],
        [`is_function`][griffe.Alias.is_function],
        [`is_attribute`][griffe.Alias.is_attribute],
        [`is_alias`][griffe.Alias.is_alias].

        Parameters:
            kind: An instance or set of kinds (strings or enumerations).

        Raises:
            ValueError: When an empty set is given as argument.

        Returns:
            True or False.
        """
        return self.final_target.is_kind(kind)

    @property
    def is_module(self) -> bool:
        """Whether this object is a module.

        See also:  [`is_init_module`][griffe.Alias.is_init_module].
        [`is_class`][griffe.Alias.is_class],
        [`is_function`][griffe.Alias.is_function],
        [`is_attribute`][griffe.Alias.is_attribute],
        [`is_alias`][griffe.Alias.is_alias],
        [`is_kind`][griffe.Alias.is_kind].
        """
        return self.final_target.is_module

    @property
    def is_class(self) -> bool:
        """Whether this object is a class.

        See also: [`is_module`][griffe.Alias.is_module],
        [`is_function`][griffe.Alias.is_function],
        [`is_attribute`][griffe.Alias.is_attribute],
        [`is_alias`][griffe.Alias.is_alias],
        [`is_kind`][griffe.Alias.is_kind].
        """
        return self.final_target.is_class

    @property
    def is_function(self) -> bool:
        """Whether this object is a function.

        See also: [`is_module`][griffe.Alias.is_module],
        [`is_class`][griffe.Alias.is_class],
        [`is_attribute`][griffe.Alias.is_attribute],
        [`is_alias`][griffe.Alias.is_alias],
        [`is_kind`][griffe.Alias.is_kind].
        """
        return self.final_target.is_function

    @property
    def is_attribute(self) -> bool:
        """Whether this object is an attribute.

        See also: [`is_module`][griffe.Alias.is_module],
        [`is_class`][griffe.Alias.is_class],
        [`is_function`][griffe.Alias.is_function],
        [`is_alias`][griffe.Alias.is_alias],
        [`is_kind`][griffe.Alias.is_kind].
        """
        return self.final_target.is_attribute

    def has_labels(self, *labels: str) -> bool:
        """Tell if this object has all the given labels.

        See also: [`labels`][griffe.Alias.labels].

        Parameters:
            *labels: Labels that must be present.

        Returns:
            True or False.
        """
        return self.final_target.has_labels(*labels)

    def filter_members(self, *predicates: Callable[[Object | Alias], bool]) -> dict[str, Object | Alias]:
        """Filter and return members based on predicates.

        See also: [`members`][griffe.Alias.members],
        [`get_member`][griffe.Alias.get_member],
        [`set_member`][griffe.Alias.set_member].

        Parameters:
            *predicates: A list of predicates, i.e. callables accepting a member as argument and returning a boolean.

        Returns:
            A dictionary of members.
        """
        return self.final_target.filter_members(*predicates)

    @property
    def module(self) -> Module:
        """The parent module of this object.

        See also: [`package`][griffe.Alias.package].

        Raises:
            ValueError: When the object is not a module and does not have a parent.
        """
        return self.final_target.module

    @property
    def package(self) -> Module:
        """The absolute top module (the package) of this object.

        See also: [`module`][griffe.Alias.module].
        """
        return self.final_target.package

    @property
    def filepath(self) -> Path | list[Path]:
        """The file path (or directory list for namespace packages) where this object was defined.

        See also: [`relative_filepath`][griffe.Alias.relative_filepath],
        [`relative_package_filepath`][griffe.Alias.relative_package_filepath].
        """
        return self.final_target.filepath

    @property
    def relative_filepath(self) -> Path:
        """The file path where this object was defined, relative to the current working directory.

        If this object's file path is not relative to the current working directory, return its absolute path.

        See also: [`filepath`][griffe.Alias.filepath],
        [`relative_package_filepath`][griffe.Alias.relative_package_filepath].

        Raises:
            ValueError: When the relative path could not be computed.
        """
        return self.final_target.relative_filepath

    @property
    def relative_package_filepath(self) -> Path:
        """The file path where this object was defined, relative to the top module path.

        See also: [`filepath`][griffe.Alias.filepath],
        [`relative_filepath`][griffe.Alias.relative_filepath].

        Raises:
            ValueError: When the relative path could not be computed.
        """
        return self.final_target.relative_package_filepath

    @property
    def canonical_path(self) -> str:
        """The full dotted path of this object.

        The canonical path is the path where the object was defined (not imported).

        See also: [`path`][griffe.Alias.path].
        """
        return self.final_target.canonical_path

    @property
    def lines_collection(self) -> LinesCollection:
        """The lines collection attached to this object or its parents.

        See also: [`lines`][griffe.Alias.lines],
        [`source`][griffe.Alias.source].

        Raises:
            ValueError: When no modules collection can be found in the object or its parents.
        """
        return self.final_target.lines_collection

    @property
    def lines(self) -> list[str]:
        """The lines containing the source of this object.

        See also: [`source`][griffe.Alias.source],
        [`lines_collection`][griffe.Alias.lines_collection].
        """
        return self.final_target.lines

    @property
    def source(self) -> str:
        """The source code of this object.

        See also: [`lines`][griffe.Alias.lines],
        [`lines_collection`][griffe.Alias.lines_collection].
        """
        return self.final_target.source

    def resolve(self, name: str) -> str:
        """Resolve a name within this object's and parents' scope.

        Parameters:
            name: The name to resolve.

        Raises:
            NameResolutionError: When the name could not be resolved.

        Returns:
            The resolved name.
        """
        return self.final_target.resolve(name)

    # SPECIFIC MODULE/CLASS/FUNCTION/ATTRIBUTE PROXIES ---------------
    # These methods and properties exist on targets of specific kind.
    # We first try to reach the final target, triggering alias resolution errors
    # and cyclic aliases errors early. We avoid recursing in the alias chain.

    @property
    def _filepath(self) -> Path | list[Path] | None:
        return cast(Module, self.final_target)._filepath

    @property
    def bases(self) -> list[Expr | str]:
        """The class bases.

        See also: [`Class`][griffe.Class],
        [`resolved_bases`][griffe.Alias.resolved_bases],
        [`mro`][griffe.Alias.mro].
        """
        return cast(Class, self.final_target).bases

    @property
    def decorators(self) -> list[Decorator]:
        """The class/function decorators.

        See also: [`Function`][griffe.Function],
        [`Class`][griffe.Class].
        """
        return cast(Union[Class, Function], self.target).decorators

    @property
    def imports_future_annotations(self) -> bool:
        """Whether this module import future annotations."""
        return cast(Module, self.final_target).imports_future_annotations

    @property
    def is_init_module(self) -> bool:
        """Whether this module is an `__init__.py` module.

        See also: [`is_module`][griffe.Alias.is_module].
        """
        return cast(Module, self.final_target).is_init_module

    @property
    def is_package(self) -> bool:
        """Whether this module is a package (top module).

        See also: [`is_subpackage`][griffe.Alias.is_subpackage].
        """
        return cast(Module, self.final_target).is_package

    @property
    def is_subpackage(self) -> bool:
        """Whether this module is a subpackage.

        See also: [`is_package`][griffe.Alias.is_package].
        """
        return cast(Module, self.final_target).is_subpackage

    @property
    def is_namespace_package(self) -> bool:
        """Whether this module is a namespace package (top folder, no `__init__.py`).

        See also: [`is_namespace_subpackage`][griffe.Alias.is_namespace_subpackage].
        """
        return cast(Module, self.final_target).is_namespace_package

    @property
    def is_namespace_subpackage(self) -> bool:
        """Whether this module is a namespace subpackage.

        See also: [`is_namespace_package`][griffe.Alias.is_namespace_package].
        """
        return cast(Module, self.final_target).is_namespace_subpackage

    @property
    def overloads(self) -> dict[str, list[Function]] | list[Function] | None:
        """The overloaded signatures declared in this class/module or for this function."""
        return cast(Union[Module, Class, Function], self.final_target).overloads

    @overloads.setter
    def overloads(self, overloads: list[Function] | None) -> None:
        cast(Union[Module, Class, Function], self.final_target).overloads = overloads

    @property
    def parameters(self) -> Parameters:
        """The parameters of the current function or `__init__` method for classes.

        This property can fetch inherited members,
        and therefore is part of the consumer API:
        do not use when producing Griffe trees!
        """
        return cast(Union[Class, Function], self.final_target).parameters

    @property
    def returns(self) -> str | Expr | None:
        """The function return type annotation."""
        return cast(Function, self.final_target).returns

    @returns.setter
    def returns(self, returns: str | Expr | None) -> None:
        cast(Function, self.final_target).returns = returns

    @property
    def setter(self) -> Function | None:
        """The setter linked to this function (property)."""
        return cast(Attribute, self.final_target).setter

    @property
    def deleter(self) -> Function | None:
        """The deleter linked to this function (property)."""
        return cast(Attribute, self.final_target).deleter

    @property
    def value(self) -> str | Expr | None:
        """The attribute value."""
        return cast(Attribute, self.final_target).value

    @property
    def annotation(self) -> str | Expr | None:
        """The attribute type annotation."""
        return cast(Attribute, self.final_target).annotation

    @annotation.setter
    def annotation(self, annotation: str | Expr | None) -> None:
        cast(Attribute, self.final_target).annotation = annotation

    @property
    def resolved_bases(self) -> list[Object]:
        """Resolved class bases.

        This method is part of the consumer API:
        do not use when producing Griffe trees!
        """
        return cast(Class, self.final_target).resolved_bases

    def mro(self) -> list[Class]:
        """Return a list of classes in order corresponding to Python's MRO."""
        return cast(Class, self.final_target).mro()

    # SPECIFIC ALIAS METHOD AND PROPERTIES -----------------
    # These methods and properties do not exist on targets,
    # they are specific to aliases.

    @property
    def target(self) -> Object | Alias:
        """The resolved target (actual object), if possible.

        Upon accessing this property, if the target is not already resolved,
        a lookup is done using the modules collection to find the target.

        See also: [`final_target`][griffe.Alias.final_target],
        [`resolve_target`][griffe.Alias.resolve_target],
        [`resolved`][griffe.Alias.resolved].
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

    @property
    def final_target(self) -> Object:
        """The final, resolved target, if possible.

        This will iterate through the targets until a non-alias object is found.

        See also: [`target`][griffe.Alias.target],
        [`resolve_target`][griffe.Alias.resolve_target],
        [`resolved`][griffe.Alias.resolved].
        """
        # Here we quickly iterate on the alias chain,
        # remembering which path we've seen already to detect cycles.

        # The cycle detection is needed because alias chains can be created
        # as already resolved, and can contain cycles.

        # using a dict as an ordered set
        paths_seen: dict[str, None] = {}
        target = self
        while target.is_alias:
            if target.path in paths_seen:
                raise CyclicAliasError([*paths_seen, target.path])
            paths_seen[target.path] = None
            target = target.target  # type: ignore[assignment]
        return target  # type: ignore[return-value]

    def resolve_target(self) -> None:
        """Resolve the target.

        See also: [`target`][griffe.Alias.target],
        [`final_target`][griffe.Alias.final_target],
        [`resolved`][griffe.Alias.resolved].

        Raises:
            AliasResolutionError: When the target cannot be resolved.
                It happens when the target does not exist,
                or could not be loaded (unhandled dynamic object?),
                or when the target is from a module that was not loaded
                and added to the collection.
            CyclicAliasError: When the resolved target is the alias itself.
        """
        # Here we try to resolve the whole alias chain recursively.
        # We detect cycles by setting a "passed through" state variable
        # on each alias as we pass through it. Passing a second time
        # through an alias will raise a CyclicAliasError.

        # If a single link of the chain cannot be resolved,
        # the whole chain stays unresolved. This prevents
        # bad surprises later, in code that checks if
        # an alias is resolved by checking only
        # the first link of the chain.
        if self._passed_through:
            raise CyclicAliasError([self.target_path])
        self._passed_through = True
        try:
            self._resolve_target()
        finally:
            self._passed_through = False

    def _resolve_target(self) -> None:
        try:
            resolved = self.modules_collection.get_member(self.target_path)
        except KeyError as error:
            raise AliasResolutionError(self) from error
        if resolved is self:
            raise CyclicAliasError([self.target_path])
        if resolved.is_alias and not resolved.resolved:
            try:
                resolved.resolve_target()
            except CyclicAliasError as error:
                raise CyclicAliasError([self.target_path, *error.chain]) from error
        self._target = resolved
        if self.parent is not None:
            self._target.aliases[self.path] = self  # type: ignore[union-attr]  # we just set the target

    def _update_target_aliases(self) -> None:
        with suppress(AttributeError, AliasResolutionError, CyclicAliasError):
            self._target.aliases[self.path] = self  # type: ignore[union-attr]

    @property
    def resolved(self) -> bool:
        """Whether this alias' target is resolved."""
        return self._target is not None

    @property
    def wildcard(self) -> str | None:
        """The module on which the wildcard import is performed (if any).

        See also: [`GriffeLoader.expand_wildcards`][griffe.GriffeLoader.expand_wildcards].
        """
        if self.name.endswith("/*"):
            return self.target_path
        return None

    def as_dict(self, *, full: bool = False, **kwargs: Any) -> dict[str, Any]:  # noqa: ARG002
        """Return this alias' data as a dictionary.

        See also: [`as_json`][griffe.Alias.as_json].

        Parameters:
            full: Whether to return full info, or just base info.
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base: dict[str, Any] = {
            "kind": Kind.ALIAS,
            "name": self.name,
            "target_path": self.target_path,
        }

        if full:
            base["path"] = self.path

        if self.alias_lineno:
            base["lineno"] = self.alias_lineno
        if self.alias_endlineno:
            base["endlineno"] = self.alias_endlineno

        return base


class Module(Object):
    """The class representing a Python module."""

    kind = Kind.MODULE

    def __init__(self, *args: Any, filepath: Path | list[Path] | None = None, **kwargs: Any) -> None:
        """Initialize the module.

        Parameters:
            *args: See [`griffe.Object`][].
            filepath: The module file path (directory for namespace [sub]packages, none for builtin modules).
            **kwargs: See [`griffe.Object`][].
        """
        super().__init__(*args, **kwargs)
        self._filepath: Path | list[Path] | None = filepath
        self.overloads: dict[str, list[Function]] = defaultdict(list)
        """The overloaded signatures declared in this module."""

    def __repr__(self) -> str:
        try:
            return f"Module({self.filepath!r})"
        except BuiltinModuleError:
            return f"Module({self.name!r})"

    @property
    def filepath(self) -> Path | list[Path]:
        """The file path of this module.

        Raises:
            BuiltinModuleError: When the instance filepath is None.
        """
        if self._filepath is None:
            raise BuiltinModuleError(self.name)
        return self._filepath

    @property
    def imports_future_annotations(self) -> bool:
        """Whether this module import future annotations."""
        return (
            "annotations" in self.members
            and self.members["annotations"].is_alias
            and self.members["annotations"].target_path == "__future__.annotations"  # type: ignore[union-attr]
        )

    @property
    def is_init_module(self) -> bool:
        """Whether this module is an `__init__.py` module.

        See also: [`is_module`][griffe.Module.is_module].
        """
        if isinstance(self.filepath, list):
            return False
        try:
            return self.filepath.name.split(".", 1)[0] == "__init__"
        except BuiltinModuleError:
            return False

    @property
    def is_package(self) -> bool:
        """Whether this module is a package (top module).

        See also: [`is_subpackage`][griffe.Module.is_subpackage].
        """
        return not bool(self.parent) and self.is_init_module

    @property
    def is_subpackage(self) -> bool:
        """Whether this module is a subpackage.

        See also: [`is_package`][griffe.Module.is_package].
        """
        return bool(self.parent) and self.is_init_module

    @property
    def is_namespace_package(self) -> bool:
        """Whether this module is a namespace package (top folder, no `__init__.py`).

        See also: [`is_namespace_subpackage`][griffe.Module.is_namespace_subpackage].
        """
        try:
            return self.parent is None and isinstance(self.filepath, list)
        except BuiltinModuleError:
            return False

    @property
    def is_namespace_subpackage(self) -> bool:
        """Whether this module is a namespace subpackage.

        See also: [`is_namespace_package`][griffe.Module.is_namespace_package].
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

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this module's data as a dictionary.

        See also: [`as_json`][griffe.Module.as_json].

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = super().as_dict(**kwargs)
        if isinstance(self._filepath, list):
            base["filepath"] = [str(path) for path in self._filepath]
        elif self._filepath:
            base["filepath"] = str(self._filepath)
        else:
            base["filepath"] = None
        return base


class Class(Object):
    """The class representing a Python class."""

    kind = Kind.CLASS

    def __init__(
        self,
        *args: Any,
        bases: Sequence[Expr | str] | None = None,
        decorators: list[Decorator] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the class.

        Parameters:
            *args: See [`griffe.Object`][].
            bases: The list of base classes, if any.
            decorators: The class decorators, if any.
            **kwargs: See [`griffe.Object`][].
        """
        super().__init__(*args, **kwargs)

        self.bases: list[Expr | str] = list(bases) if bases else []
        """The class bases.

        See also: [`resolved_bases`][griffe.Class.resolved_bases],
        [`mro`][griffe.Class.mro].
        """

        self.decorators: list[Decorator] = decorators or []
        """The class decorators."""

        self.overloads: dict[str, list[Function]] = defaultdict(list)
        """The overloaded signatures declared in this class."""

    @property
    def parameters(self) -> Parameters:
        """The parameters of this class' `__init__` method, if any.

        This property fetches inherited members,
        and therefore is part of the consumer API:
        do not use when producing Griffe trees!
        """
        try:
            return self.all_members["__init__"].parameters  # type: ignore[union-attr]
        except KeyError:
            return Parameters()

    @property
    def resolved_bases(self) -> list[Object]:
        """Resolved class bases.

        This method is part of the consumer API:
        do not use when producing Griffe trees!

        See also: [`bases`][griffe.Class.bases],
        [`mro`][griffe.Class.mro].
        """
        resolved_bases = []
        for base in self.bases:
            base_path = base if isinstance(base, str) else base.canonical_path
            try:
                resolved_base = self.modules_collection[base_path]
                if resolved_base.is_alias:
                    resolved_base = resolved_base.final_target
            except (AliasResolutionError, CyclicAliasError, KeyError):
                logger.debug("Base class %s is not loaded, or not static, it cannot be resolved", base_path)
            else:
                resolved_bases.append(resolved_base)
        return resolved_bases

    def _mro(self, seen: tuple[str, ...] = ()) -> list[Class]:
        seen = (*seen, self.path)
        bases: list[Class] = [base for base in self.resolved_bases if base.is_class]  # type: ignore[misc]
        if not bases:
            return [self]
        for base in bases:
            if base.path in seen:
                cycle = " -> ".join(seen) + f" -> {base.path}"
                raise ValueError(f"Cannot compute C3 linearization, inheritance cycle detected: {cycle}")
        return [self, *c3linear_merge(*[base._mro(seen) for base in bases], bases)]

    def mro(self) -> list[Class]:
        """Return a list of classes in order corresponding to Python's MRO.

        See also: [`bases`][griffe.Class.bases],
        [`resolved_bases`][griffe.Class.resolved_bases].
        """
        return self._mro()[1:]  # remove self

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this class' data as a dictionary.

        See also: [`as_json`][griffe.Class.as_json].

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
        returns: str | Expr | None = None,
        decorators: list[Decorator] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the function.

        Parameters:
            *args: See [`griffe.Object`][].
            parameters: The function parameters.
            returns: The function return annotation.
            decorators: The function decorators, if any.
            **kwargs: See [`griffe.Object`][].
        """
        super().__init__(*args, **kwargs)
        self.parameters: Parameters = parameters or Parameters()
        """The function parameters."""
        self.returns: str | Expr | None = returns
        """The function return type annotation."""
        self.decorators: list[Decorator] = decorators or []
        """The function decorators."""
        self.overloads: list[Function] | None = None
        """The overloaded signatures of this function."""

        for parameter in self.parameters:
            parameter.function = self

    @property
    def annotation(self) -> str | Expr | None:
        """The type annotation of the returned value."""
        return self.returns

    def resolve(self, name: str) -> str:
        """Resolve a name within this object's and parents' scope.

        Parameters:
            name: The name to resolve.

        Raises:
            NameResolutionError: When the name could not be resolved.

        Returns:
            The resolved name.
        """
        # We're in an `__init__` method and name is a parameter name.
        if self.parent and self.name == "__init__" and name in self.parameters:
            return f"{self.parent.path}({name})"
        return super().resolve(name)

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this function's data as a dictionary.

        See also: [`as_json`][griffe.Function.as_json].

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
        value: str | Expr | None = None,
        annotation: str | Expr | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the function.

        Parameters:
            *args: See [`griffe.Object`][].
            value: The attribute value, if any.
            annotation: The attribute annotation, if any.
            **kwargs: See [`griffe.Object`][].
        """
        super().__init__(*args, **kwargs)
        self.value: str | Expr | None = value
        """The attribute value."""
        self.annotation: str | Expr | None = annotation
        """The attribute type annotation."""
        self.setter: Function | None = None
        """The setter linked to this property."""
        self.deleter: Function | None = None
        """The deleter linked to this property."""

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this function's data as a dictionary.

        See also: [`as_json`][griffe.Attribute.as_json].

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
