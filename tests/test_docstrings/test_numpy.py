"""Tests for the [Numpy-style parser][griffe.docstrings.numpy]."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

from griffe.dataclasses import Attribute, Class, Docstring, Function, Module, Parameter, Parameters
from griffe.docstrings.dataclasses import (
    DocstringSectionKind,
)
from griffe.docstrings.utils import parse_annotation
from griffe.expressions import ExprName

if TYPE_CHECKING:
    from tests.test_docstrings.helpers import ParserType


# =============================================================================================
# Markup flow (multilines, indentation, etc.)
def test_simple_docstring(parse_numpy: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_numpy: Fixture parser.
    """
    sections, warnings = parse_numpy("A simple docstring.")
    assert len(sections) == 1
    assert not warnings


def test_multiline_docstring(parse_numpy: ParserType) -> None:
    """Parse a multi-line docstring.

    Parameters:
        parse_numpy: Fixture parser.
    """
    sections, warnings = parse_numpy(
        """
        A somewhat longer docstring.

        Blablablabla.
        """,
    )
    assert len(sections) == 1
    assert not warnings


def test_code_blocks(parse_numpy: ParserType) -> None:
    """Parse code blocks.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        This docstring contains a code block!

        ```python
        print("hello")
        ```
    """

    sections, warnings = parse_numpy(docstring)
    assert len(sections) == 1
    assert not warnings


def test_indented_code_block(parse_numpy: ParserType) -> None:
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


def test_empty_indented_lines_in_section_with_items(parse_numpy: ParserType) -> None:
    """In sections with items, don't treat lines with just indentation as items.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = "Returns\n-------\nonly_item : type\n    Description.\n    \n    \n\nSomething."
    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1
    assert len(sections[0].value) == 2


def test_doubly_indented_lines_in_section_items(parse_numpy: ParserType) -> None:
    """In sections with items, don't remove all spaces on the left of indented lines.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = "Returns\n-------\nonly_item : type\n    Description:\n\n    - List item.\n        - Sublist item."
    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1
    lines = sections[0].value[0].description.split("\n")
    assert lines[-1].startswith(4 * " " + "- ")


# =============================================================================================
# Admonitions
def test_admonition_see_also(parse_numpy: ParserType) -> None:
    """Test a "See Also" admonition.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
    Summary text.

    See Also
    --------
    some_function

    more text
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 2
    assert sections[0].value == "Summary text."
    assert sections[1].title == "See Also"
    assert sections[1].value.description == "some_function\n\nmore text"


def test_admonition_empty(parse_numpy: ParserType) -> None:
    """Test an empty "See Also" admonition.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
    Summary text.

    See Also
    --------
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 2
    assert sections[0].value == "Summary text."
    assert sections[1].title == "See Also"
    assert sections[1].value.description == ""


def test_isolated_dash_lines_do_not_create_sections(parse_numpy: ParserType) -> None:
    """An isolated dash-line (`---`) should not be parsed as a section.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
    Summary text.

    ---
    Text.

    Note
    ----
    Note contents.

    ---
    Text.
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 2
    assert sections[0].value == "Summary text.\n\n---\nText."
    assert sections[1].title == "Note"
    assert sections[1].value.description == "Note contents.\n\n---\nText."


def test_admonition_warnings_special_case(parse_numpy: ParserType) -> None:
    """Test that the "Warnings" section renders as a warning admonition.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
    Summary text.

    Warnings
    --------
    Be careful!!!

    more text
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 2
    assert sections[0].value == "Summary text."
    assert sections[1].title == "Warnings"
    assert sections[1].value.description == "Be careful!!!\n\nmore text"
    assert sections[1].value.kind == "warning"


def test_admonition_notes_special_case(parse_numpy: ParserType) -> None:
    """Test that the "Warnings" section renders as a warning admonition.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
    Summary text.

    Notes
    -----
    Something noteworthy.

    more text
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 2
    assert sections[0].value == "Summary text."
    assert sections[1].title == "Notes"
    assert sections[1].value.description == "Something noteworthy.\n\nmore text"
    assert sections[1].value.kind == "note"


# =============================================================================================
# Annotations
def test_prefer_docstring_type_over_annotation(parse_numpy: ParserType) -> None:
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
        docstring,
        parent=Function("func", parameters=Parameters(Parameter("a", annotation="str"))),
    )
    assert len(sections) == 1
    param = sections[0].value[0]
    assert param.name == "a"
    assert param.description == ""
    assert param.annotation.name == "int"


def test_parse_complex_annotations(parse_numpy: ParserType) -> None:
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


@pytest.mark.parametrize(
    ("docstring", "name"),
    [
        ("Attributes\n---\na : {name}\n    Description.\n", "int"),
        ("Parameters\n---\na : {name}\n    Description.\n", "int"),
        ("Other Parameters\n---\na : {name}\n    Description.\n", "int"),
        ("Yields\n---\na : {name}\n    Description.\n", "int"),
        ("Receives\n---\na : {name}\n    Description.\n", "int"),
        ("Returns\n---\na : {name}\n    Description.\n", "int"),
        ("Raises\n---\n{name}\n    Description.\n", "RuntimeError"),
        ("Warns\n---\n{name}\n    Description.\n", "UserWarning"),
    ],
)
def test_parse_annotations_in_all_sections(parse_numpy: ParserType, docstring: str, name: str) -> None:
    """Assert annotations are parsed in all relevant sections.

    Parameters:
        parse_numpy: Fixture parser.
        docstring: Parametrized docstring.
        name: Parametrized name in annotation.
    """
    docstring = docstring.format(name=name)
    sections, _ = parse_numpy(docstring, parent=Function("f"))
    assert len(sections) == 1
    assert sections[0].value[0].annotation.name == name


def test_dont_crash_on_text_annotations(parse_numpy: ParserType, caplog: pytest.LogCaptureFixture) -> None:
    """Don't crash while parsing annotations containing unhandled nodes.

    Parameters:
        parse_numpy: Fixture parser.
        caplog: Pytest fixture used to capture logs.
    """
    docstring = """
        Attributes
        ----------
        region : str, list-like, geopandas.GeoSeries, geopandas.GeoDataFrame, geometric
            Description.

        Parameters
        ----------
        region : str, list-like, geopandas.GeoSeries, geopandas.GeoDataFrame, geometric
            Description.

        Returns
        -------
        str or bytes
            Description.

        Receives
        --------
        region : str, list-like, geopandas.GeoSeries, geopandas.GeoDataFrame, geometric
            Description.

        Yields
        ------
        str or bytes
            Description.
    """
    caplog.set_level(logging.DEBUG)
    assert parse_numpy(docstring, parent=Function("f"))
    assert all(record.levelname == "DEBUG" for record in caplog.records if "Failed to parse" in record.message)


# =============================================================================================
# Sections
def test_parameters_section(parse_numpy: ParserType) -> None:
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


def test_parse_starred_parameters(parse_numpy: ParserType) -> None:
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


def test_other_parameters_section(parse_numpy: ParserType) -> None:
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


def test_retrieve_annotation_from_parent(parse_numpy: ParserType) -> None:
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
        docstring,
        parent=Function("func", parameters=Parameters(Parameter("a", annotation="str"))),
    )
    assert len(sections) == 1
    param = sections[0].value[0]
    assert param.name == "a"
    assert param.description == ""
    assert param.annotation == "str"


def test_deprecated_section(parse_numpy: ParserType) -> None:
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


def test_returns_section(parse_numpy: ParserType) -> None:
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
        x :
            Name only
        :
            No name or annotation
        : int
            Only annotation
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1

    param = sections[0].value[0]
    assert param.name == ""
    assert param.description == "A list of integers."
    assert param.annotation == "list of int"

    param = sections[0].value[1]
    assert param.name == "flag"
    assert param.description == "Some kind\nof flag."
    assert param.annotation == "bool"

    param = sections[0].value[2]
    assert param.name == "x"
    assert param.description == "Name only"
    assert param.annotation is None

    param = sections[0].value[3]
    assert param.name == ""
    assert param.description == "No name or annotation"
    assert param.annotation is None

    param = sections[0].value[4]
    assert param.name == ""
    assert param.description == "Only annotation"
    assert param.annotation == "int"


def test_yields_section(parse_numpy: ParserType) -> None:
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
    param = sections[0].value[0]
    assert param.name == ""
    assert param.description == "A list of integers."
    assert param.annotation == "list of int"

    param = sections[0].value[1]
    assert param.name == "flag"
    assert param.description == "Some kind\nof flag."
    assert param.annotation == "bool"


def test_receives_section(parse_numpy: ParserType) -> None:
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
    param = sections[0].value[0]
    assert param.name == ""
    assert param.description == "A list of integers."
    assert param.annotation == "list of int"
    param = sections[0].value[1]
    assert param.name == "flag"
    assert param.description == "Some kind\nof flag."
    assert param.annotation == "bool"


def test_raises_section(parse_numpy: ParserType) -> None:
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
    param = sections[0].value[0]
    assert param.description == "There was an issue."
    assert param.annotation == "RuntimeError"


def test_warns_section(parse_numpy: ParserType) -> None:
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
    param = sections[0].value[0]
    assert param.description == "Heads up."
    assert param.annotation == "ResourceWarning"


def test_attributes_section(parse_numpy: ParserType) -> None:
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
    param = sections[0].value[0]
    assert param.name == "a"
    assert param.description == "Hello."
    assert param.annotation is None

    param = sections[0].value[1]
    assert param.name == "m"
    assert param.description == ""
    assert param.annotation is None

    param = sections[0].value[2]
    assert param.name == "z"
    assert param.description == "Bye."
    assert param.annotation == "int"


def test_parse_functions_section(parse_numpy: ParserType) -> None:
    """Parse Functions/Methods sections.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Functions
        ---------
        f(a, b=2)
            Hello.
        g
            Hi.

        Methods
        -------
        f(a, b=2)
            Hello.
        g
            Hi.
    """

    sections, warnings = parse_numpy(docstring)
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


def test_parse_classes_section(parse_numpy: ParserType) -> None:
    """Parse Classes sections.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Classes
        -------
        C(a, b=2)
            Hello.
        D
            Hi.
    """

    sections, warnings = parse_numpy(docstring)
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


def test_parse_modules_section(parse_numpy: ParserType) -> None:
    """Parse Modules sections.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Modules
        -------
        m
            Hello.
        n
            Hi.
    """

    sections, warnings = parse_numpy(docstring)
    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.modules
    module_m = sections[0].value[0]
    assert module_m.name == "m"
    assert module_m.description == "Hello."
    module_n = sections[0].value[1]
    assert module_n.name == "n"
    assert module_n.description == "Hi."
    assert not warnings


def test_examples_section(parse_numpy: ParserType) -> None:
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

        ```pycon
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


def test_examples_section_when_followed_by_named_section(parse_numpy: ParserType) -> None:
    """Parse examples section followed by another section.

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


def test_examples_section_as_last(parse_numpy: ParserType) -> None:
    """Parse examples section being last in the docstring.

    Parameters:
        parse_numpy: Parse function (fixture).
    """
    docstring = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit...

        Examples
        --------
        ```pycon
        >>> LoremIpsum.from_string("consectetur")
        <foofoo: Ipsum.Lorem>

        ```
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 2
    assert sections[0].kind is DocstringSectionKind.text
    assert sections[1].kind is DocstringSectionKind.examples


def test_blank_lines_in_section(parse_numpy: ParserType) -> None:
    """Support blank lines in the middle of sections.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Examples
        --------
        Line 1.

        Line 2.
    """
    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1


# =============================================================================================
# Attributes sections
def test_retrieve_attributes_annotation_from_parent(parse_numpy: ParserType) -> None:
    """Retrieve the annotations of attributes from the parent object.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Summary.

        Attributes
        ----------
        a :
            Whatever.
        b :
            Whatever.
    """
    parent = Class("cls")
    parent["a"] = Attribute("a", annotation=ExprName("int"))
    parent["b"] = Attribute("b", annotation=ExprName("str"))
    sections, _ = parse_numpy(docstring, parent=parent)
    attributes = sections[1].value
    assert attributes[0].name == "a"
    assert attributes[0].annotation.name == "int"
    assert attributes[1].name == "b"
    assert attributes[1].annotation.name == "str"


# =============================================================================================
# Parameters sections
def test_warn_about_unknown_parameters(parse_numpy: ParserType) -> None:
    """Warn about unknown parameters in "Parameters" sections.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Parameters
        ----------
        x : int
            Integer.
        y : int
            Integer.
    """

    _, warnings = parse_numpy(
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


def test_never_warn_about_unknown_other_parameters(parse_numpy: ParserType) -> None:
    """Never warn about unknown parameters in "Other parameters" sections.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Other Parameters
        ----------------
        x : int
            Integer.
        z : int
            Integer.
    """

    _, warnings = parse_numpy(
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


def test_unknown_params_scan_doesnt_crash_without_parameters(parse_numpy: ParserType) -> None:
    """Assert we don't crash when parsing parameters sections and parent object does not have parameters.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Parameters
        ----------
        this : str
            This.
        that : str
            That.
    """

    _, warnings = parse_numpy(docstring, parent=Module("mod"))
    assert not warnings


def test_class_uses_init_parameters(parse_numpy: ParserType) -> None:
    """Assert we use the `__init__` parameters when parsing classes' parameters sections.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Parameters
        ----------
        x :
            X value.
    """

    parent = Class("c")
    parent["__init__"] = Function("__init__", parameters=Parameters(Parameter("x", annotation="int")))
    sections, warnings = parse_numpy(docstring, parent=parent)
    assert not warnings
    argx = sections[0].value[0]
    assert argx.name == "x"
    assert argx.annotation == "int"
    assert argx.description == "X value."


def test_detect_optional_flag(parse_numpy: ParserType) -> None:
    """Detect the optional part of a parameter docstring.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Parameters
        ----------
        a : str, optional
        g, h : bytes, optional, default=b''
    """

    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1
    assert sections[0].value[0].annotation == "str"
    assert sections[0].value[1].annotation == "bytes"
    assert sections[0].value[1].default == "b''"
    assert sections[0].value[2].annotation == "bytes"
    assert sections[0].value[2].default == "b''"


@pytest.mark.parametrize("newlines", [1, 2, 3])
def test_blank_lines_in_item_descriptions(parse_numpy: ParserType, newlines: int) -> None:
    """Support blank lines in the middle of item descriptions.

    Parameters:
        parse_numpy: Fixture parser.
        newlines: Number of new lines between item summary and its body.
    """
    nl = "\n"
    nlindent = "\n" + " " * 12
    docstring = f"""
        Parameters
        ----------
        a : str
            Summary.{nlindent * newlines}Body.
    """
    sections, _ = parse_numpy(docstring)
    assert len(sections) == 1
    assert sections[0].value[0].annotation == "str"
    assert sections[0].value[0].description == f"Summary.{nl * newlines}Body."


# =============================================================================================
# Yields sections
@pytest.mark.parametrize(
    "return_annotation",
    [
        "Iterator[tuple[int, float]]",
        "Generator[tuple[int, float], ..., ...]",
    ],
)
def test_parse_yields_tuple_in_iterator_or_generator(parse_numpy: ParserType, return_annotation: str) -> None:
    """Parse Yields annotations in Iterator or Generator types.

    Parameters:
        parse_numpy: Fixture parser.
        return_annotation: Parametrized return annotation as a string.
    """
    docstring = """
        Summary.

        Yields
        ------
        a :
            Whatever.
        b :
            Whatever.
    """
    sections, _ = parse_numpy(
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
def test_extract_yielded_type_with_single_return_item(parse_numpy: ParserType, return_annotation: str) -> None:
    """Extract main type annotation from Iterator or Generator.

    Parameters:
        parse_numpy: Fixture parser.
        return_annotation: Parametrized return annotation as a string.
    """
    docstring = """
        Summary.

        Yields
        ------
        a :
            A number.
    """
    sections, _ = parse_numpy(
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
def test_parse_receives_tuple_in_generator(parse_numpy: ParserType) -> None:
    """Parse Receives annotations in Generator type.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Summary.

        Receives
        --------
        a :
            Whatever.
        b :
            Whatever.
    """
    sections, _ = parse_numpy(
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
def test_extract_received_type_with_single_return_item(parse_numpy: ParserType, return_annotation: str) -> None:
    """Extract main type annotation from Iterator or Generator.

    Parameters:
        parse_numpy: Fixture parser.
        return_annotation: Parametrized return annotation as a string.
    """
    docstring = """
        Summary.

        Receives
        --------
        a :
            A floating point number.
    """
    sections, _ = parse_numpy(
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
def test_parse_returns_tuple_in_generator(parse_numpy: ParserType) -> None:
    """Parse Returns annotations in Generator type.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = """
        Summary.

        Returns
        -------
        a :
            Whatever.
        b :
            Whatever.
    """
    sections, _ = parse_numpy(
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
def test_ignore_init_summary(parse_numpy: ParserType, docstring: str) -> None:
    """Correctly ignore summary in `__init__` methods' docstrings.

    Parameters:
        parse_numpy: Fixture parser.
        docstring: The docstring to parse (parametrized).
    """
    sections, _ = parse_numpy(docstring, parent=Function("__init__", parent=Class("C")), ignore_init_summary=True)
    for section in sections:
        assert "Summary" not in section.value

    if docstring.strip():
        sections, _ = parse_numpy(docstring, parent=Function("__init__", parent=Module("M")), ignore_init_summary=True)
        assert "Summary" in sections[0].value
        sections, _ = parse_numpy(docstring, parent=Function("f", parent=Class("C")), ignore_init_summary=True)
        assert "Summary" in sections[0].value
        sections, _ = parse_numpy(docstring, ignore_init_summary=True)
        assert "Summary" in sections[0].value


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
def test_trim_doctest_flags_basic_example(parse_numpy: ParserType, docstring: str) -> None:
    """Correctly parse simple example docstrings when `trim_doctest_flags` option is turned on.

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


def test_trim_doctest_flags_multi_example(parse_numpy: ParserType) -> None:
    """Correctly parse multiline example docstrings when `trim_doctest_flags` option is turned on.

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


def test_parsing_choices(parse_numpy: ParserType) -> None:
    """Correctly parse choices.

    Parameters:
        parse_numpy: Fixture parser.
    """
    docstring = r"""
    Parameters
    --------
    order : {'C', 'F', 'A'}
        Description of `order`.
    """
    sections, warnings = parse_numpy(docstring, trim_doctest_flags=True)
    assert sections[0].value[0].annotation == "'C', 'F', 'A'"
    assert not warnings
