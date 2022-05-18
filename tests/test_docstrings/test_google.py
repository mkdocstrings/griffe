"""Tests for the [Google-style parser][griffe.docstrings.google]."""

from __future__ import annotations

import inspect

import pytest

from griffe.dataclasses import Attribute, Class, Docstring, Function, Module, Parameter, Parameters
from griffe.docstrings.dataclasses import DocstringSectionKind
from griffe.docstrings.utils import parse_annotation
from griffe.expressions import Name


# =============================================================================================
# Markup flow (multilines, indentation, etc.)
def test_simple_docstring(parse_google):
    """Parse a simple docstring.

    Parameters:
        parse_google: Fixture parser.
    """
    sections, warnings = parse_google("A simple docstring.")
    assert len(sections) == 1
    assert not warnings


def test_multiline_docstring(parse_google):
    """Parse a multi-line docstring.

    Parameters:
        parse_google: Fixture parser.
    """
    sections, warnings = parse_google(
        """
        A somewhat longer docstring.

        Blablablabla.
        """
    )
    assert len(sections) == 1
    assert not warnings


def test_parse_partially_indented_lines(parse_google):
    """Properly handle partially indented lines.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        The available formats are:
           - JSON

        The unavailable formats are:  
           - YAML
    """  # noqa: W291
    sections, warnings = parse_google(docstring)
    assert len(sections) == 2
    assert sections[0].kind is DocstringSectionKind.admonition
    assert sections[1].kind is DocstringSectionKind.text
    assert not warnings


def test_multiple_lines_in_sections_items(parse_google):
    """Parse multi-line item description.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            p (int): This parameter
               has a description
              spawning on multiple lines.

               It even has blank lines in it.
                       Some of these lines
                   are indented for no reason.
            q (int):
              What if the first line is blank?
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 1
    assert len(sections[0].value) == 2
    assert warnings
    for warning in warnings:
        assert "should be 4 * 2 = 8 spaces, not" in warning


def test_code_blocks(parse_google):
    """Parse code blocks.

    Parameters:
        parse_google: Fixture parser.
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

    sections, warnings = parse_google(docstring)
    assert len(sections) == 1
    assert not warnings


def test_indented_code_block(parse_google):
    """Parse indented code blocks.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        This docstring contains a docstring in a code block o_O!

            \"\"\"
            This docstring is contained in another docstring O_o!

            Parameters:
                s: A string.
            \"\"\"
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 1
    assert not warnings


def test_different_indentation(parse_google):
    """Parse different indentations, warn on confusing indentation.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Raises:
             StartAt5: this section's items starts with 5 spaces of indentation.
                  Well indented continuation line.
              Badly indented continuation line (will trigger a warning).

                      Empty lines are preserved, as well as extra-indentation (this line is a code block).
             AnyOtherLine: ...starting with exactly 5 spaces is a new item.
            AnyLine: ...indented with less than 5 spaces signifies the end of the section.
        """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 2
    assert len(sections[0].value) == 2
    assert sections[0].value[0].description == (
        "this section's items starts with 5 spaces of indentation.\n"
        "Well indented continuation line.\n"
        "Badly indented continuation line (will trigger a warning).\n"
        "\n"
        "    Empty lines are preserved, as well as extra-indentation (this line is a code block)."
    )
    assert sections[1].value == "    AnyLine: ...indented with less than 5 spaces signifies the end of the section."
    assert len(warnings) == 1
    assert "should be 5 * 2 = 10 spaces, not 6" in warnings[0]


# =============================================================================================
# Annotations (general)
def test_parse_without_parent(parse_google):
    """Parse a docstring without a parent function.

    Parameters:
        parse_google: Fixture parser.
    """
    sections, warnings = parse_google(
        """
        Parameters:
            void: SEGFAULT.
            niet: SEGFAULT.
            nada: SEGFAULT.
            rien: SEGFAULT.

        Keyword Args:
            keywd: SEGFAULT.

        Exceptions:
            GlobalError: when nothing works as expected.

        Returns:
            Itself.
        """
    )

    assert len(sections) == 4
    assert len(warnings) == 6  # missing annotations for parameters and return
    for warning in warnings[:-1]:
        assert "parameter" in warning
    assert "return" in warnings[-1]


def test_parse_without_annotations(parse_google):
    """Parse a function docstring without signature annotations.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            x: X value.

        Keyword Args:
            y: Y value.

        Returns:
            Sum X + Y + Z.
    """

    sections, warnings = parse_google(
        docstring,
        parent=Function(
            "func",
            parameters=Parameters(
                Parameter("x"),
                Parameter("y"),
            ),
        ),
    )
    assert len(sections) == 3
    assert len(warnings) == 3
    for warning in warnings[:-1]:
        assert "parameter" in warning
    assert "return" in warnings[-1]


def test_parse_with_annotations(parse_google):
    """Parse a function docstring with signature annotations.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            x: X value.

        Keyword Parameters:
            y: Y value.

        Returns:
            Sum X + Y.
    """

    sections, warnings = parse_google(
        docstring,
        parent=Function(
            "func",
            parameters=Parameters(
                Parameter("x", annotation="int"),
                Parameter("y", annotation="int"),
            ),
            returns="int",
        ),
    )
    assert len(sections) == 3
    assert not warnings


# =============================================================================================
# Sections (general)
def test_parse_attributes_section(parse_google):
    """Parse Attributes sections.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Attributes:
            hey: Hey.
            ho: Ho.
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 1
    assert not warnings


def test_parse_examples_sections(parse_google):
    """Parse a function docstring with examples.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Examples:
            Some examples that will create a unified code block:

            >>> 2 + 2 == 5
            False
            >>> print("examples")
            "examples"

            This is just a random comment in the examples section.

            These examples will generate two different code blocks. Note the blank line.

            >>> print("I'm in the first code block!")
            "I'm in the first code block!"

            >>> print("I'm in other code block!")
            "I'm in other code block!"

            We also can write multiline examples:

            >>> x = 3 + 2  # doctest: +SKIP
            >>> y = x + 10
            >>> y
            15

            This is just a typical Python code block:

            ```python
            print("examples")
            return 2 + 2
            ```

            Even if it contains doctests, the following block is still considered a normal code-block.

            ```python
            >>> print("examples")
            "examples"
            >>> 2 + 2
            4
            ```

            The blank line before an example is optional.
            >>> x = 3
            >>> y = "apple"
            >>> z = False
            >>> l = [x, y, z]
            >>> my_print_list_function(l)
            3
            "apple"
            False
        """

    sections, warnings = parse_google(
        docstring,
        parent=Function(
            "func",
            parameters=Parameters(
                Parameter("x", annotation="int"),
                Parameter("y", annotation="int"),
            ),
            returns="int",
        ),
        trim_doctest_flags=False,
    )
    assert len(sections) == 1
    examples = sections[0]
    assert len(examples.value) == 9
    assert examples.value[6][1].startswith(">>> x = 3 + 2  # doctest: +SKIP")
    assert not warnings


def test_parse_yields_section(parse_google):
    """Parse Yields section.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Yields:
            x: Floats.
            (int): Integers.
            y (int): Same.
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 1
    annotated = sections[0].value[0]
    assert annotated.name == "x"
    assert annotated.annotation is None
    assert annotated.description == "Floats."
    annotated = sections[0].value[1]
    assert annotated.name == ""
    assert annotated.annotation == "int"
    assert annotated.description == "Integers."
    annotated = sections[0].value[2]
    assert annotated.name == "y"
    assert annotated.annotation == "int"
    assert annotated.description == "Same."
    assert len(warnings) == 1
    assert "'x'" in warnings[0]


def test_invalid_sections(parse_google):
    """Warn on invalid (empty) sections.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
        Exceptions:
        Exceptions:

        Returns:
        Note:

        Important:
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 1
    for warning in warnings[:3]:
        assert "Empty" in warning
    assert "Empty returns section at line" in warnings[3]
    assert "Empty" in warnings[-1]


def test_close_sections(parse_google):
    """Parse sections without blank lines in between.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            x: X.
        Parameters:
            y: Y.

        Parameters:
            z: Z.
        Exceptions:
            Error2: error.
        Exceptions:
            Error1: error.
        Returns:
            1.
        Returns:
            2.
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 7
    assert len(warnings) == 5  # no type or annotations


# =============================================================================================
# Parameters sections
def test_parse_args_and_kwargs(parse_google):
    """Parse args and kwargs.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            a (str): a parameter.
            *args (str): args parameters.
            **kwargs (str): kwargs parameters.
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 1
    expected_parameters = {"a": "a parameter.", "*args": "args parameters.", "**kwargs": "kwargs parameters."}
    for parameter in sections[0].value:
        assert parameter.name in expected_parameters
        assert expected_parameters[parameter.name] == parameter.description
    assert not warnings


def test_parse_args_kwargs_keyword_only(parse_google):
    """Parse args and kwargs.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            a (str): a parameter.
            *args (str): args parameters.

        Keyword Args:
            **kwargs (str): kwargs parameters.
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 2
    expected_parameters = {"a": "a parameter.", "*args": "args parameters."}
    for parameter in sections[0].value:
        assert parameter.name in expected_parameters
        assert expected_parameters[parameter.name] == parameter.description

    expected_parameters = {"**kwargs": "kwargs parameters."}
    for kwarg in sections[1].value:
        assert kwarg.name in expected_parameters
        assert expected_parameters[kwarg.name] == kwarg.description

    assert not warnings


def test_parse_types_in_docstring(parse_google):
    """Parse types in docstring.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            x (int): X value.

        Keyword Args:
            y (int): Y value.

        Returns:
            s (int): Sum X + Y + Z.
    """

    sections, warnings = parse_google(
        docstring,
        parent=Function(
            "func",
            parameters=Parameters(
                Parameter("x"),
                Parameter("y"),
            ),
        ),
    )
    assert len(sections) == 3
    assert not warnings

    assert sections[0].kind is DocstringSectionKind.parameters
    assert sections[1].kind is DocstringSectionKind.other_parameters
    assert sections[2].kind is DocstringSectionKind.returns

    (argx,) = sections[0].value  # noqa: WPS460
    (argy,) = sections[1].value  # noqa: WPS460
    (returns,) = sections[2].value  # noqa: WPS460

    assert argx.name == "x"
    assert argx.annotation.source == "int"
    assert argx.annotation.full == "int"
    assert argx.description == "X value."
    assert argx.value is None

    assert argy.name == "y"
    assert argy.annotation.source == "int"
    assert argy.annotation.full == "int"
    assert argy.description == "Y value."
    assert argy.value is None

    assert returns.annotation.source == "int"
    assert returns.annotation.full == "int"
    assert returns.description == "Sum X + Y + Z."


def test_parse_optional_type_in_docstring(parse_google):
    """Parse optional types in docstring.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            x (int): X value.
            y (int, optional): Y value.

        Keyword Args:
            z (int, optional): Z value.
    """

    sections, warnings = parse_google(
        docstring,
        parent=Function(
            "func",
            parameters=Parameters(
                Parameter("x", default="1"),
                Parameter("y", default="None"),
                Parameter("z", default="None"),
            ),
        ),
    )
    assert len(sections) == 2
    assert not warnings

    assert sections[0].kind is DocstringSectionKind.parameters
    assert sections[1].kind is DocstringSectionKind.other_parameters

    argx, argy = sections[0].value
    (argz,) = sections[1].value  # noqa: WPS460

    assert argx.name == "x"
    assert argx.annotation.source == "int"
    assert argx.annotation.full == "int"
    assert argx.description == "X value."
    assert argx.value == "1"

    assert argy.name == "y"
    assert argy.annotation.source == "int"
    assert argy.annotation.full == "int"
    assert argy.description == "Y value."
    assert argy.value == "None"

    assert argz.name == "z"
    assert argz.annotation.source == "int"
    assert argz.annotation.full == "int"
    assert argz.description == "Z value."
    assert argz.value == "None"


def test_prefer_docstring_types_over_annotations(parse_google):
    """Prefer the docstring type over the annotation.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            x (str): X value.

        Keyword Args:
            y (str): Y value.

        Returns:
            (str): Sum X + Y + Z.
    """

    sections, warnings = parse_google(
        docstring,
        parent=Function(
            "func",
            parameters=Parameters(
                Parameter("x", annotation="int"),
                Parameter("y", annotation="int"),
            ),
            returns="int",
        ),
    )
    assert len(sections) == 3
    assert not warnings

    assert sections[0].kind is DocstringSectionKind.parameters
    assert sections[1].kind is DocstringSectionKind.other_parameters
    assert sections[2].kind is DocstringSectionKind.returns

    (argx,) = sections[0].value  # noqa: WPS460
    (argy,) = sections[1].value  # noqa: WPS460
    (returns,) = sections[2].value  # noqa: WPS460

    assert argx.name == "x"
    assert argx.annotation.source == "str"
    assert argx.annotation.full == "str"
    assert argx.description == "X value."

    assert argy.name == "y"
    assert argy.annotation.source == "str"
    assert argy.annotation.full == "str"
    assert argy.description == "Y value."

    assert returns.annotation.source == "str"
    assert returns.annotation.full == "str"
    assert returns.description == "Sum X + Y + Z."


def test_parameter_line_without_colon(parse_google):
    """Warn when missing colon.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            x is an integer.
    """

    sections, warnings = parse_google(docstring)
    assert not sections  # getting x fails, so the section is empty and discarded
    assert len(warnings) == 2
    assert "pair" in warnings[0]
    assert "Empty" in warnings[1]


def test_parameter_line_without_colon_keyword_only(parse_google):
    """Warn when missing colon.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Keyword Args:
            x is an integer.
    """

    sections, warnings = parse_google(docstring)
    assert not sections  # getting x fails, so the section is empty and discarded
    assert len(warnings) == 2
    assert "pair" in warnings[0]
    assert "Empty" in warnings[1]


def test_warn_about_unknown_parameters(parse_google):
    """Warn about unknown parameters in "Parameters" sections.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            x (int): Integer.
            y (int): Integer.
    """

    _, warnings = parse_google(
        docstring,
        parent=Function(
            "func",
            parameters=Parameters(
                Parameter("a"),
                Parameter("y"),
            ),
        ),
    )
    assert len(warnings) == 1
    assert "'x' does not appear in the function signature" in warnings[0]


def test_never_warn_about_unknown_other_parameters(parse_google):
    """Never warn about unknown parameters in "Other parameters" sections.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Other Parameters:
            x (int): Integer.
            z (int): Integer.
    """

    _, warnings = parse_google(
        docstring,
        parent=Function(
            "func",
            parameters=Parameters(
                Parameter("a"),
                Parameter("y"),
            ),
        ),
    )
    assert not warnings


def test_unknown_params_scan_doesnt_crash_without_parameters(parse_google):
    """Assert we don't crash when parsing parameters sections and parent object does not have parameters.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            this (str): This.
            that (str): That.
    """

    _, warnings = parse_google(docstring, parent=Module("mod"))
    assert not warnings


def test_class_uses_init_parameters(parse_google):
    """Assert we use the `__init__` parameters when parsing classes' parameters sections.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            x: X value.
    """
    parent = Class("c")
    parent["__init__"] = Function("__init__", parameters=Parameters(Parameter("x", annotation="int")))
    sections, warnings = parse_google(docstring, parent=parent)
    assert not warnings
    argx = sections[0].value[0]
    assert argx.name == "x"
    assert argx.annotation == "int"
    assert argx.description == "X value."


def test_dataclass_uses_attributes(parse_google):
    """Assert we use the class' attributes as parameters when parsing dataclasses' parameters sections.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            auth: Auth method.
            base_url: Base URL.
    """
    parent = Class("c")
    parent.labels.add("dataclass")
    parent["auth"] = Attribute("auth", annotation="Optional[str]", value="None")
    parent["base_url"] = Attribute("base_url", annotation="str", value="'https://api.example.com'")
    sections, warnings = parse_google(docstring, parent=parent)
    assert not warnings
    auth, base_url = sections[0].value
    assert auth.name == "auth"
    assert auth.annotation == "Optional[str]"
    assert auth.description == "Auth method."
    assert auth.default == "None"
    assert base_url.name == "base_url"
    assert base_url.annotation == "str"
    assert base_url.description == "Base URL."
    assert base_url.default == "'https://api.example.com'"


# TODO: possible feature
# def test_missing_parameter(parse_google):
#     """Warn on missing parameter in docstring.
#
#     Parameters:
#         parse_google: Fixture parser.
#     """
#     docstring = """
#         Parameters:
#             x: Integer.
#     """

#     sections, warnings = parse_google(docstring)
#     assert len(sections) == 1
#     assert not warnings


# =============================================================================================
# Attributes sections
def test_retrieve_attributes_annotation_from_parent(parse_google):
    """Retrieve the annotations of attributes from the parent object.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Summary.

        Attributes:
            a: Whatever.
            b: Whatever.
    """
    parent = Class("cls")
    parent["a"] = Attribute("a", annotation=Name("int", "int"))
    parent["b"] = Attribute("b", annotation=Name("str", "str"))
    sections, _ = parse_google(docstring, parent=parent)
    attributes = sections[1].value
    assert attributes[0].name == "a"
    assert attributes[0].annotation.source == "int"
    assert attributes[1].name == "b"
    assert attributes[1].annotation.source == "str"


# =============================================================================================
# Yields sections
def test_parse_yields_section_with_return_annotation(parse_google):
    """Parse Yields section with a return annotation in the parent function.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Yields:
            Integers.
    """

    function = Function("func", returns="Iterator[int]")
    sections, warnings = parse_google(docstring, function)
    assert len(sections) == 1
    annotated = sections[0].value[0]
    assert annotated.annotation == "Iterator[int]"
    assert annotated.description == "Integers."
    assert not warnings


@pytest.mark.parametrize(
    "return_annotation",
    [
        "Iterator[tuple[int, float]]",
        "Generator[tuple[int, float], ..., ...]",
    ],
)
def test_parse_yields_tuple_in_iterator_or_generator(parse_google, return_annotation):
    """Parse Yields annotations in Iterator or Generator types.

    Parameters:
        parse_google: Fixture parser.
        return_annotation: Parametrized return annotation as a string.
    """
    docstring = """
        Summary.

        Yields:
            a: Whatever.
            b: Whatever.
    """
    sections, _ = parse_google(
        docstring,
        parent=Function(
            "func",
            returns=parse_annotation(return_annotation, Docstring("d", parent=Function("f"))),
        ),
    )
    yields = sections[1].value
    assert yields[0].name == "a"
    assert yields[0].annotation.source == "int"
    assert yields[1].name == "b"
    assert yields[1].annotation.source == "float"


# =============================================================================================
# Receives sections
def test_parse_receives_tuple_in_generator(parse_google):
    """Parse Receives annotations in Generator type.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Summary.

        Receives:
            a: Whatever.
            b: Whatever.
    """
    sections, _ = parse_google(
        docstring,
        parent=Function(
            "func",
            returns=parse_annotation("Generator[..., tuple[int, float], ...]", Docstring("d", parent=Function("f"))),
        ),
    )
    receives = sections[1].value
    assert receives[0].name == "a"
    assert receives[0].annotation.source == "int"
    assert receives[1].name == "b"
    assert receives[1].annotation.source == "float"


# =============================================================================================
# Returns sections
def test_parse_returns_tuple_in_generator(parse_google):
    """Parse Returns annotations in Generator type.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Summary.

        Returns:
            a: Whatever.
            b: Whatever.
    """
    sections, _ = parse_google(
        docstring,
        parent=Function(
            "func",
            returns=parse_annotation("Generator[..., ..., tuple[int, float]]", Docstring("d", parent=Function("f"))),
        ),
    )
    returns = sections[1].value
    assert returns[0].name == "a"
    assert returns[0].annotation.source == "int"
    assert returns[1].name == "b"
    assert returns[1].annotation.source == "float"


# =============================================================================================
# Parser special features
def test_parse_admonitions(parse_google):
    """Parse admonitions.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Important note:
            Hello.

        Note: With title.
            Hello again.

        Something:
            Something.
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 3
    assert not warnings
    assert sections[0].title == "Important note"
    assert sections[0].value.kind == "important-note"
    assert sections[0].value.contents == "Hello."
    assert sections[1].title == "With title."
    assert sections[1].value.kind == "note"
    assert sections[1].value.contents == "Hello again."
    assert sections[2].title == "Something"
    assert sections[2].value.kind == "something"
    assert sections[2].value.contents == "Something."


@pytest.mark.parametrize(
    "docstring",
    [
        """
        ******************************
        This looks like an admonition:
        ******************************
        """,
        """
        Warning: this line also looks
        like an admonition.
        """,
        """
        Matching but not an admonition:



        - Multiple empty lines above.
        """,
        """Last line:""",
    ],
)
def test_handle_false_admonitions_correctly(parse_google, docstring):
    """Correctly handle lines that look like admonitions.

    Parameters:
        parse_google: Fixture parser.
        docstring: The docstring to parse (parametrized).
    """
    sections, warnings = parse_google(docstring)
    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.text
    assert len(sections[0].value.splitlines()) == len(inspect.cleandoc(docstring).splitlines())
    assert not warnings


def test_dont_insert_admonition_before_current_section(parse_google):
    """Check that admonitions are inserted at the right place.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Summary.

        Short description.

        Info:
            Something useful.
    """
    sections, _ = parse_google(docstring)
    assert len(sections) == 2
    assert sections[0].kind is DocstringSectionKind.text
    assert sections[1].kind is DocstringSectionKind.admonition


@pytest.mark.parametrize(
    "docstring",
    [
        "",
        "\n",
        "\n\n",
        "Summary.",
        "Summary.\n\n\n",
        "Summary.\n\nParagraph.",
        "Summary\non two lines.",
        "Summary\non two lines.\n\nParagraph.",
    ],
)
def test_ignore_init_summary(parse_google, docstring):
    """Correctly ignore summary in `__init__` methods' docstrings.

    Parameters:
        parse_google: Fixture parser.
        docstring: The docstring to parse_google (parametrized).
    """
    sections, _ = parse_google(docstring, parent=Function("__init__", parent=Class("C")), ignore_init_summary=True)
    for section in sections:
        assert "Summary" not in section.value

    if docstring.strip():
        sections, _ = parse_google(docstring, parent=Function("__init__", parent=Module("M")), ignore_init_summary=True)
        assert "Summary" in sections[0].value
        sections, _ = parse_google(docstring, parent=Function("f", parent=Class("C")), ignore_init_summary=True)
        assert "Summary" in sections[0].value
        sections, _ = parse_google(docstring, ignore_init_summary=True)
        assert "Summary" in sections[0].value


@pytest.mark.parametrize(
    "docstring",
    [
        """
        Examples:
            Base case 1. We want to skip the following test.
            >>> 1 + 1 == 3  # doctest: +SKIP
            True
        """,
        r"""
        Examples:

            Base case 2. We have a blankline test.
            >>> print("a\n\nb")
            a
            <BLANKLINE>
            b
        """,
    ],
)
def test_trim_doctest_flags_basic_example(parse_google, docstring):
    """Correctly parse simple example docstrings when `trim_doctest_flags` option is turned on.

    Parameters:
        parse_google: Fixture parser.
        docstring: The docstring to parse (parametrized).
    """
    sections, warnings = parse_google(docstring, trim_doctest_flags=True)
    assert len(sections) == 1
    assert len(sections[0].value) == 2
    assert not warnings

    # verify that doctest flags have indeed been trimmed
    example_str = sections[0].value[1][1]
    assert "# doctest: +SKIP" not in example_str
    assert "<BLANKLINE>" not in example_str


def test_trim_doctest_flags_multi_example(parse_google):
    """Correctly parse multiline example docstrings when `trim_doctest_flags` option is turned on.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = r"""
    Examples:

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
    sections, warnings = parse_google(docstring, trim_doctest_flags=True)
    assert len(sections) == 1
    assert len(sections[0].value) == 4
    assert not warnings

    # verify that doctest flags have indeed been trimmed
    example_str = sections[0].value[1][1]
    assert "# doctest: +SKIP" not in example_str
    example_str = sections[0].value[3][1]
    assert "<BLANKLINE>" not in example_str
    assert "\n>>> print(list(range(1, 100)))\n" in example_str


def test_single_line_with_trailing_whitespace(parse_google):
    """Don't crash on single line docstrings with trailing whitespace.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = "a: b\n    "
    sections, warnings = parse_google(docstring, trim_doctest_flags=True)
    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.text
    assert not warnings
