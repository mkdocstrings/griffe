"""Tests for the [Numpy-style parser][griffe.docstrings.numpy]."""

from __future__ import annotations

from griffe.dataclasses import Function, Parameter, Parameters
from griffe.docstrings import numpy
from griffe.docstrings.dataclasses import (
    DocstringAttribute,
    DocstringParameter,
    DocstringRaise,
    DocstringReceive,
    DocstringReturn,
    DocstringSectionKind,
    DocstringWarn,
    DocstringYield,
)
from tests.test_docstrings.helpers import assert_attribute_equal, assert_element_equal, assert_parameter_equal, parser

parse = parser(numpy)


# =============================================================================================
# Markup flow (multilines, indentation, etc.)
def test_simple_docstring():
    """Parse a simple docstring."""
    sections, warnings = parse("A simple docstring.")
    assert len(sections) == 1
    assert not warnings


def test_multiline_docstring():
    """Parse a multi-line docstring."""
    sections, warnings = parse(
        """
        A somewhat longer docstring.

        Blablablabla.
        """
    )
    assert len(sections) == 1
    assert not warnings


def test_code_blocks():
    """Parse code blocks."""
    docstring = """
        This docstring contains a docstring in a code block o_O!

        ```python
        \"\"\"
        This docstring is contained in another docstring O_o!

        Parameters:
            s: A string.
        \"\"\"
        ```
    """

    sections, warnings = parse(docstring)
    assert len(sections) == 1
    assert not warnings


def test_indented_code_block():
    """Parse indented code blocks."""
    docstring = """
        This docstring contains a docstring in a code block o_O!

            \"\"\"
            This docstring is contained in another docstring O_o!

            Parameters:
                s: A string.
            \"\"\"
    """

    sections, warnings = parse(docstring)
    assert len(sections) == 1
    assert not warnings


def test_parameters_section():
    """Parse parameters section."""
    docstring = """
        Parameters
        ----------
        a
        b : int
        c : str, optional
        d : float, default=1.0
        e, f
        g, h : bytes, optional, default=b''
        i : {0, 1, 2}
        j : {"a", 1, None, True}
        k
            K's description.
    """

    sections, _ = parse(docstring)
    assert len(sections) == 1


def test_other_parameters_section():
    """Parse other parameters section."""
    docstring = """
        Other Parameters
        ----------------
        a
        b : int
        c : str, optional
        d : float, default=1.0
        e, f
        g, h : bytes, optional, default=b''
        i : {0, 1, 2}
        j : {"a", 1, None, True}
        k
            K's description.
    """

    sections, _ = parse(docstring)
    assert len(sections) == 1


def test_retrieve_annotation_from_parent():
    """Retrieve parameter annotation from the parent object."""
    docstring = """
        Parameters
        ----------
        a
    """

    sections, _ = parse(docstring, parent=Function("func", parameters=Parameters(Parameter("a", annotation="str"))))
    assert len(sections) == 1
    assert_parameter_equal(sections[0].value[0], DocstringParameter("a", description="", annotation="str"))


def test_prefer_docstring_type_over_annotation():
    """Prefer the type written in the docstring over the annotation in the parent."""
    docstring = """
        Parameters
        ----------
        a : int
    """

    sections, _ = parse(docstring, parent=Function("func", parameters=Parameters(Parameter("a", annotation="str"))))
    assert len(sections) == 1
    assert_parameter_equal(sections[0].value[0], DocstringParameter("a", description="", annotation="int"))


def test_deprecated_section():
    """Parse deprecated section."""
    docstring = """
        Deprecated
        ----------
        1.23.4
            Deprecated.
            Sorry.
    """

    sections, _ = parse(docstring)
    assert len(sections) == 1
    assert sections[0].value[0] == "1.23.4"
    assert sections[0].value[1] == "Deprecated.\nSorry."


def test_returns_section():
    """Parse returns section."""
    docstring = """
        Returns
        -------
        list of int
            A list of integers.
        flag : bool
            Some kind
            of flag.
    """

    sections, _ = parse(docstring)
    assert len(sections) == 1
    assert_element_equal(
        sections[0].value[0], DocstringReturn(name="", annotation="list of int", description="A list of integers.")
    )
    assert_element_equal(
        sections[0].value[1], DocstringReturn(name="", annotation="bool", description="Some kind\nof flag.")
    )


def test_yields_section():
    """Parse yields section."""
    docstring = """
        Yields
        ------
        list of int
            A list of integers.
        flag : bool
            Some kind
            of flag.
    """

    sections, _ = parse(docstring)
    assert len(sections) == 1
    assert_element_equal(
        sections[0].value[0], DocstringYield(name="", annotation="list of int", description="A list of integers.")
    )
    assert_element_equal(
        sections[0].value[1], DocstringYield(name="", annotation="bool", description="Some kind\nof flag.")
    )


def test_receives_section():
    """Parse receives section."""
    docstring = """
        Receives
        --------
        list of int
            A list of integers.
        flag : bool
            Some kind
            of flag.
    """

    sections, _ = parse(docstring)
    assert len(sections) == 1
    assert_element_equal(
        sections[0].value[0], DocstringReceive(name="", annotation="list of int", description="A list of integers.")
    )
    assert_element_equal(
        sections[0].value[1], DocstringReceive(name="", annotation="bool", description="Some kind\nof flag.")
    )


def test_raises_section():
    """Parse raises section."""
    docstring = """
        Raises
        ------
        RuntimeError
            There was an issue.
    """

    sections, _ = parse(docstring)
    assert len(sections) == 1
    assert_element_equal(
        sections[0].value[0], DocstringRaise(annotation="RuntimeError", description="There was an issue.")
    )


def test_warns_section():
    """Parse warns section."""
    docstring = """
        Warns
        -----
        ResourceWarning
            Heads up.
    """

    sections, _ = parse(docstring)
    assert len(sections) == 1
    assert_element_equal(sections[0].value[0], DocstringWarn(annotation="ResourceWarning", description="Heads up."))


def test_attributes_section():
    """Parse attributes section."""
    docstring = """
        Attributes
        ----------
        a
            Hello.
        m
        z : int
            Bye.
    """

    sections, _ = parse(docstring)
    assert len(sections) == 1
    assert_attribute_equal(sections[0].value[0], DocstringAttribute(name="a", annotation=None, description="Hello."))
    assert_attribute_equal(sections[0].value[1], DocstringAttribute(name="m", annotation=None, description=""))
    assert_attribute_equal(sections[0].value[2], DocstringAttribute(name="z", annotation="int", description="Bye."))


def test_examples_section():
    """Parse examples section."""
    docstring = """
        Examples
        --------
        Hello.

        >>> 1 + 2
        3

        ```python
        >>> print("Hello again.")
        ```

        >>> a = 0
        >>> b = a + 1
        >>> print(b)
        1

        Bye.

        --------

        Not in the section.
    """

    sections, _ = parse(docstring)
    assert len(sections) == 2
    examples = sections[0]
    assert len(examples.value) == 5
    assert examples.value[0] == (DocstringSectionKind.text, "Hello.")
    assert examples.value[1] == (DocstringSectionKind.examples, ">>> 1 + 2\n3")
