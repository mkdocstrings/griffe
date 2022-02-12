"""This extension removes the summary (first line) from the docstrings of classes' `__init__` methods."""

from __future__ import annotations

import ast

from griffe.agents.extensions.base import VisitorExtension, When
from griffe.dataclasses import Kind
from griffe.logger import get_logger

logger = get_logger(__name__)


class NoInitSummaryExtension(VisitorExtension):
    """This extension removes the summary (first line) from the docstrings of classes' `__init__` methods.

    The extension runs after each function visit, checks if the function name was `__init__`
    and if its parent is a class, and in that case modify the raw docstring of the function
    to remove its summary (the first line).
    """

    when = When.after_all

    def visit_functiondef(self, node: ast.FunctionDef) -> None:  # noqa: D102
        current = self.visitor.current
        if current.kind is Kind.CLASS and node.name == "__init__":
            init_method = current["__init__"]
            if init_method.docstring is not None:
                lines = init_method.docstring.value.split("\n")
                if lines[0] and not lines[1]:  # first line followed by empty line
                    lines = lines[2:]
                    init_method.docstring.value = "\n".join(lines)


# make it available
Extension = NoInitSummaryExtension
