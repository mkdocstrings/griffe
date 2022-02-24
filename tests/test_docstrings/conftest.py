"""Pytest fixture for docstrings tests."""

import pytest

from griffe.docstrings import google, numpy, sphinx
from tests.test_docstrings.helpers import parser


@pytest.fixture()
def parse_google():
    """Yield a function to parse Google docstrings.

    Yields:
        A parser function.
    """
    yield from parser(google)


@pytest.fixture()
def parse_numpy():
    """Yield a function to parse Numpy docstrings.

    Yields:
        A parser function.
    """
    yield from parser(numpy)


@pytest.fixture()
def parse_sphinx():
    """Yield a function to parse Sphinx docstrings.

    Yields:
        A parser function.
    """
    yield from parser(sphinx)
