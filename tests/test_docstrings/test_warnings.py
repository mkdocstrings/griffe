"""Tests for the docstrings utility functions."""

from __future__ import annotations

from griffe.dataclasses import Docstring, Function, Parameter, ParameterKind, Parameters
from griffe.docstrings.parsers import Parser, parse


def test_can_warn_without_parent_module() -> None:
    """Assert we can parse a docstring even if it does not have a parent module."""
    function = Function(
        "func",
        parameters=Parameters(
            Parameter("param1", annotation=None, kind=ParameterKind.positional_or_keyword),  # I only changed this line
            Parameter("param2", annotation="int", kind=ParameterKind.keyword_only),
        ),
    )
    text = """
    Hello I'm a docstring!

    Parameters:
        param1: Description.
        param2: Description.
    """
    docstring = Docstring(text, lineno=1, parent=function)
    assert parse(docstring, Parser.google)
