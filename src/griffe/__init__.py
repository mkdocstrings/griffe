"""
griffe package.

Signatures for entire Python programs.
Extract the structure, the frame, the skeleton of your project,
to generate API documentation or find breaking changes in your API.
"""

from griffe.diff import find_breaking_changes
from griffe.git import load_git
from griffe.loader import load  # noqa: WPS347

__all__ = ["find_breaking_changes", "load", "load_git"]
