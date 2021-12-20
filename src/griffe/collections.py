"""This module stores collections of data, useful during parsing."""

from __future__ import annotations

import tokenize
from collections import defaultdict
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any

from griffe.mixins import GetMembersMixin, SetCollectionMembersMixin

if TYPE_CHECKING:
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

    def __bool__(self):
        return True

    # TODO: remove once Python 3.7 support is dropped
    @lru_cache(maxsize=None)
    def tokens(self, path: Path) -> tuple[list[tokenize.TokenInfo], defaultdict]:
        """Tokenize the code.

        Parameters:
            path: The filepath to get the tokens of.

        Returns:
            A token list and a mapping of tokens by line number.
        """
        readline = BytesIO("\n".join(self[path]).encode()).readline
        tokens = list(tokenize.tokenize(readline))
        token_table = defaultdict(list)  # mapping line numbers to token numbers
        for index, token in enumerate(tokens):
            token_table[token.start[0]].append(index)
        return tokens, token_table


class ModulesCollection(GetMembersMixin, SetCollectionMembersMixin):
    """A collection of modules, allowing easy access to members."""

    def __init__(self) -> None:
        """Initialize the collection."""
        self.members: dict[str, Module] = {}

    def __bool__(self):
        return True

    def __contains__(self, item: Any) -> bool:
        return item in self.members
