"""This module stores collections of data, useful during parsing."""

from __future__ import annotations

from pathlib import Path

lines_collection: dict[Path, list[str]] = {}
"""A simple dictionary containing lines of modules.
It will probably be made more powerful later."""
