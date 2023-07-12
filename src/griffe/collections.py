"""This module stores collections of data, useful during parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ItemsView, KeysView, ValuesView

from griffe.mixins import GetMembersMixin, SetMembersMixin

if TYPE_CHECKING:
    from pathlib import Path

    from griffe.dataclasses import Module


class LinesCollection:
    """A simple dictionary containing the modules source code lines."""

    def __init__(self) -> None:
        """Initialize the collection."""
        self._data: dict[Path, list[str]] = {}

    def __getitem__(self, key: Path) -> list[str]:
        return self._data[key]

    def __setitem__(self, key: Path, value: list[str]) -> None:
        self._data[key] = value

    def __bool__(self) -> bool:
        return True

    def keys(self) -> KeysView:
        """Return the collection keys.

        Returns:
            The collection keys.
        """
        return self._data.keys()

    def values(self) -> ValuesView:
        """Return the collection values.

        Returns:
            The collection values.
        """
        return self._data.values()

    def items(self) -> ItemsView:
        """Return the collection items.

        Returns:
            The collection items.
        """
        return self._data.items()


class ModulesCollection(GetMembersMixin, SetMembersMixin):
    """A collection of modules, allowing easy access to members."""

    is_collection = True

    def __init__(self) -> None:
        """Initialize the collection."""
        self.members: dict[str, Module] = {}

    def __bool__(self) -> bool:
        return True

    def __contains__(self, item: Any) -> bool:
        return item in self.members

    @property
    def all_members(self) -> dict[str, Module]:  # noqa: D102
        return self.members


__all__ = ["LinesCollection", "ModulesCollection"]
