"""This module stores collections of data, useful during parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from griffe.mixins import GetMembersMixin, SetCollectionMembersMixin

if TYPE_CHECKING:
    from griffe.dataclasses import Module


class LinesCollection(dict):  # noqa: WPS600
    """A simple dictionary containing the modules source code lines."""

    def __bool__(self):
        return True


class ModulesCollection(GetMembersMixin, SetCollectionMembersMixin):
    """A collection of modules, allowing easy access to members."""

    def __init__(self) -> None:
        """Initialize the collection."""
        self.members: dict[str, Module] = {}

    def __bool__(self):
        return True

    def __contains__(self, item: Any) -> bool:
        return item in self.members
