"""Test names and expressions methods."""

from __future__ import annotations

import pytest

from griffe.docstrings.parsers import Parser
from tests.helpers import temporary_visited_module


@pytest.mark.parametrize(
    ("annotation", "items"),
    [
        ("tuple[int, float] | None", 2),
        ("None | tuple[int, float]", 2),
        ("Optional[tuple[int, float]]", 2),
        ("typing.Optional[tuple[int, float]]", 2),
    ],
)
def test_explode_return_annotations(annotation, items):
    """Check that we correctly split items from return annotations.

    Parameters:
        annotation: The return annotation.
        items: The number of items to write in the docstring returns section.
    """
    newline = "\n            "
    returns = newline.join(f"x{_}: Some value." for _ in range(items))
    code = f"""
    import typing
    from typing import Optional

    def function() -> {annotation}:
        '''This function returns either two ints or None

        Returns:
            {returns}
        '''
    """
    with temporary_visited_module(code) as module:
        sections = module["function"].docstring.parse(Parser.google)
        assert sections[1].value
