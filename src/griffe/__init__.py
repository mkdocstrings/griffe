"""griffe package.

Signatures for entire Python programs.
Extract the structure, the frame, the skeleton of your project,
to generate API documentation or find breaking changes in your API.
"""

from __future__ import annotations

from griffe.diff import find_breaking_changes
from griffe.git import load_git
from griffe.loader import load

__all__: list[str] = ["find_breaking_changes", "load", "load_git"]
