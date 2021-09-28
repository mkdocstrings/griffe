"""Tests for the [RST-style parser][griffe.docstrings.rst]."""

from __future__ import annotations

import inspect

import pytest

from griffe.dataclasses import Argument, Arguments, Class, Data, Docstring, Function, Module
from griffe.docstrings import rst as parser
from griffe.docstrings.dataclasses import DocstringArgument, DocstringAttribute, DocstringElement, DocstringReturn, DocstringSectionKind

SOME_NAME = "foo"
SOME_TEXT = "descriptive test text"
SOME_EXTRA_TEXT = "more test text"
SOME_EXCEPTION_NAME = "SomeException"
SOME_OTHER_EXCEPTION_NAME = "SomeOtherException"


def parse(docstring: str, parent: Module | Class | Function | Data | None = None, **parser_opts):
    """Parse a doctring.

    Arguments:
        docstring: The docstring to parse.
        parent: The docstring's parent object.
        **parser_opts: Additional options accepted by the parser.

    Returns:
        The parsed sections, and warnings.
    """
    docstring_object = Docstring(docstring, lineno=1, endlineno=None)
    docstring_object.endlineno = len(docstring_object.lines) + 1
    if parent:
        docstring_object.parent = parent
        parent.docstring = docstring_object
    warnings = []
    parser.warn = lambda _docstring, _offset, message: warnings.append(message)
    sections = parser.parse(docstring_object, **parser_opts)
    return sections, warnings


def assert_argument_equal(actual: DocstringArgument, expected: DocstringArgument) -> None:
    assert actual.name == expected.name
    assert_annotated_obj_equal(actual, expected)
    assert actual.value == expected.value


def assert_attribute_equal(actual: DocstringAttribute, expected: DocstringAttribute) -> None:
    assert actual.name == expected.name
    assert_annotated_obj_equal(actual, expected)


def assert_annotated_obj_equal(actual: DocstringElement, expected: DocstringElement) -> None:
    assert actual.annotation == expected.annotation
    assert actual.description == expected.description


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
def test_parse__description_only_docstring__single_markdown_section(docstring):
    sections, warnings = parse(docstring)

    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.text
    assert sections[0].value == inspect.cleandoc(docstring)
    assert not warnings


def test_parse__no_description__single_markdown_section():
    sections, warnings = parse("")

    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.text
    assert sections[0].value == ""
    assert not warnings


def test_parse__multiple_blank_lines_before_description__single_markdown_section():
    sections, warnings = parse(
        """


        Now text"""
    )

    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.text
    assert sections[0].value == "Now text"
    assert not warnings


def test_parse__description_with_initial_newline__single_markdown_section():
    docstring = """
        With initial newline
    """

    sections, warnings = parse(docstring)
    assert len(sections) == 1
    assert sections[0].kind is DocstringSectionKind.text
    assert sections[0].value == inspect.cleandoc(docstring)
    assert not warnings


def test_parse__param_field__param_section():
    """Parse a simple docstring."""
    sections, _ = parse(
        f"""
        Docstring with one line param.

        :param {SOME_NAME}: {SOME_TEXT}
        """
    )
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(sections[1].value[0], DocstringArgument(SOME_NAME, annotation=None, description=SOME_TEXT))


def test_parse__only_param_field__empty_markdown():
    sections, _ = parse(":param foo: text")
    assert len(sections) == 2
    assert sections[0].kind is DocstringSectionKind.text
    assert sections[0].value == ""


@pytest.mark.parametrize(
    "param_directive_name",
    [
        "param",
        "parameter",
        "arg",
        "argument",
        "key",
        "keyword",
    ],
)
def test_parse__all_param_names__param_section(param_directive_name):
    sections, _ = parse(
        f"""
        Docstring with one line param.

        :{param_directive_name} {SOME_NAME}: {SOME_TEXT}
        """
    )
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(sections[1].value[0], DocstringArgument(SOME_NAME, annotation=None, description=SOME_TEXT))


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
def test_parse__param_field_multi_line__param_section(docstring):
    """Parse a simple docstring."""
    sections, _ = parse(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(
        sections[1].value[0],
        DocstringArgument(SOME_NAME, annotation=None, description=f"{SOME_TEXT} {SOME_EXTRA_TEXT}"),
    )


def test_parse__param_field_for_function__param_section_with_kind():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param foo: descriptive test text
    """

    sections, _ = parse(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(
        sections[1].value[0],
        DocstringArgument(SOME_NAME, annotation=None, description=SOME_TEXT),
    )


def test_parse__param_field_docs_type__param_section_with_type():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param str foo: descriptive test text
    """

    sections, _ = parse(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(
        sections[1].value[0],
        DocstringArgument(SOME_NAME, annotation="str", description=SOME_TEXT),
    )


def test_parse__param_field_type_field__param_section_with_type():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param foo: descriptive test text
        :type foo: str
    """

    sections, _ = parse(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(
        sections[1].value[0],
        DocstringArgument(SOME_NAME, annotation="str", description=SOME_TEXT),
    )


def test_parse__param_field_type_field_first__param_section_with_type():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :type foo: str
        :param foo: descriptive test text
    """

    sections, _ = parse(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(
        sections[1].value[0],
        DocstringArgument(SOME_NAME, annotation="str", description=SOME_TEXT),
    )


def test_parse__param_field_type_field_or_none__param_section_with_optional():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param foo: descriptive test text
        :type foo: str or None
    """

    sections, _ = parse(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(
        sections[1].value[0],
        DocstringArgument(SOME_NAME, annotation="Optional[str]", description=SOME_TEXT),
    )


def test_parse__param_field_type_none_or_field__param_section_with_optional():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param foo: descriptive test text
        :type foo: None or str
    """

    sections, _ = parse(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(
        sections[1].value[0],
        DocstringArgument(SOME_NAME, annotation="Optional[str]", description=SOME_TEXT),
    )


def test_parse__param_field_type_field_or_int__param_section_with_union():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param foo: descriptive test text
        :type foo: str or int
    """

    sections, _ = parse(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(
        sections[1].value[0],
        DocstringArgument(SOME_NAME, annotation="Union[str,int]", description=SOME_TEXT),
    )


def test_parse__param_field_type_multiple__param_section_with_union():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param foo: descriptive test text
        :type foo: str or int or float
    """

    sections, _ = parse(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(
        sections[1].value[0],
        DocstringArgument(
            SOME_NAME,
            annotation="Union[str,int,float]",
            description=SOME_TEXT,
        ),
    )


def test_parse__param_field_annotate_type__param_section_with_type():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param foo: descriptive test text
    """

    arguments = Arguments()
    arguments.add(Argument("foo", annotation="str", kind=None, default=None))
    function = Function(name="func", arguments=arguments)
    sections, warnings = parse(docstring, parent=function)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(
        sections[1].value[0],
        DocstringArgument(SOME_NAME, annotation="str", description=SOME_TEXT),
    )
    assert not warnings


def test_parse__param_field_no_matching_param__result_from_docstring():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param other: descriptive test text
    """

    sections, _ = parse(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(
        sections[1].value[0],
        DocstringArgument("other", annotation=None, description=SOME_TEXT),
    )


def test_parse__param_field_with_default__result_from_docstring():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param foo: descriptive test text
    """

    arguments = Arguments()
    arguments.add(Argument("foo", annotation=None, kind=None, default=repr("")))
    function = Function(name="func", arguments=arguments)
    sections, warnings = parse(docstring, parent=function)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.arguments
    assert_argument_equal(
        sections[1].value[0],
        DocstringArgument("foo", annotation=None, description=SOME_TEXT, value=repr("")),
    )
    assert not warnings


def test_parse__param_field_no_matching_param__error_message():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param other: descriptive test text
    """

    _, warnings = parse(docstring)
    assert "No matching parameter for 'other'" in warnings[0]


def test_parse__invalid_param_field_only_initial_marker__error_message():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param foo descriptive test text
    """

    _, warnings = parse(docstring)
    assert "Failed to get ':directive: value' pair" in warnings[0]


def test_parse__invalid_param_field_wrong_part_count__error_message():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param: descriptive test text
    """

    _, warnings = parse(docstring)
    assert "Failed to parse field directive" in warnings[0]


def test_parse__param_twice__error_message():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param foo: descriptive test text
        :param foo: descriptive test text again
    """

    arguments = Arguments()
    arguments.add(Argument("foo", annotation=None, kind=None, default=None))
    function = Function(name="func", arguments=arguments)
    _, warnings = parse(docstring, parent=function)
    assert "Duplicate parameter entry for 'foo'" in warnings[0]


def test_parse__param_type_twice_doc__error_message():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param str foo: descriptive test text
        :type foo: str
    """

    arguments = Arguments()
    arguments.add(Argument("foo", annotation=None, kind=None, default=None))
    function = Function(name="func", arguments=arguments)
    _, warnings = parse(docstring, parent=function)
    assert "Duplicate parameter information for 'foo'" in warnings[0]


def test_parse__param_type_twice_type_directive_first__error_message():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :type foo: str
        :param str foo: descriptive test text
    """

    arguments = Arguments()
    arguments.add(Argument("foo", annotation=None, kind=None, default=None))
    function = Function(name="func", arguments=arguments)
    _, warnings = parse(docstring, parent=function)
    assert "Duplicate parameter information for 'foo'" in warnings[0]


def test_parse__param_type_twice_annotated__error_message():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param str foo: descriptive test text
        :type foo: str
    """

    arguments = Arguments()
    arguments.add(Argument("foo", annotation="str", kind=None, default=None))
    function = Function(name="func", arguments=arguments)
    _, warnings = parse(docstring, parent=function)
    assert "Duplicate parameter information for 'foo'" in warnings[0]


def test_parse__param_type_no_type__error_message():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param str foo: descriptive test text
        :type str
    """

    arguments = Arguments()
    arguments.add(Argument("foo", annotation="str", kind=None, default=None))
    function = Function(name="func", arguments=arguments)
    _, warnings = parse(docstring, parent=function)
    assert "Failed to get ':directive: value' pair from" in warnings[0]


def test_parse__param_type_no_name__error_message():
    """Parse a simple docstring."""
    docstring = """
        Docstring with line continuation.

        :param str foo: descriptive test text
        :type: str
        """

    arguments = Arguments()
    arguments.add(Argument("foo", annotation="str", kind=None, default=None))
    function = Function(name="func", arguments=arguments)
    _, warnings = parse(docstring, parent=function)
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
def test_parse__attribute_field_multi_line__param_section(docstring):
    """Parse a simple docstring."""
    sections, warnings = parse(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.attributes
    assert_attribute_equal(
        sections[1].value[0],
        DocstringAttribute(SOME_NAME, annotation=None, description=f"{SOME_TEXT} {SOME_EXTRA_TEXT}"),
    )
    assert not warnings


@pytest.mark.parametrize(
    "attribute_directive_name",
    [
        "var",
        "ivar",
        "cvar",
    ],
)
def test_parse__all_attribute_names__param_section(attribute_directive_name):
    sections, warnings = parse(
        f"""
        Docstring with one line attribute.

        :{attribute_directive_name} {SOME_NAME}: {SOME_TEXT}
        """
    )
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.attributes
    assert_attribute_equal(
        sections[1].value[0],
        DocstringAttribute(SOME_NAME, annotation=None, description=SOME_TEXT),
    )
    assert not warnings


def test_parse__class_attributes__attributes_section():
    docstring = """
        Class docstring with attributes

        :var foo: descriptive test text
    """

    sections, _ = parse(docstring, parent=Class(name="klass"))
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.attributes
    assert_attribute_equal(
        sections[1].value[0],
        DocstringAttribute(SOME_NAME, annotation=None, description=SOME_TEXT),
    )


def test_parse__class_attributes_with_type__annotation_in_attributes_section():
    docstring = """
        Class docstring with attributes

        :vartype foo: str
        :var foo: descriptive test text
    """

    sections, _ = parse(docstring, parent=Class(name="klass"))
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.attributes
    assert_attribute_equal(
        sections[1].value[0],
        DocstringAttribute(SOME_NAME, annotation="str", description=SOME_TEXT),
    )


def test_parse__attribute_invalid_directive___error():
    docstring = """
        Class docstring with attributes

        :var descriptive test text
    """

    _, warnings = parse(docstring)
    assert "Failed to get ':directive: value' pair from" in warnings[0]


def test_parse__attribute_no_name__error():
    docstring = """
        Class docstring with attributes

        :var: descriptive test text
    """

    _, warnings = parse(docstring)
    assert "Failed to parse field directive from" in warnings[0]


def test_parse__attribute_duplicate__error():
    docstring = """
        Class docstring with attributes

        :var foo: descriptive test text
        :var foo: descriptive test text
        """

    _, warnings = parse(docstring)
    assert "Duplicate attribute entry for 'foo'" in warnings[0]


def test_parse__class_attributes_type_invalid__error():
    docstring = """
        Class docstring with attributes

        :vartype str
        :var foo: descriptive test text
        """

    _, warnings = parse(docstring)
    assert "Failed to get ':directive: value' pair from " in warnings[0]


def test_parse__class_attributes_type_no_name__error():
    docstring = """
        Class docstring with attributes

        :vartype: str
        :var foo: descriptive test text
        """

    _, warnings = parse(docstring)
    assert "Failed to get attribute name from" in warnings[0]


def test_parse__return_directive__return_section_no_type():
    docstring = """
        Function with only return directive

        :return: descriptive test text
    """

    sections, _ = parse(docstring)
    assert len(sections) == 2
    assert sections[1].kind is DocstringSectionKind.returns
    assert_annotated_obj_equal(
        sections[1].value,
        DocstringReturn(annotation=None, description=SOME_TEXT),
    )


# def test_parse__return_directive_rtype__return_section_with_type():
#     def f(foo: str):
#         """
#         Function with only return & rtype directive

#         :return: descriptive test text
#         :rtype: str
#         """
#         return foo

#     sections, warnings = parse(f)
#     assert len(sections) == 2
#     assert sections[1].kind is DocstringSectionKind.RETURN
#     assert_annotated_obj_equal(
#         sections[1].value,
#         DocstringElement(annotation="str", description=SOME_TEXT),
#     )


# def test_parse__return_directive_rtype_first__return_section_with_type():
#     def f(foo: str):
#         """
#         Function with only return & rtype directive

#         :rtype: str
#         :return: descriptive test text
#         """
#         return foo

#     sections, warnings = parse(f)
#     assert len(sections) == 2
#     assert sections[1].kind is DocstringSectionKind.RETURN
#     assert_annotated_obj_equal(
#         sections[1].value,
#         DocstringElement(annotation="str", description=SOME_TEXT),
#     )


# def test_parse__return_directive_annotation__return_section_with_type():
#     def f(foo: str) -> str:
#         """
#         Function with return directive, rtype directive, & annotation

#         :return: descriptive test text
#         """
#         return foo

#     sections, warnings = parse(f)
#     assert len(sections) == 2
#     assert sections[1].kind is DocstringSectionKind.RETURN
#     assert_annotated_obj_equal(
#         sections[1].value,
#         DocstringElement(annotation=str, description=SOME_TEXT),
#     )


# def test_parse__return_directive_annotation__return_section_with_type_error():
#     def f(foo: str) -> str:
#         """
#         Function with return directive, rtype directive, & annotation

#         :return: descriptive test text
#         :rtype: str
#         """
#         return foo

#     sections, warnings = parse(f)
#     assert len(sections) == 2
#     assert sections[1].kind is DocstringSectionKind.RETURN
#     assert_annotated_obj_equal(
#         sections[1].value,
#         DocstringElement(annotation=str, description=SOME_TEXT),
#     )
#     assert "Duplicate type information for return" in warnings[0]


# def test_parse__return_invalid__error():
#     def f(foo: str):
#         """
#         Function with only return directive

#         :return descriptive test text
#         """
#         return foo

#     sections, warnings = parse(f)
#     assert "Failed to get ':directive: value' pair from " in warnings[0]


# def test_parse__rtype_invalid__error():
#     def f(foo: str):
#         """
#         Function with only return directive

#         :rtype str
#         """
#         return foo

#     sections, warnings = parse(f)
#     assert "Failed to get ':directive: value' pair from " in warnings[0]


# def test_parse__raises_directive__exception_section():
#     def f(foo: str):
#         """
#         Function with only return directive

#         :raise SomeException: descriptive test text
#         """
#         return foo

#     sections, warnings = parse(f)
#     assert len(sections) == 2
#     assert sections[1].kind is DocstringSectionKind.EXCEPTIONS
#     assert_annotated_obj_equal(
#         sections[1].value[0],
#         DocstringElement(annotation=SOME_EXCEPTION_NAME, description=SOME_TEXT),
#     )


# def test_parse__multiple_raises_directive__exception_section_with_two():
#     def f(foo: str):
#         """
#         Function with only return directive

#         :raise SomeException: descriptive test text
#         :raise SomeOtherException: descriptive test text
#         """
#         return foo

#     sections, warnings = parse(f)
#     assert len(sections) == 2
#     assert sections[1].kind is DocstringSectionKind.EXCEPTIONS
#     assert_annotated_obj_equal(
#         sections[1].value[0],
#         DocstringElement(annotation=SOME_EXCEPTION_NAME, description=SOME_TEXT),
#     )
#     assert_annotated_obj_equal(
#         sections[1].value[1],
#         DocstringElement(annotation=SOME_OTHER_EXCEPTION_NAME, description=SOME_TEXT),
#     )


# @pytest.mark.parametrize(
#     "attribute_directive_name",
#     [
#         "raises",
#         "raise",
#         "except",
#         "exception",
#     ],
# )
# def test_parse__all_exception_names__param_section(attribute_directive_name):
#     sections, warnings = parse(
#         f"""
#         Docstring with one line attribute.

#         :{attribute_directive_name} {SOME_EXCEPTION_NAME}: {SOME_TEXT}
#         """
#     )
#     assert len(sections) == 2
#     assert sections[1].kind is DocstringSectionKind.EXCEPTIONS
#     assert_annotated_obj_equal(
#         sections[1].value[0],
#         DocstringElement(annotation=SOME_EXCEPTION_NAME, description=SOME_TEXT),
#     )


# def test_parse__raise_invalid__error():
#     def f(foo: str):
#         """
#         Function with only return directive

#         :raise descriptive test text
#         """
#         return foo

#     sections, warnings = parse(f)
#     assert "Failed to get ':directive: value' pair from " in warnings[0]


# def test_parse__raise_no_name__error():
#     def f(foo: str):
#         """
#         Function with only return directive

#         :raise: descriptive test text
#         """
#         return foo

#     sections, warnings = parse(f)
#     assert "Failed to parse exception directive from" in warnings[0]


# # -------------------------------
# # Fixture tests
# # -------------------------------


# def test_parse_module_attributes_section__expected_attributes_section():
#     """Parse attributes section in modules."""
#     obj = get_rst_object_documentation("docstring_attributes_section")
#     assert len(obj.docstring_sections) == 2
#     attr_section = obj.docstring_sections[1]
#     assert attr_section.kind is DocstringSectionKind.ATTRIBUTES
#     assert len(attr_section.value) == 5
#     expected = [
#         {"name": "A", "annotation": "int", "description": "Alpha."},
#         # type annotation takes preference over docstring
#         {"name": "B", "annotation": "str", "description": "Beta."},
#         {"name": "C", "annotation": "bool", "description": "Gamma."},
#         {"name": "D", "annotation": "", "description": "Delta."},
#         {"name": "E", "annotation": "float", "description": "Epsilon."},
#     ]
#     assert [serialize_attribute(attr) for attr in attr_section.value] == expected


# def test_parse_module_attributes_section__expected_docstring_errors():
#     """Parse attributes section in modules."""
#     obj = get_rst_object_documentation("docstring_attributes_section")
#     assert len(obj.docstring_errors) == 1
#     assert "Duplicate attribute information for 'B'" in obj.docstring_errors[0]


# def test_property_docstring__expected_description():
#     """Parse a property docstring."""
#     class_ = get_rst_object_documentation("class_docstrings:NotDefinedYet")
#     prop = class_.attributes[0]
#     sections = prop.docstring_sections
#     assert len(sections) == 2
#     assert sections[0].kind is DocstringSectionKind.text
#     assert (
#         sections[0].value
#         == "This property returns `self`.\n\nIt's fun because you can call it like `obj.ha.ha.ha.ha.ha.ha...`."
#     )


# def test_property_docstring__expected_return():
#     """Parse a property docstring."""
#     class_ = get_rst_object_documentation("class_docstrings:NotDefinedYet")
#     prop = class_.attributes[0]
#     sections = prop.docstring_sections
#     assert len(sections) == 2
#     assert sections[1].kind is DocstringSectionKind.RETURN
#     assert_annotated_obj_equal(sections[1].value, DocstringElement("NotDefinedYet", "self!"))


# def test_property_class_init__expected_description():
#     class_ = get_rst_object_documentation("class_docstrings:ClassInitFunction")
#     init = class_.methods[0]
#     sections = init.docstring_sections
#     assert len(sections) == 2
#     assert sections[0].kind is DocstringSectionKind.text
#     assert sections[0].value == "Initialize instance."


# def test_class_init__expected_param():
#     class_ = get_rst_object_documentation("class_docstrings:ClassInitFunction")
#     init = class_.methods[0]
#     sections = init.docstring_sections
#     assert len(sections) == 2
#     assert sections[1].kind is DocstringSectionKind.arguments
#     param_section = sections[1]
#     assert_argument_equal(param_section.value[0], DocstringArgument("value", str, "Value to store"))
#     assert_argument_equal(
#         param_section.value[1],
#         DocstringArgument("other", "int", "Other value with default", default=1),
#     )


# def test_member_function___expected_param():
#     class_ = get_rst_object_documentation("class_docstrings:ClassWithFunction")
#     init = class_.methods[0]
#     sections = init.docstring_sections
#     assert len(sections) == 3
#     param_section = sections[1]
#     assert param_section.kind is DocstringSectionKind.arguments
#     assert_argument_equal(param_section.value[0], DocstringArgument("value", str, "Value to store"))
#     assert_argument_equal(
#         param_section.value[1],
#         DocstringArgument("other", "int", "Other value with default", default=1),
#     )


# def test_member_function___expected_return():
#     class_ = get_rst_object_documentation("class_docstrings:ClassWithFunction")
#     init = class_.methods[0]
#     sections = init.docstring_sections
#     assert len(sections) == 3
#     assert sections[2].kind is DocstringSectionKind.RETURN
#     assert_annotated_obj_equal(sections[2].value, DocstringElement(str, "Concatenated result"))


# def test_property_docstring__no_errors():
#     """Parse a property docstring."""
#     class_ = get_rst_object_documentation("class_docstrings:NotDefinedYet")
#     prop = class_.attributes[0]
#     assert not prop.docstring_errors
