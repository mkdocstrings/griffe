"""Tests for the [Google-style parser][griffe.docstrings.google]."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

import pytest

from griffe.dataclasses import Attribute, Class, Docstring, Function, Module, Parameter, Parameters
from griffe.docstrings.dataclasses import DocstringReturn, DocstringSectionKind
from griffe.docstrings.utils import parse_annotation
from griffe.expressions import ExprName

if TYPE_CHECKING:
    from tests.test_docstrings.helpers import ParserType


# =============================================================================================
# Markup flow (multilines, indentation, etc.)
def test_simple_docstring(parse_google: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_google: Fixture parser.
    """
    sections, warnings = parse_google("A simple docstring.")
    assert len(sections) == 1
    assert not warnings


def test_multiline_docstring(parse_google: ParserType) -> None:
    """Parse a multi-line docstring.

    Parameters:
        parse_google: Fixture parser.
    """
    sections, warnings = parse_google(
        """
        A somewhat longer docstring.

        Blablablabla.
        """,
    )
    assert len(sections) == 1
    assert not warnings


def test_parse_partially_indented_lines(parse_google: ParserType) -> None:
    """Properly handle partially indented lines.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        The available formats are:
           - JSON

        The unavailable formats are:
           - YAML
    """
    sections, warnings = parse_google(docstring)
    assert len(sections) == 2
    assert sections[0].kind is DocstringSectionKind.admonition
    assert sections[1].kind is DocstringSectionKind.admonition
    assert not warnings


def test_multiple_lines_in_sections_items(parse_google: ParserType) -> None:
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


def test_code_blocks(parse_google: ParserType) -> None:
    """Parse code blocks.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        This docstring contains a code block!

        ```python
        print("hello")
        ```
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 1
    assert not warnings


def test_indented_code_block(parse_google: ParserType) -> None:
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


def test_different_indentation(parse_google: ParserType) -> None:
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


def test_empty_indented_lines_in_section_with_items(parse_google: ParserType) -> None:
    """In sections with items, don't treat lines with just indentation as items.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = "Returns:\n    only_item: Description.\n    \n    \n\nSomething."
    sections, _ = parse_google(docstring)
    assert len(sections) == 2
    assert len(sections[0].value) == 1


@pytest.mark.parametrize(
    "section",
    [
        "Attributes",
        "Other Parameters",
        "Parameters",
        "Raises",
        "Receives",
        "Returns",
        "Warns",
        "Yields",
    ],
)
def test_starting_item_description_on_new_line(parse_google: ParserType, section: str) -> None:
    """In sections with items, allow starting item descriptions on a new (indented) line.

    Parameters:
        parse_google: Fixture parser.
        section: A parametrized section name.
    """
    docstring = f"\n{section}:\n    only_item:\n        Description."
    sections, _ = parse_google(docstring)
    assert len(sections) == 1
    assert len(sections[0].value) == 1
    assert sections[0].value[0].description.strip() == "Description."


# =============================================================================================
# Annotations
def test_parse_without_parent(parse_google: ParserType) -> None:
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
        """,
    )

    assert len(sections) == 4
    assert len(warnings) == 6  # missing annotations for parameters and return
    for warning in warnings[:-1]:
        assert "parameter" in warning
    assert "return" in warnings[-1]


def test_parse_without_annotations(parse_google: ParserType) -> None:
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


def test_parse_with_annotations(parse_google: ParserType) -> None:
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
# Sections
def test_parse_attributes_section(parse_google: ParserType) -> None:
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


def test_parse_functions_section(parse_google: ParserType) -> None:
    """Parse Functions/Methods sections.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Functions:
            f(a, b=2): Hello.
            g: Hi.

        Methods:
            f(a, b=2): Hello.
            g: Hi.
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 2
    for section in sections:
        assert section.kind is DocstringSectionKind.functions
        func_f = section.value[0]
        assert func_f.name == "f"
        assert func_f.signature == "f(a, b=2)"
        assert func_f.description == "Hello."
        func_g = section.value[1]
        assert func_g.name == "g"
        assert func_g.signature is None
        assert func_g.description == "Hi."
    assert not warnings


def test_parse_classes_section(parse_google: ParserType) -> None:
    """Parse Classes sections.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Classes:
            C(a, b=2): Hello.
            D: Hi.
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.classes
    class_c = sections[0].value[0]
    assert class_c.name == "C"
    assert class_c.signature == "C(a, b=2)"
    assert class_c.description == "Hello."
    class_d = sections[0].value[1]
    assert class_d.name == "D"
    assert class_d.signature is None
    assert class_d.description == "Hi."
    assert not warnings


def test_parse_modules_section(parse_google: ParserType) -> None:
    """Parse Modules sections.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Modules:
            m: Hello.
            n: Hi.
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.modules
    module_m = sections[0].value[0]
    assert module_m.name == "m"
    assert module_m.description == "Hello."
    module_n = sections[0].value[1]
    assert module_n.name == "n"
    assert module_n.description == "Hi."
    assert not warnings


def test_parse_examples_sections(parse_google: ParserType) -> None:
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

            ```pycon
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


def test_parse_yields_section(parse_google: ParserType) -> None:
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


def test_invalid_sections(parse_google: ParserType) -> None:
    """Warn on invalid sections.

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
    assert not warnings


# =============================================================================================
# Parameters sections
def test_parse_args_and_kwargs(parse_google: ParserType) -> None:
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


def test_parse_args_kwargs_keyword_only(parse_google: ParserType) -> None:
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


def test_parse_types_in_docstring(parse_google: ParserType) -> None:
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

    (argx,) = sections[0].value
    (argy,) = sections[1].value
    (returns,) = sections[2].value

    assert argx.name == "x"
    assert argx.annotation.name == "int"
    assert argx.annotation.canonical_path == "int"
    assert argx.description == "X value."
    assert argx.value is None

    assert argy.name == "y"
    assert argy.annotation.name == "int"
    assert argy.annotation.canonical_path == "int"
    assert argy.description == "Y value."
    assert argy.value is None

    assert returns.annotation.name == "int"
    assert returns.annotation.canonical_path == "int"
    assert returns.description == "Sum X + Y + Z."


def test_parse_optional_type_in_docstring(parse_google: ParserType) -> None:
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
    (argz,) = sections[1].value

    assert argx.name == "x"
    assert argx.annotation.name == "int"
    assert argx.annotation.canonical_path == "int"
    assert argx.description == "X value."
    assert argx.value == "1"

    assert argy.name == "y"
    assert argy.annotation.name == "int"
    assert argy.annotation.canonical_path == "int"
    assert argy.description == "Y value."
    assert argy.value == "None"

    assert argz.name == "z"
    assert argz.annotation.name == "int"
    assert argz.annotation.canonical_path == "int"
    assert argz.description == "Z value."
    assert argz.value == "None"


def test_prefer_docstring_types_over_annotations(parse_google: ParserType) -> None:
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

    (argx,) = sections[0].value
    (argy,) = sections[1].value
    (returns,) = sections[2].value

    assert argx.name == "x"
    assert argx.annotation.name == "str"
    assert argx.annotation.canonical_path == "str"
    assert argx.description == "X value."

    assert argy.name == "y"
    assert argy.annotation.name == "str"
    assert argy.annotation.canonical_path == "str"
    assert argy.description == "Y value."

    assert returns.annotation.name == "str"
    assert returns.annotation.canonical_path == "str"
    assert returns.description == "Sum X + Y + Z."


def test_parameter_line_without_colon(parse_google: ParserType) -> None:
    """Warn when missing colon.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Parameters:
            x is an integer.
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 0  # empty sections are discarded
    assert len(warnings) == 1
    assert "pair" in warnings[0]


def test_parameter_line_without_colon_keyword_only(parse_google: ParserType) -> None:
    """Warn when missing colon.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Keyword Args:
            x is an integer.
    """

    sections, warnings = parse_google(docstring)
    assert len(sections) == 0  # empty sections are discarded
    assert len(warnings) == 1
    assert "pair" in warnings[0]


def test_warn_about_unknown_parameters(parse_google: ParserType) -> None:
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


def test_never_warn_about_unknown_other_parameters(parse_google: ParserType) -> None:
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


def test_unknown_params_scan_doesnt_crash_without_parameters(parse_google: ParserType) -> None:
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


def test_class_uses_init_parameters(parse_google: ParserType) -> None:
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


def test_dataclass_uses_attributes(parse_google: ParserType) -> None:
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
# def test_missing_parameter(parse_google: ParserType) -> None:
#     """Warn on missing parameter in docstring.
#
#     Parameters:
#         parse_google: Fixture parser.
#     """
#     docstring = """
#         Parameters:
#             x: Integer.
#     """
#     assert not warnings


# =============================================================================================
# Attributes sections
def test_retrieve_attributes_annotation_from_parent(parse_google: ParserType) -> None:
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
    parent["a"] = Attribute("a", annotation=ExprName("int"))
    parent["b"] = Attribute("b", annotation=ExprName("str"))
    sections, _ = parse_google(docstring, parent=parent)
    attributes = sections[1].value
    assert attributes[0].name == "a"
    assert attributes[0].annotation.name == "int"
    assert attributes[1].name == "b"
    assert attributes[1].annotation.name == "str"


# =============================================================================================
# Yields sections
def test_parse_yields_section_with_return_annotation(parse_google: ParserType) -> None:
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
def test_parse_yields_tuple_in_iterator_or_generator(parse_google: ParserType, return_annotation: str) -> None:
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
    assert yields[0].annotation.name == "int"
    assert yields[1].name == "b"
    assert yields[1].annotation.name == "float"


@pytest.mark.parametrize(
    "return_annotation",
    [
        "Iterator[int]",
        "Generator[int, None, None]",
    ],
)
def test_extract_yielded_type_with_single_return_item(parse_google: ParserType, return_annotation: str) -> None:
    """Extract main type annotation from Iterator or Generator.

    Parameters:
        parse_google: Fixture parser.
        return_annotation: Parametrized return annotation as a string.
    """
    docstring = """
        Summary.

        Yields:
            A number.
    """
    sections, _ = parse_google(
        docstring,
        parent=Function(
            "func",
            returns=parse_annotation(return_annotation, Docstring("d", parent=Function("f"))),
        ),
    )
    yields = sections[1].value
    assert yields[0].annotation.name == "int"


# =============================================================================================
# Receives sections
def test_parse_receives_tuple_in_generator(parse_google: ParserType) -> None:
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
    assert receives[0].annotation.name == "int"
    assert receives[1].name == "b"
    assert receives[1].annotation.name == "float"


@pytest.mark.parametrize(
    "return_annotation",
    [
        "Generator[int, float, None]",
    ],
)
def test_extract_received_type_with_single_return_item(parse_google: ParserType, return_annotation: str) -> None:
    """Extract main type annotation from Iterator or Generator.

    Parameters:
        parse_google: Fixture parser.
        return_annotation: Parametrized return annotation as a string.
    """
    docstring = """
        Summary.

        Receives:
            A floating point number.
    """
    sections, _ = parse_google(
        docstring,
        parent=Function(
            "func",
            returns=parse_annotation(return_annotation, Docstring("d", parent=Function("f"))),
        ),
    )
    receives = sections[1].value
    assert receives[0].annotation.name == "float"


# =============================================================================================
# Returns sections
def test_parse_returns_tuple_in_generator(parse_google: ParserType) -> None:
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
    assert returns[0].annotation.name == "int"
    assert returns[1].name == "b"
    assert returns[1].annotation.name == "float"


# =============================================================================================
# Parser special features
def test_parse_admonitions(parse_google: ParserType) -> None:
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
def test_handle_false_admonitions_correctly(parse_google: ParserType, docstring: str) -> None:
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


def test_dont_insert_admonition_before_current_section(parse_google: ParserType) -> None:
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
def test_ignore_init_summary(parse_google: ParserType, docstring: str) -> None:
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
def test_trim_doctest_flags_basic_example(parse_google: ParserType, docstring: str) -> None:
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


def test_trim_doctest_flags_multi_example(parse_google: ParserType) -> None:
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


def test_single_line_with_trailing_whitespace(parse_google: ParserType) -> None:
    """Don't crash on single line docstrings with trailing whitespace.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = "a: b\n    "
    sections, warnings = parse_google(docstring, trim_doctest_flags=True)
    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.text
    assert not warnings


@pytest.mark.parametrize(
    ("returns_multiple_items", "return_annotation", "expected"),
    [
        (
            False,
            None,
            [DocstringReturn("", description="XXXXXXX\n    YYYYYYY\nZZZZZZZ", annotation=None)],
        ),
        (
            False,
            "tuple[int, int]",
            [DocstringReturn("", description="XXXXXXX\n    YYYYYYY\nZZZZZZZ", annotation="tuple[int, int]")],
        ),
        (
            True,
            None,
            [
                DocstringReturn("", description="XXXXXXX\nYYYYYYY", annotation=None),
                DocstringReturn("", description="ZZZZZZZ", annotation=None),
            ],
        ),
        (
            True,
            "tuple[int,int]",
            [
                DocstringReturn("", description="XXXXXXX\nYYYYYYY", annotation="int"),
                DocstringReturn("", description="ZZZZZZZ", annotation="int"),
            ],
        ),
    ],
)
def test_parse_returns_multiple_items(
    parse_google: ParserType,
    returns_multiple_items: bool,
    return_annotation: str,
    expected: list[DocstringReturn],
) -> None:
    """Parse Returns section with and without multiple items.

    Parameters:
        parse_google: Fixture parser.
        returns_multiple_items: Whether the `Returns` section has multiple items.
        return_annotation: The return annotation of the function to parse.
        expected: The expected value of the parsed Returns section.
    """
    parent = (
        Function("func", returns=parse_annotation(return_annotation, Docstring("d", parent=Function("f"))))
        if return_annotation is not None
        else None
    )
    docstring = """
        Returns:
            XXXXXXX
                YYYYYYY
            ZZZZZZZ
    """
    sections, _ = parse_google(
        docstring,
        returns_multiple_items=returns_multiple_items,
        parent=parent,
    )

    assert len(sections) == 1
    assert len(sections[0].value) == len(expected)

    for annotated, expected_ in zip(sections[0].value, expected):
        assert annotated.name == expected_.name
        assert str(annotated.annotation) == str(expected_.annotation)
        assert annotated.description == expected_.description


def test_avoid_false_positive_sections(parse_google: ParserType) -> None:
    """Avoid false positive when parsing sections.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Summary.
        Modules:
            Not a modules section.
        No blank line before title:
            Not an admonition.

        Blank line after title:

            Not an admonition.

        Modules:

            Not a modules section.
        Modules:

            Not a modules section.
        No blank line before and blank line after:

            Not an admonition.

        Classes:

        - Text.
    """
    sections, warnings = parse_google(docstring)
    assert len(sections) == 1
    assert "Classes" in sections[0].value
    assert "Text" in sections[0].value
    assert len(warnings) == 6
    assert warnings == [
        "Possible section skipped, reasons: Missing blank line above section",
        "Possible admonition skipped, reasons: Missing blank line above admonition",
        "Possible admonition skipped, reasons: Extraneous blank line below admonition title",
        "Possible section skipped, reasons: Extraneous blank line below section title",
        "Possible section skipped, reasons: Missing blank line above section; Extraneous blank line below section title",
        "Possible admonition skipped, reasons: Missing blank line above admonition; Extraneous blank line below admonition title",
    ]


def test_type_in_returns_without_parentheses(parse_google: ParserType) -> None:
    """Assert we can parse the return type without parentheses.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = """
        Summary.

        Returns:
            int: Description
                on several lines.
    """
    sections, warnings = parse_google(docstring, returns_named_value=False)
    assert len(sections) == 2
    assert not warnings
    retval = sections[1].value[0]
    assert retval.name == ""
    assert retval.annotation == "int"
    assert retval.description == "Description\non several lines."

    docstring = """
        Summary.

        Returns:
            Description
                on several lines.
    """
    sections, warnings = parse_google(docstring, returns_named_value=False)
    assert len(sections) == 2
    assert len(warnings) == 1
    retval = sections[1].value[0]
    assert retval.name == ""
    assert retval.annotation is None
    assert retval.description == "Description\non several lines."


def test_reading_property_type_in_summary(parse_google: ParserType) -> None:
    """Assert we can parse the return type of properties in their summary.

    Parameters:
        parse_google: Fixture parser.
    """
    docstring = "str: Description of the property."
    parent = Attribute("prop")
    parent.labels.add("property")
    sections, warnings = parse_google(docstring, returns_type_in_property_summary=True, parent=parent)
    assert len(sections) == 2
    assert sections[0].kind is DocstringSectionKind.text
    assert sections[1].kind is DocstringSectionKind.returns
    retval = sections[1].value[0]
    assert retval.name == ""
    assert retval.annotation.name == "str"
    assert retval.description == ""
