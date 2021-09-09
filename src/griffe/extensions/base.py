"""This module contains the base classes for dealing with extensions."""

from __future__ import annotations

import ast
import enum
from typing import Type


class When(enum.Enum):
    """This enumeration contains the different times at which an extension is used.

    Attributes:
        visit_starts: For each node, before starting the visit.
        children_visit_starts: For each node, after the visit has started, and before starting to visit children.
        children_visit_stops: For each node, after the children have been visited, and before finishing the visit.
        visit_stops: For each node, after finishing the visit.
    """

    visit_starts: int = 1
    children_visit_starts: int = 2
    children_visit_stops: int = 3
    visit_stops: int = 4


class Extension(ast.NodeVisitor):
    """The node visitor extension base class, to inherit from."""

    when: When

    def __init__(self, main_visitor: ast.NodeVisitor) -> None:
        """Initialize the visitor extension.

        Arguments:
            main_visitor: The main visitor.
        """
        super().__init__()
        self.visitor = main_visitor


class Extensions:
    """This class helps iterating on extensions that should run at different times."""

    def __init__(self) -> None:
        """Initialize the extensions container."""
        self._classes: list[Type[Extension]] = []
        self._instances: dict[When, list[Extension]] = {}

    @property
    def when_visit_starts(self) -> list[Extension]:
        """Return the visitors that run when the visit starts.

        Returns:
            Visitors.
        """
        return self._instances[When.visit_starts]

    @property
    def when_children_visit_starts(self) -> list[Extension]:
        """Return the visitors that run when the children visit starts.

        Returns:
            Visitors.
        """
        return self._instances[When.children_visit_starts]

    @property
    def when_children_visit_stops(self) -> list[Extension]:
        """Return the visitors that run when the children visit stops.

        Returns:
            Visitors.
        """
        return self._instances[When.children_visit_stops]

    @property
    def when_visit_stops(self) -> list[Extension]:
        """Return the visitors that run when the visit stops.

        Returns:
            Visitors.
        """
        return self._instances[When.visit_stops]

    def when(self, when: When) -> list[Extension]:
        """Return the visitors that run at the given time.

        Arguments:
            when: The selected time.

        Returns:
            Visitors.
        """
        return self._instances[when]

    def add(self, *extensions: Type[Extension]) -> None:
        """Add visitor extensions to this container.

        Arguments:
            *extensions: The extensions to add.
        """
        self._classes.extend(extensions)

    def instantiate(self, main_visitor: ast.NodeVisitor) -> Extensions:
        """Clear and instantiate the visitor classes.

        Arguments:
            main_visitor: The main visitor, leading the visit.

        Returns:
            Self, conveniently.
        """
        # clear instances
        for when in When:
            self._instances[when] = []
        # create instances
        for visitor_class in self._classes:
            self._instances[visitor_class.when].append(visitor_class(main_visitor))
        return self
