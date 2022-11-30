"""This module contains the data classes that represent resolvable names and expressions."""

from __future__ import annotations

import sys
from typing import Any, Callable

from griffe.exceptions import NameResolutionError

# TODO: remove once Python 3.7 support is dropped
if sys.version_info < (3, 8):
    from cached_property import cached_property
else:
    from functools import cached_property  # noqa: WPS440


class Name:
    """This class represents a Python object identified by a name in a given scope.

    Attributes:
        source: The name as written in the source code.
    """

    def __init__(self, source: str, full: str | Callable) -> None:
        """Initialize the name.

        Parameters:
            source: The name as written in the source code.
            full: The full, resolved name in the given scope, or a callable to resolve it later.
        """
        self.source: str = source
        if isinstance(full, str):
            self._full: str = full
            self._resolver: Callable = lambda: None
        else:
            self._full = ""
            self._resolver = full

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.full == other or self.brief == other
        if isinstance(other, (Name, Expression)):
            return self.full == other.full  # noqa: WPS437
        raise NotImplementedError(f"uncomparable types: {type(self)} and {type(other)}")

    def __repr__(self) -> str:
        return f"Name(source={self.source!r}, full={self.full!r})"

    def __str__(self) -> str:
        return self.source

    @property
    def full(self) -> str:
        """Return the full, resolved name.

        If it was given when creating the name, return that.
        If a callable was given, call it and return its result.
        It the name cannot be resolved, return the source.

        Returns:
            The resolved name or the source.
        """
        if not self._full:
            try:
                self._full = self._resolver() or self.source
            except NameResolutionError:
                # probably a built-in
                self._full = self.source
        return self._full

    @property
    def brief(self) -> str:
        """Return the brief source name.

        Returns:
            The last part of the source name.
        """
        return self.source.rsplit(".", 1)[-1]

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this name's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        return {"source": self.source, "full": self.full}


class Expression(list):  # noqa: WPS600
    """This class represents a Python expression.

    For example, it can represent complex annotations such as:

    - `Optional[Dict[str, Tuple[int, bool]]]`
    - `str | Callable | list[int]`

    Expressions are simple lists containing strings, names or expressions.
    Each name in the expression can be resolved to its full name within its scope.
    """

    def __init__(self, *values: str | Expression | Name) -> None:
        """Initialize the expression.

        Parameters:
            *values: The initial values of the expression.
        """
        super().__init__()
        self.extend(values)
        # for value in values:
        #     if isinstance(value, Expression):
        #         self.extend(value)
        #     else:
        #         self.append(value)

    def __str__(self):
        return "".join(str(element) for element in self)

    @property
    def full(self) -> str:
        """Return self as a string.

        This property is only useful to the AST utils.

        Returns:
            Self as a string.
        """
        return str(self)

    @property
    def kind(self) -> str:
        """Return the main type object as a string.

        Returns:
            The main type of this expression.
        """
        return str(self.non_optional).split("[", 1)[0].rsplit(".", 1)[-1].lower()

    @property
    def is_tuple(self) -> bool:
        """Tell whether this expression represents a tuple.

        Returns:
            True or False.
        """
        return self.kind == "tuple"

    @property
    def is_iterator(self) -> bool:
        """Tell whether this expression represents an iterator.

        Returns:
            True or False.
        """
        return self.kind == "iterator"

    @property
    def is_generator(self) -> bool:
        """Tell whether this expression represents a generator.

        Returns:
            True or False.
        """
        return self.kind == "generator"

    @cached_property
    def non_optional(self) -> Expression:
        """Return the same expression as non-optional.

        This will return a new expression without
        the `Optional[]` or `| None` parts.

        Returns:
            A non-optional expression.
        """
        if self[-1] == "None" and self[-2] == " | ":
            if isinstance(self[0], Expression):
                return self[0]
            return Expression(self[0])
        if self[0] == "None" and self[1] == " | ":
            if isinstance(self[2], Expression):
                return self[2]
            return Expression(self[2])
        if isinstance(self[0], Name) and self[0].full == "typing.Optional":
            if isinstance(self[2], Expression):
                return self[2]
            return Expression(self[2])
        return self

    def tuple_item(self, nth: int) -> str | Name:
        """Return the n-th item of this tuple expression.

        Parameters:
            nth: The item number.

        Returns:
            A string or name.
        """
        #  0  1     2     3
        # N|E [     E     ]
        #       N , N , N
        #       0 1 2 3 4
        return self.non_optional[2][2 * nth]

    def tuple_items(self) -> list[Name | Expression]:
        """Return a tuple items as a list.

        Returns:
            The tuple items.
        """
        return self.non_optional[2][::2]

    def iterator_item(self) -> Name | Expression:
        """Return the item of an iterator.

        Returns:
            The iterator item.
        """
        # Iterator[ItemType]
        return self.non_optional[2]

    def generator_items(self) -> tuple[Name | Expression, Name | Expression, Name | Expression]:
        """Return the items of a generator.

        Returns:
            The yield type.
            The send/receive type.
            The return type.
        """
        # Generator[Yield, Send/Receive, Return]
        return self.non_optional[2][0], self[2][2], self[2][4]
