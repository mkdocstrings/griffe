"""This module contains the data classes that represent resolvable names and expressions."""

from __future__ import annotations

from typing import Any, Callable

from griffe.exceptions import NameResolutionError


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

    def __repr__(self) -> str:
        return f"AnnotationName(source={self.source!r}, full={self.full!r})"

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

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore
        """Return this name's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        return {"source": self.source, "full": self.full}


class Expression(list):  # noqa: WPS600
    """This class represents a Python expression.

    For example, it can represents complex annotations such as:

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

    def __str__(self):
        return "".join(str(element) for element in self)
