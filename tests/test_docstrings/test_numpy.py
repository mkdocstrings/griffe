"""Tests for the [Numpy-style parser][griffe.docstrings.numpy]."""

from __future__ import annotations

import pytest

from griffe.dataclasses import Function, Parameter, Parameters
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
from tests.test_docstrings.helpers import assert_attribute_equal, assert_element_equal, assert_parameter_equal


# =============================================================================================
# Markup flow (multilines, indentation, etc.)
def test_simple_docstring(parse_numpy):
    """Parse a simple docstring.

    Parameters:
        parse_numpy: Fixture parser.
    """
    sections, warnings = parse_numpy("A simple docstring.")
    assert len(sections) == 1
    assert not warnings


def test_multiline_docstring(parse_numpy):
    """Parse a multi-line docstring.

    Parameters:
        parse_numpy: Fixture parser.
    """
    sections, warnings = parse_numpy(
        """
        A somewhat longer docstring.

        Blablablabla.
        """
    )
    assert len(sections) == 1
    assert not warnings


def test_code_blocks(parse_numpy):
    """Parse code blocks.

    Parameters:
        parse_numpy: Fixture parser.
    """
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

    sections, warnings = parse_numpy(docstring)
    assert len(sections) == 1
    assert not warnings


def test_indented_code_block(parse_numpy):
    """Parse indented code blocks.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        This docstring contains a docstring in a code block o_O!

            \"\"\"
            This docstring is contained in another docstring O_o!

            Parameters:
                s: A string.
            \"\"\"
    """

    sections, warnings = parse_numpy(docstring)
    assert len(sections) == 1
    assert not warnings


# =============================================================================================
# Sections
def test_parameters_section(parse_numpy):
    """Parse parameters section.

    Parameters:
        parse_numpy: Fixture parser.
    """
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

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1


def test_parse_starred_parameters(parse_numpy):
    """Parse parameters names with stars in them.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Parameters
        ----------
        *a : str
        **b : int
        ***c : float
    """

    sections, warnings = parse_numpy(docstring)
    assert len(sections) == 1
    assert len(warnings) == 1


def test_other_parameters_section(parse_numpy):
    """Parse other parameters section.

    Parameters:
        parse_numpy: Fixture parser.
    """
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

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1


def test_retrieve_annotation_from_parent(parse_numpy):
    """Retrieve parameter annotation from the parent object.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Parameters
        ----------
        a
    """

    sections, _ = parse_numpy(
        docstring, parent=Function("func", parameters=Parameters(Parameter("a", annotation="str")))
    )
    assert len(sections) == 1
    assert_parameter_equal(sections[0].value[0], DocstringParameter("a", description="", annotation="str"))


def test_deprecated_section(parse_numpy):
    """Parse deprecated section.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Deprecated
        ----------
        1.23.4
            Deprecated.
            Sorry.
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1
    assert sections[0].value.version == "1.23.4"
    assert sections[0].value.description == "Deprecated.\nSorry."


def test_returns_section(parse_numpy):
    """Parse returns section.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Returns
        -------
        list of int
            A list of integers.
        flag : bool
            Some kind
            of flag.
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1
    assert_element_equal(
        sections[0].value[0], DocstringReturn(name="", annotation="list of int", description="A list of integers.")
    )
    assert_element_equal(
        sections[0].value[1], DocstringReturn(name="", annotation="bool", description="Some kind\nof flag.")
    )


def test_yields_section(parse_numpy):
    """Parse yields section.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Yields
        ------
        list of int
            A list of integers.
        flag : bool
            Some kind
            of flag.
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1
    assert_element_equal(
        sections[0].value[0], DocstringYield(name="", annotation="list of int", description="A list of integers.")
    )
    assert_element_equal(
        sections[0].value[1], DocstringYield(name="", annotation="bool", description="Some kind\nof flag.")
    )


def test_receives_section(parse_numpy):
    """Parse receives section.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Receives
        --------
        list of int
            A list of integers.
        flag : bool
            Some kind
            of flag.
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1
    assert_element_equal(
        sections[0].value[0], DocstringReceive(name="", annotation="list of int", description="A list of integers.")
    )
    assert_element_equal(
        sections[0].value[1], DocstringReceive(name="", annotation="bool", description="Some kind\nof flag.")
    )


def test_raises_section(parse_numpy):
    """Parse raises section.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Raises
        ------
        RuntimeError
            There was an issue.
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1
    assert_element_equal(
        sections[0].value[0], DocstringRaise(annotation="RuntimeError", description="There was an issue.")
    )


def test_warns_section(parse_numpy):
    """Parse warns section.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Warns
        -----
        ResourceWarning
            Heads up.
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1
    assert_element_equal(sections[0].value[0], DocstringWarn(annotation="ResourceWarning", description="Heads up."))


def test_attributes_section(parse_numpy):
    """Parse attributes section.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Attributes
        ----------
        a
            Hello.
        m
        z : int
            Bye.
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1
    assert_attribute_equal(sections[0].value[0], DocstringAttribute(name="a", annotation=None, description="Hello."))
    assert_attribute_equal(sections[0].value[1], DocstringAttribute(name="m", annotation=None, description=""))
    assert_attribute_equal(sections[0].value[2], DocstringAttribute(name="z", annotation="int", description="Bye."))


def test_examples_section(parse_numpy):
    """Parse examples section.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Examples
        --------
        Hello.

        >>> 1 + 2
        3

        ```python
        >>> print("Hello again.")
        ```

        >>> a = 0  # doctest: +SKIP
        >>> b = a + 1
        >>> print(b)
        1

        Bye.

        --------

        Not in the section.
    """

    sections, _ = parse_numpy(docstring, trim_doctest_flags=False)
    assert len(sections) == 2
    examples = sections[0]
    assert len(examples.value) == 5
    assert examples.value[0] == (DocstringSectionKind.text, "Hello.")
    assert examples.value[1] == (DocstringSectionKind.examples, ">>> 1 + 2\n3")
    assert examples.value[3][1].startswith(">>> a = 0  # doctest: +SKIP")


def test_examples_section_when_followed_by_named_section(parse_numpy):
    """Parse examples section.

    Parameters:
        parse_numpy: Parse function (fixture).
    """
    docstring = """
        Examples
        --------
        Hello, hello.

        Parameters
        ----------
        foo : int
    """

    sections, _ = parse_numpy(docstring, trim_doctest_flags=False)
    assert len(sections) == 2
    assert sections[0].kind is DocstringSectionKind.examples
    assert sections[1].kind is DocstringSectionKind.parameters


# =============================================================================================
# Annotations
def test_prefer_docstring_type_over_annotation(parse_numpy):
    """Prefer the type written in the docstring over the annotation in the parent.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Parameters
        ----------
        a : int
    """

    sections, _ = parse_numpy(
        docstring, parent=Function("func", parameters=Parameters(Parameter("a", annotation="str")))
    )
    assert len(sections) == 1
    assert_parameter_equal(sections[0].value[0], DocstringParameter("a", description="", annotation="int"))


def test_parse_complex_annotations(parse_numpy):
    """Check the type regex accepts all the necessary characters.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Parameters
        ----------
        a : typing.Tuple[str, random0123456789]
        b : int | float | None
        c : Literal['hello'] | Literal["world"]
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1
    param_a, param_b, param_c = sections[0].value
    assert param_a.name == "a"
    assert param_a.description == ""
    assert param_a.annotation == "typing.Tuple[str, random0123456789]"
    assert param_b.name == "b"
    assert param_b.description == ""
    assert param_b.annotation == "int | float | None"
    assert param_c.name == "c"
    assert param_c.description == ""
    assert param_c.annotation == "Literal['hello'] | Literal[\"world\"]"


# =============================================================================================
# Parser special features
@pytest.mark.parametrize(
    "docstring",
    [
        """
        Examples
        --------
        Base case 1. We want to skip the following test.
        >>> 1 + 1 == 3  # doctest: +SKIP
        True
        """,
        r"""
        Examples
        --------

        Base case 2. We have a blankline test.
        >>> print("a\n\nb")
        a
        <BLANKLINE>
        b
        """,
    ],
)
def test_trim_doctest_flags_basic_example(parse_numpy, docstring):
    """Correctly parse_numpy simple example docstrings when `trim_doctest_flags` option is turned on.

    Parameters:
        parse_numpy: Fixture parser.
        docstring: The docstring to parse_numpy (parametrized).
    """
    sections, warnings = parse_numpy(docstring, trim_doctest_flags=True)
    assert len(sections) == 1
    assert len(sections[0].value) == 2
    assert not warnings

    # verify that doctest flags have indeed been trimmed
    example_str = sections[0].value[1][1]
    assert "# doctest: +SKIP" not in example_str
    assert "<BLANKLINE>" not in example_str


def test_trim_doctest_flags_multi_example(parse_numpy):
    """Correctly parse_numpy multiline example docstrings when `trim_doctest_flags` option is turned on.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = r"""
    Examples
    --------

    Test multiline example blocks.
    We want to skip the following test.
    >>> 1 + 1 == 3  # doctest: +SKIP
    True

    And then a few more examples here:
    >>> print("a\n\nb")
    a
    <BLANKLINE>
    b
    >>> 1 + 1 == 2  # doctest: +SKIP
    >>> print(list(range(1, 100)))    # doctest: +ELLIPSIS
    [1, 2, ..., 98, 99]
    """
    sections, warnings = parse_numpy(docstring, trim_doctest_flags=True)
    assert len(sections) == 1
    assert len(sections[0].value) == 4
    assert not warnings

    # verify that doctest flags have indeed been trimmed
    example_str = sections[0].value[1][1]
    assert "# doctest: +SKIP" not in example_str
    example_str = sections[0].value[3][1]
    assert "<BLANKLINE>" not in example_str
    assert "\n>>> print(list(range(1, 100)))\n" in example_str
