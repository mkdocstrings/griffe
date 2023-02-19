"""Pytest fixture for docstrings tests."""

from __future__ import annotations

from typing import Iterator

import pytest

from griffe.docstrings import google, numpy, sphinx
from tests.test_docstrings.helpers import ParserType, parser


@pytest.fixture()
def parse_google() -> Iterator[ParserType]:
    """Yield a function to parse Google docstrings.

    Yields:
        A parser function.
    """
    yield from parser(google)


@pytest.fixture()
def parse_numpy() -> Iterator[ParserType]:
    """Yield a function to parse Numpy docstrings.

    Yields:
        A parser function.
    """
    yield from parser(numpy)


@pytest.fixture()
def parse_sphinx() -> Iterator[ParserType]:
    """Yield a function to parse Sphinx docstrings.

    Yields:
        A parser function.
    """
    yield from parser(sphinx)
