"""Tests for the [Sphinx-style parser][griffe.docstrings.sphinx]."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any

import pytest

from griffe import (
    Attribute,
    Class,
    DocstringAttribute,
    DocstringParameter,
    DocstringRaise,
    DocstringReturn,
    DocstringSectionKind,
    Expr,
    ExprAttribute,
    ExprBinOp,
    ExprName,
    ExprSubscript,
    ExprTuple,
    Function,
    Module,
    Parameter,
    Parameters,
)

if TYPE_CHECKING:
    from tests.test_docstrings.helpers import ParserType

SOME_NAME = "foo"
SOME_TEXT = "descriptive test text"
SOME_EXTRA_TEXT = "more test text"
SOME_EXCEPTION_NAME = "SomeException"
SOME_OTHER_EXCEPTION_NAME = "SomeOtherException"


@pytest.mark.parametrize(
    "docstring",
    [
        "One line docstring description",
        """
        Multiple line docstring description.

        With more text.
        """,
    ],
)
def test_parse__description_only_docstring__single_markdown_section(parse_sphinx: ParserType, docstring: str) -> None:
    """Parse a single or multiline docstring.

    Parameters:
        parse_sphinx: Fixture parser.
        docstring: A parametrized docstring.
    """
    sections, warnings = parse_sphinx(docstring)

    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.text
    assert sections[0].value == inspect.cleandoc(docstring)
    assert not warnings


def test_parse__no_description__single_markdown_section(parse_sphinx: ParserType) -> None:
    """Parse an empty docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    sections, warnings = parse_sphinx("")

    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.text
    assert sections[0].value == ""
    assert not warnings


def test_parse__multiple_blank_lines_before_description__single_markdown_section(parse_sphinx: ParserType) -> None:
    """Parse a docstring with initial blank lines.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    sections, warnings = parse_sphinx(
        """


        Now text""",
    )

    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.text
    assert sections[0].value == "Now text"
    assert not warnings


def test_parse__param_field__param_section(parse_sphinx: ParserType) -> None:
    """Parse a parameter section.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    sections, _ = parse_sphinx(
        f"""
        Docstring with one line param.

        :param {SOME_NAME}: {SOME_TEXT}
        """,
    )
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter(SOME_NAME, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__only_param_field__empty_markdown(parse_sphinx: ParserType) -> None:
    """Parse only a parameter section.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    sections, _ = parse_sphinx(":param foo: text")
    assert len(sections) == 2
    assert sections[0].kind is DocstringSectionKind.text
    assert sections[0].value == ""


@pytest.mark.parametrize(
    "param_directive_name",
    [
        "param",
        "parameter",
        "arg",
        "arguments",
        "key",
        "keyword",
    ],
)
def test_parse__all_param_names__param_section(parse_sphinx: ParserType, param_directive_name: str) -> None:
    """Parse all parameters directives.

    Parameters:
        parse_sphinx: Fixture parser.
        param_directive_name: A parametrized directive name.
    """
    sections, _ = parse_sphinx(
        f"""
        Docstring with one line param.

        :{param_directive_name} {SOME_NAME}: {SOME_TEXT}
        """,
    )
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter(SOME_NAME, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


@pytest.mark.parametrize(
    "docstring",
    [
        f"""
        Docstring with param with continuation, no indent.

        :param {SOME_NAME}: {SOME_TEXT}
        {SOME_EXTRA_TEXT}
        """,
        f"""
        Docstring with param with continuation, with indent.

        :param {SOME_NAME}: {SOME_TEXT}
          {SOME_EXTRA_TEXT}
        """,
    ],
)
def test_parse__param_field_multi_line__param_section(parse_sphinx: ParserType, docstring: str) -> None:
    """Parse multiline directives.

    Parameters:
        parse_sphinx: Fixture parser.
        docstring: A parametrized docstring.
    """
    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter(SOME_NAME, description=f"{SOME_TEXT} {SOME_EXTRA_TEXT}")
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__param_field_for_function__param_section_with_kind(parse_sphinx: ParserType) -> None:
    """Parse parameters.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param foo: {SOME_TEXT}
    """

    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter(SOME_NAME, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__param_field_docs_type__param_section_with_type(parse_sphinx: ParserType) -> None:
    """Parse parameters with types.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param str foo: {SOME_TEXT}
    """

    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter(SOME_NAME, annotation="str", description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


@pytest.mark.parametrize("type_", ["str", "int"])
def test_parse__param_field_type_field__param_section_with_type(parse_sphinx: ParserType, type_: str) -> None:
    """Parse parameters with separated types.

    Parameters:
        parse_sphinx: Fixture parser.
        type_: The type to use in the type directive.
    """
    docstring = f"""
        Docstring with line continuation.

        :param {SOME_NAME}: {SOME_TEXT}
        :type {SOME_NAME}: {type_}
    """

    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter(SOME_NAME, annotation=f"{type_}", description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


@pytest.mark.parametrize("type_", ["str", "int"])
def test_parse__param_field_type_field__param_section_with_type_with_parent(
    parse_sphinx: ParserType,
    type_: str,
) -> None:
    """Parse parameters with separated types.

    Parameters:
        parse_sphinx: Fixture parser.
        type_: The type to use in the type directive.
    """
    docstring = f"""
        Docstring with line continuation.

        :param {SOME_NAME}: {SOME_TEXT}
        :type {SOME_NAME}: {type_}
    """
    parent_fn = Function("func", parameters=Parameters(Parameter(SOME_NAME)))
    sections, _ = parse_sphinx(docstring, parent=parent_fn)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected_annotation = ExprName(name=f"{type_}")
    expected = DocstringParameter(SOME_NAME, annotation=expected_annotation, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()
    assert isinstance(actual.annotation, type(expected.annotation))
    assert isinstance(actual.annotation, ExprName)
    assert isinstance(actual.annotation, Expr)
    assert actual.annotation.as_dict() == expected_annotation.as_dict()


def test_parse__param_field_type_field_first__param_section_with_type(parse_sphinx: ParserType) -> None:
    """Parse parameters with separated types first.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :type foo: str
        :param foo: {SOME_TEXT}
    """

    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter(SOME_NAME, annotation="str", description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__param_field_type_field_first__param_section_with_type_with_parent(parse_sphinx: ParserType) -> None:
    """Parse parameters with separated types first.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :type {SOME_NAME}: str
        :param {SOME_NAME}: {SOME_TEXT}
    """
    parent_fn = Function("func", parameters=Parameters(Parameter(SOME_NAME)))
    sections, _ = parse_sphinx(docstring, parent=parent_fn)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected_annotation = ExprName("str", parent=Class("C"))
    expected = DocstringParameter(SOME_NAME, annotation=expected_annotation, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()
    assert isinstance(actual.annotation, type(expected.annotation))
    assert isinstance(actual.annotation, ExprName)
    assert isinstance(actual.annotation, Expr)
    assert actual.annotation.as_dict() == expected_annotation.as_dict()


@pytest.mark.parametrize("union", ["str or None", "None or str", "str or int", "str or int or float"])
def test_parse__param_field_type_field_or_none__param_section_with_optional(
    parse_sphinx: ParserType,
    union: str,
) -> None:
    """Parse parameters with separated union types.

    Parameters:
        parse_sphinx: Fixture parser.
        union: A parametrized union type.
    """
    docstring = f"""
        Docstring with line continuation.

        :param foo: {SOME_TEXT}
        :type foo: {union}
    """

    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter(SOME_NAME, annotation=union.replace(" or ", " | "), description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


@pytest.mark.parametrize(
    ("union", "expected_annotation"),
    [
        ("str or None", ExprBinOp(ExprName("str"), "|", "None")),
        ("None or str", ExprBinOp("None", "|", ExprName("str"))),
        ("str or int", ExprBinOp(ExprName("str"), "|", ExprName("int"))),
        ("str or int or float", ExprBinOp(ExprBinOp(ExprName("str"), "|", ExprName("int")), "|", ExprName("float"))),
    ],
)
def test_parse__param_field_type_field_or_none__param_section_with_optional_with_parent(
    parse_sphinx: ParserType,
    union: str,
    expected_annotation: Expr,
) -> None:
    """Parse parameters with separated union types.

    Parameters:
        parse_sphinx: Fixture parser.
        union: A parametrized union type.
        expected_annotation: The expected annotation as an expression
    """
    docstring = f"""
        Docstring with line continuation.

        :param {SOME_NAME}: {SOME_TEXT}
        :type {SOME_NAME}: {union}
    """

    parent_fn = Function("func", parameters=Parameters(Parameter(SOME_NAME)))
    sections, _ = parse_sphinx(docstring, parent=parent_fn)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter(SOME_NAME, annotation=expected_annotation, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()
    assert isinstance(actual.annotation, type(expected.annotation))
    assert isinstance(actual.annotation, Expr)
    assert actual.annotation.as_dict() == expected_annotation.as_dict()


def test_parse__param_field_annotate_type__param_section_with_type(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param foo: {SOME_TEXT}
    """

    sections, warnings = parse_sphinx(
        docstring,
        parent=Function("func", parameters=Parameters(Parameter("foo", annotation="str", kind=None))),
    )
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter(SOME_NAME, annotation="str", description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()
    assert not warnings


def test_parse__param_field_no_matching_param__result_from_docstring(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param other: {SOME_TEXT}
    """

    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter("other", description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__param_field_with_default__result_from_docstring(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param foo: {SOME_TEXT}
    """

    sections, warnings = parse_sphinx(
        docstring,
        parent=Function("func", parameters=Parameters(Parameter("foo", kind=None, default=repr("")))),
    )
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter("foo", description=SOME_TEXT, value=repr(""))
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()
    assert not warnings


def test_parse__param_field_no_matching_param__error_message(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param other: {SOME_TEXT}
    """

    _, warnings = parse_sphinx(docstring)
    assert "No matching parameter for 'other'" in warnings[0]


def test_parse__invalid_param_field_only_initial_marker__error_message(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param foo {SOME_TEXT}
    """

    _, warnings = parse_sphinx(docstring)
    assert "Failed to get ':directive: value' pair" in warnings[0]


def test_parse__invalid_param_field_wrong_part_count__error_message(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param: {SOME_TEXT}
    """

    _, warnings = parse_sphinx(docstring)
    assert "Failed to parse field directive" in warnings[0]


def test_parse__invalid_param_field_wrong_part_count_spaces_4__error_message(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param typing.Union[str, int] {SOME_NAME}: {SOME_TEXT}
    """

    sections, warnings = parse_sphinx(docstring)

    # Assert that the warning is shown
    assert "Failed to parse field directive" in warnings[0]

    # Assert that the parameter is still collected, but ignores the invalid type
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter(SOME_NAME, annotation=None, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__valid_param_field_part_count_3(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param typing.Union[str,int] {SOME_NAME}: {SOME_TEXT}
    """

    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    expected = DocstringParameter(SOME_NAME, annotation="typing.Union[str,int]", description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__valid_param_field_part_count_3_with_parent(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param typing.Union[str,int] {SOME_NAME}: {SOME_TEXT}
    """

    parent_fn = Function("func3", parameters=Parameters(Parameter(name=SOME_NAME)))
    sections, _ = parse_sphinx(docstring, parent=parent_fn)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.parameters
    actual = sections[1].value[0]
    typing_expr = ExprName("typing", parent=parent_fn)
    expected_annotation = ExprSubscript(
        left=ExprAttribute(values=[typing_expr, ExprName("Union", parent=typing_expr)]),
        slice=ExprTuple([ExprName("str", parent=parent_fn), ExprName("int", parent=parent_fn)], implicit=True),
    )
    expected = DocstringParameter(SOME_NAME, annotation=expected_annotation, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__param_twice__error_message(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param foo: {SOME_TEXT}
        :param foo: {SOME_TEXT} again
    """

    _, warnings = parse_sphinx(
        docstring,
        parent=Function("func", parameters=Parameters(Parameter("foo", kind=None))),
    )
    assert "Duplicate parameter entry for 'foo'" in warnings[0]


def test_parse__param_type_twice_doc__error_message(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param str foo: {SOME_TEXT}
        :type foo: str
    """

    _, warnings = parse_sphinx(
        docstring,
        parent=Function("func", parameters=Parameters(Parameter("foo", kind=None))),
    )
    assert "Duplicate parameter information for 'foo'" in warnings[0]


def test_parse__param_type_twice_type_directive_first__error_message(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :type foo: str
        :param str foo: {SOME_TEXT}
    """

    _, warnings = parse_sphinx(
        docstring,
        parent=Function("func", parameters=Parameters(Parameter("foo", kind=None))),
    )
    assert "Duplicate parameter information for 'foo'" in warnings[0]


def test_parse__param_type_twice_annotated__error_message(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param str foo: {SOME_TEXT}
        :type foo: str
    """

    _, warnings = parse_sphinx(
        docstring,
        parent=Function("func", parameters=Parameters(Parameter("foo", annotation="str", kind=None))),
    )
    assert "Duplicate parameter information for 'foo'" in warnings[0]


def test_warn_about_unknown_parameters(parse_sphinx: ParserType) -> None:
    """Warn about unknown parameters in "Parameters" sections.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = """

        :param str a: {SOME_TEXT}
    """

    _, warnings = parse_sphinx(
        docstring,
        parent=Function(
            "func",
            parameters=Parameters(
                Parameter("b"),
            ),
        ),
    )
    assert len(warnings) == 1
    assert "Parameter 'a' does not appear in the function signature" in warnings[0]


def test_parse__param_type_no_type__error_message(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param str foo: {SOME_TEXT}
        :type str
    """

    _, warnings = parse_sphinx(
        docstring,
        parent=Function("func", parameters=Parameters(Parameter("foo", annotation="str", kind=None))),
    )
    assert "Failed to get ':directive: value' pair from" in warnings[0]


def test_parse__param_type_no_name__error_message(parse_sphinx: ParserType) -> None:
    """Parse a simple docstring.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Docstring with line continuation.

        :param str foo: {SOME_TEXT}
        :type: str
        """

    _, warnings = parse_sphinx(
        docstring,
        parent=Function("func", parameters=Parameters(Parameter("foo", annotation="str", kind=None))),
    )
    assert "Failed to get parameter name from" in warnings[0]


@pytest.mark.parametrize(
    "docstring",
    [
        f"""
        Docstring with param with continuation, no indent.

        :var {SOME_NAME}: {SOME_TEXT}
        {SOME_EXTRA_TEXT}
        """,
        f"""
        Docstring with param with continuation, with indent.

        :var {SOME_NAME}: {SOME_TEXT}
          {SOME_EXTRA_TEXT}
        """,
    ],
)
def test_parse__attribute_field_multi_line__param_section(parse_sphinx: ParserType, docstring: str) -> None:
    """Parse multiline attributes.

    Parameters:
        parse_sphinx: Fixture parser.
        docstring: A parametrized docstring.
    """
    sections, warnings = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.attributes
    actual = sections[1].value[0]
    expected = DocstringAttribute(SOME_NAME, description=f"{SOME_TEXT} {SOME_EXTRA_TEXT}")
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()
    assert not warnings


@pytest.mark.parametrize(
    "attribute_directive_name",
    [
        "var",
        "ivar",
        "cvar",
    ],
)
def test_parse__all_attribute_names__param_section(parse_sphinx: ParserType, attribute_directive_name: str) -> None:
    """Parse all attributes directives.

    Parameters:
        parse_sphinx: Fixture parser.
        attribute_directive_name: A parametrized directive name.
    """
    sections, warnings = parse_sphinx(
        f"""
        Docstring with one line attribute.

        :{attribute_directive_name} {SOME_NAME}: {SOME_TEXT}
        """,
    )
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.attributes
    actual = sections[1].value[0]
    expected = DocstringAttribute(SOME_NAME, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()
    assert not warnings


def test_parse__class_attributes__attributes_section(parse_sphinx: ParserType) -> None:
    """Parse class attributes.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Class docstring with attributes

        :var foo: {SOME_TEXT}
    """

    sections, _ = parse_sphinx(docstring, parent=Class("klass"))
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.attributes
    actual = sections[1].value[0]
    expected = DocstringAttribute(SOME_NAME, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__class_attributes_with_type__annotation_in_attributes_section(parse_sphinx: ParserType) -> None:
    """Parse typed class attributes.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Class docstring with attributes

        :vartype foo: str
        :var foo: {SOME_TEXT}
    """

    sections, _ = parse_sphinx(docstring, parent=Class("klass"))
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.attributes
    actual = sections[1].value[0]
    expected = DocstringAttribute(SOME_NAME, annotation="str", description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__attribute_invalid_directive___error(parse_sphinx: ParserType) -> None:
    """Warn on invalid attribute directive.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Class docstring with attributes

        :var {SOME_TEXT}
    """

    _, warnings = parse_sphinx(docstring)
    assert "Failed to get ':directive: value' pair from" in warnings[0]


def test_parse__attribute_no_name__error(parse_sphinx: ParserType) -> None:
    """Warn on invalid attribute directive.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Class docstring with attributes

        :var: {SOME_TEXT}
    """

    _, warnings = parse_sphinx(docstring)
    assert "Failed to parse field directive from" in warnings[0]


def test_parse__attribute_duplicate__error(parse_sphinx: ParserType) -> None:
    """Warn on duplicate attribute directive.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Class docstring with attributes

        :var foo: {SOME_TEXT}
        :var foo: {SOME_TEXT}
        """

    _, warnings = parse_sphinx(docstring)
    assert "Duplicate attribute entry for 'foo'" in warnings[0]


def test_parse__class_attributes_type_invalid__error(parse_sphinx: ParserType) -> None:
    """Warn on invalid attribute type directive.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Class docstring with attributes

        :vartype str
        :var foo: {SOME_TEXT}
        """

    _, warnings = parse_sphinx(docstring)
    assert "Failed to get ':directive: value' pair from " in warnings[0]


def test_parse__class_attributes_type_no_name__error(parse_sphinx: ParserType) -> None:
    """Warn on invalid attribute directive.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Class docstring with attributes

        :vartype: str
        :var foo: {SOME_TEXT}
        """

    _, warnings = parse_sphinx(docstring)
    assert "Failed to get attribute name from" in warnings[0]


def test_parse__return_directive__return_section_no_type(parse_sphinx: ParserType) -> None:
    """Parse return directives.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Function with only return directive

        :return: {SOME_TEXT}
    """

    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.returns
    actual = sections[1].value[0]
    expected = DocstringReturn(name="", annotation=None, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__return_directive_rtype__return_section_with_type(parse_sphinx: ParserType) -> None:
    """Parse typed return directives.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Function with only return & rtype directive

        :return: {SOME_TEXT}
        :rtype: str
    """

    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.returns
    actual = sections[1].value[0]
    expected = DocstringReturn(name="", annotation="str", description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__return_directive_rtype_first__return_section_with_type(parse_sphinx: ParserType) -> None:
    """Parse typed-first return directives.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Function with only return & rtype directive

        :rtype: str
        :return: {SOME_TEXT}
    """

    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.returns
    actual = sections[1].value[0]
    expected = DocstringReturn(name="", annotation="str", description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__return_directive_annotation__return_section_with_type(parse_sphinx: ParserType) -> None:
    """Parse return directives with return annotation.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Function with return directive, rtype directive, & annotation

        :return: {SOME_TEXT}
    """

    sections, _ = parse_sphinx(docstring, parent=Function("func", returns="str"))
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.returns
    actual = sections[1].value[0]
    expected = DocstringReturn(name="", annotation="str", description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__return_directive_annotation__prefer_return_directive(parse_sphinx: ParserType) -> None:
    """Prefer docstring type over return annotation.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Function with return directive, rtype directive, & annotation

        :return: {SOME_TEXT}
        :rtype: str
    """

    sections, _ = parse_sphinx(docstring, parent=Function("func", returns="int"))
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.returns
    actual = sections[1].value[0]
    expected = DocstringReturn(name="", annotation="str", description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__return_invalid__error(parse_sphinx: ParserType) -> None:
    """Warn on invalid return directive.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Function with only return directive

        :return {SOME_TEXT}
    """

    _, warnings = parse_sphinx(docstring)
    assert "Failed to get ':directive: value' pair from " in warnings[0]


def test_parse__rtype_invalid__error(parse_sphinx: ParserType) -> None:
    """Warn on invalid typed return directive.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = """
        Function with only return directive

        :rtype str
    """

    _, warnings = parse_sphinx(docstring)
    assert "Failed to get ':directive: value' pair from " in warnings[0]


def test_parse__raises_directive__exception_section(parse_sphinx: ParserType) -> None:
    """Parse raise directives.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Function with only return directive

        :raise SomeException: {SOME_TEXT}
    """

    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.raises
    actual = sections[1].value[0]
    expected = DocstringRaise(annotation=SOME_EXCEPTION_NAME, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__multiple_raises_directive__exception_section_with_two(parse_sphinx: ParserType) -> None:
    """Parse multiple raise directives.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Function with only return directive

        :raise SomeException: {SOME_TEXT}
        :raise SomeOtherException: {SOME_TEXT}
    """

    sections, _ = parse_sphinx(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.raises
    actual = sections[1].value[0]
    expected = DocstringRaise(annotation=SOME_EXCEPTION_NAME, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()
    actual = sections[1].value[1]
    expected = DocstringRaise(annotation=SOME_OTHER_EXCEPTION_NAME, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


@pytest.mark.parametrize(
    "raise_directive_name",
    [
        "raises",
        "raise",
        "except",
        "exception",
    ],
)
def test_parse__all_exception_names__param_section(parse_sphinx: ParserType, raise_directive_name: str) -> None:
    """Parse all raise directives.

    Parameters:
        parse_sphinx: Fixture parser.
        raise_directive_name: A parametrized directive name.
    """
    sections, _ = parse_sphinx(
        f"""
        Docstring with one line attribute.

        :{raise_directive_name} {SOME_EXCEPTION_NAME}: {SOME_TEXT}
        """,
    )
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.raises
    actual = sections[1].value[0]
    expected = DocstringRaise(annotation=SOME_EXCEPTION_NAME, description=SOME_TEXT)
    assert isinstance(actual, type(expected))
    assert actual.as_dict() == expected.as_dict()


def test_parse__raise_invalid__error(parse_sphinx: ParserType) -> None:
    """Warn on invalid raise directives.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Function with only return directive

        :raise {SOME_TEXT}
    """

    _, warnings = parse_sphinx(docstring)
    assert "Failed to get ':directive: value' pair from " in warnings[0]


def test_parse__raise_no_name__error(parse_sphinx: ParserType) -> None:
    """Warn on invalid raise directives.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = f"""
        Function with only return directive

        :raise: {SOME_TEXT}
    """

    _, warnings = parse_sphinx(docstring)
    assert "Failed to parse exception directive from" in warnings[0]


def test_parse__module_attributes_section__expected_attributes_section(parse_sphinx: ParserType) -> None:
    """Parse attributes section in modules.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = """
        Let's describe some attributes.

        :var A: Alpha.
        :vartype B: bytes
        :var B: Beta.
        :var C: Gamma.
        :var D: Delta.
        :var E: Epsilon.
        :vartype E: float
    """

    module = Module("mod", filepath=None)
    module["A"] = Attribute("A", annotation="int", value="0")
    module["B"] = Attribute("B", annotation="str", value=repr("ŧ"))
    module["C"] = Attribute("C", annotation="bool", value="True")
    module["D"] = Attribute("D", annotation=None, value="3.0")
    module["E"] = Attribute("E", annotation=None, value="None")
    sections, warnings = parse_sphinx(docstring, parent=module)

    attr_section = sections[1]
    assert attr_section.kind is DocstringSectionKind.attributes
    assert len(attr_section.value) == 5
    expected_data: list[dict[str, Any]] = [
        {"name": "A", "annotation": "int", "description": "Alpha."},
        {"name": "B", "annotation": "bytes", "description": "Beta."},
        {"name": "C", "annotation": "bool", "description": "Gamma."},
        {"name": "D", "annotation": None, "description": "Delta."},
        {"name": "E", "annotation": "float", "description": "Epsilon."},
    ]
    for index, expected_kwargs in enumerate(expected_data):
        actual = attr_section.value[index]
        expected = DocstringAttribute(**expected_kwargs)
        assert isinstance(actual, type(expected))
        assert actual.name == expected.name
        assert actual.as_dict() == expected.as_dict()
    assert not warnings


def test_parse__properties_return_type(parse_sphinx: ParserType) -> None:
    """Parse attributes section in modules.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = """
        Property that returns True for explaining the issue.

        :return: True
    """
    prop = Attribute("example", annotation="bool")
    sections, warnings = parse_sphinx(docstring, parent=prop)
    assert not warnings
    assert sections[1].value[0].annotation == "bool"


# =============================================================================================
# Warnings
def test_disabled_warnings(parse_sphinx: ParserType) -> None:
    """Assert warnings are disabled.

    Parameters:
        parse_sphinx: Fixture parser.
    """
    docstring = ":param x: X value."
    _, warnings = parse_sphinx(docstring, warnings=True)
    assert warnings
    _, warnings = parse_sphinx(docstring, warnings=False)
    assert not warnings
