"""This module defines functions to parse Google-style docstrings into structured data."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Pattern

from griffe.docstrings.dataclasses import (
    DocstringAdmonition,
    DocstringAttribute,
    DocstringException,
    DocstringParameter,
    DocstringReceive,
    DocstringReturn,
    DocstringSection,
    DocstringSectionKind,
    DocstringWarn,
    DocstringYield,
)
from griffe.docstrings.utils import warning

if TYPE_CHECKING:
    from griffe.dataclasses import Docstring

_warn = warning(__name__)

_section_kind = {
    "args": DocstringSectionKind.parameters,
    "arguments": DocstringSectionKind.parameters,
    "params": DocstringSectionKind.parameters,
    "parameters": DocstringSectionKind.parameters,
    "keyword args": DocstringSectionKind.other_parameters,
    "keyword parameters": DocstringSectionKind.other_parameters,
    "other args": DocstringSectionKind.other_parameters,
    "other parameters": DocstringSectionKind.other_parameters,
    "raises": DocstringSectionKind.raises,
    "exceptions": DocstringSectionKind.raises,
    "returns": DocstringSectionKind.returns,
    "yields": DocstringSectionKind.yields,
    "examples": DocstringSectionKind.examples,
    "attributes": DocstringSectionKind.attributes,
}

_RE_ADMONITION: Pattern = re.compile(r"^(?P<type>[\w-][\s\w-]*):(\s+(?P<title>.+))?$", re.I)
"""Regular expression to match admonitions, of the form `TYPE: [TITLE]`."""


def _read_block_items(docstring: Docstring, offset: int) -> tuple[list[str], int]:  # noqa: WPS231
    lines = docstring.lines
    if offset >= len(lines):
        return [], offset

    index = offset
    items: list[str] = []

    # skip first empty lines
    while _is_empty_line(lines[index]):
        index += 1

    # get initial indent
    indent = len(lines[index]) - len(lines[index].lstrip())

    if indent == 0:
        # first non-empty line was not indented, abort
        return [], index - 1

    # start processing first item
    current_item = [lines[index][indent:]]
    index += 1

    # loop on next lines
    while index < len(lines):
        line = lines[index]

        if line.startswith(indent * 2 * " "):
            # continuation line
            current_item.append(line[indent * 2 :])

        elif line.startswith((indent + 1) * " "):
            # indent between initial and continuation: append but warn
            cont_indent = len(line) - len(line.lstrip())
            current_item.append(line[cont_indent:])
            _warn(
                docstring,
                index,
                f"Confusing indentation for continuation line {index+1} in docstring, "
                f"should be {indent} * 2 = {indent*2} spaces, not {cont_indent}",
            )

        elif line.startswith(indent * " "):
            # indent equal to initial one: new item
            items.append("\n".join(current_item))
            current_item = [line[indent:]]

        elif _is_empty_line(line):
            # empty line: preserve it in the current item
            current_item.append("")

        else:
            # indent lower than initial one: end of section
            break

        index += 1

    if current_item:
        items.append("\n".join(current_item).rstrip("\n"))

    return items, index - 1


def _read_block(docstring: Docstring, offset: int) -> tuple[str, int]:
    lines = docstring.lines
    if offset >= len(lines):
        return "", offset

    index = offset
    block: list[str] = []

    # skip first empty lines
    while _is_empty_line(lines[index]):
        index += 1

    # get initial indent
    indent = len(lines[index]) - len(lines[index].lstrip())

    if indent == 0:
        # first non-empty line was not indented, abort
        return "", index - 1

    # start processing first item
    block.append(lines[index].lstrip())
    index += 1

    # loop on next lines
    while index < len(lines) and (lines[index].startswith(indent * " ") or _is_empty_line(lines[index])):
        block.append(lines[index][indent:])
        index += 1

    return "\n".join(block).rstrip("\n"), index - 1


def _read_parameters(docstring: Docstring, offset: int) -> tuple[list[DocstringParameter], int]:  # noqa: WPS231
    parameters = []
    type_: str
    annotation: str | None

    block, index = _read_block_items(docstring, offset)

    for arg_line in block:

        # check the presence of a name and description, separated by a semi-colon
        try:
            name_with_type, description = arg_line.split(":", 1)
        except ValueError:
            _warn(docstring, index, f"Failed to get 'name: description' pair from '{arg_line}'")
            continue

        description = description.lstrip()

        # use the type given after the parameter name, if any
        if " " in name_with_type:
            name, type_ = name_with_type.split(" ", 1)
            annotation = type_.strip("()")
            if annotation.endswith(", optional"):  # type: ignore
                annotation = annotation[:-10]  # type: ignore
        else:
            name = name_with_type
            # try to use the annotation from the signature
            try:
                annotation = docstring.parent.parameters[name].annotation  # type: ignore
            except (AttributeError, KeyError):
                annotation = None

        try:
            default = docstring.parent.parameters[name].default  # type: ignore
        except (AttributeError, KeyError):
            default = None

        if annotation is None:
            _warn(docstring, index, f"No type or annotation for parameter '{name}'")

        parameters.append(DocstringParameter(name=name, value=default, annotation=annotation, description=description))

    return parameters, index


def _read_parameters_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    parameters, index = _read_parameters(docstring, offset)

    if parameters:
        return DocstringSection(DocstringSectionKind.parameters, parameters), index

    _warn(docstring, index, f"Empty parameters section at line {offset}")
    return None, index


def _read_other_parameters_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    parameters, index = _read_parameters(docstring, offset)

    if parameters:
        return DocstringSection(DocstringSectionKind.other_parameters, parameters), index

    _warn(docstring, index, f"Empty keyword parameters section at line {offset}")
    return None, index


def _read_attributes_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    attributes = []
    block, index = _read_block_items(docstring, offset)

    annotation: str | None
    for attr_line in block:
        try:
            name_with_type, description = attr_line.split(":", 1)
        except ValueError:
            _warn(docstring, index, f"Failed to get 'name: description' pair from '{attr_line}'")
            continue

        description = description.lstrip()

        if " " in name_with_type:
            name, annotation = name_with_type.split(" ", 1)
            annotation = annotation.strip("()")
            if annotation.endswith(", optional"):
                annotation = annotation[:-10]
        else:
            name = name_with_type
            annotation = None

        attributes.append(DocstringAttribute(name=name, annotation=annotation, description=description))

    if attributes:
        return DocstringSection(DocstringSectionKind.attributes, attributes), index

    _warn(docstring, index, f"Empty attributes section at line {offset}")
    return None, index


def _read_raises_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    exceptions = []
    block, index = _read_block_items(docstring, offset)

    for exception_line in block:
        try:
            annotation, description = exception_line.split(": ", 1)
        except ValueError:
            _warn(docstring, index, f"Failed to get 'exception: description' pair from '{exception_line}'")
        else:
            exceptions.append(DocstringException(annotation=annotation, description=description.lstrip(" ")))

    if exceptions:
        return DocstringSection(DocstringSectionKind.raises, exceptions), index

    _warn(docstring, index, f"Empty exceptions section at line {offset}")
    return None, index


def _read_warns_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    warns = []
    block, index = _read_block_items(docstring, offset)

    for exception_line in block:
        try:
            annotation, description = exception_line.split(": ", 1)
        except ValueError:
            _warn(docstring, index, f"Failed to get 'warning: description' pair from '{exception_line}'")
        else:
            warns.append(DocstringWarn(annotation=annotation, description=description.lstrip(" ")))

    if warns:
        return DocstringSection(DocstringSectionKind.warns, warns), index

    _warn(docstring, index, f"Empty warns section at line {offset}")
    return None, index


def _read_returns_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    text, index = _read_block(docstring, offset)

    # early exit if there is no text in the return section
    if not text:
        _warn(docstring, index, f"Empty return section at line {offset}")
        return None, index

    # check the presence of a name and description, separated by a semi-colon
    try:
        type_, text = text.split(":", 1)
    except ValueError:
        description = text
        # try to use the annotation from the signature
        try:  # noqa: WPS505
            annotation = docstring.parent.returns  # type: ignore
        except AttributeError:
            annotation = None
    else:
        annotation = type_.lstrip()
        description = text.lstrip()

    # there was no type in the docstring and no return annotation in the signature
    if annotation is None:
        _warn(docstring, index, "No return type/annotation in docstring/signature")

    return (
        DocstringSection(DocstringSectionKind.returns, DocstringReturn(annotation=annotation, description=description)),
        index,
    )


def _read_yields_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    text, index = _read_block(docstring, offset)

    # early exit if there is no text in the yield section
    if not text:
        _warn(docstring, index, f"Empty yield section at line {offset}")
        return None, index

    # check the presence of a name and description, separated by a semi-colon
    try:
        type_, text = text.split(":", 1)
    except ValueError:
        description = text
        # try to use the annotation from the signature
        try:  # noqa: WPS505
            # TODO: handle Iterator and Generator types
            annotation = docstring.parent.returns  # type: ignore
        except AttributeError:
            annotation = None
    else:
        annotation = type_.lstrip()
        description = text.lstrip()

    # there was no type in the docstring and no return annotation in the signature
    if annotation is None:
        _warn(docstring, index, "No yield type/annotation in docstring/signature")

    return (
        DocstringSection(DocstringSectionKind.yields, DocstringYield(annotation=annotation, description=description)),
        index,
    )


def _read_receives_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    text, index = _read_block(docstring, offset)

    # early exit if there is no text in the receive section
    if not text:
        _warn(docstring, index, f"Empty receives section at line {offset}")
        return None, index

    # check the presence of a name and description, separated by a semi-colon
    try:
        type_, text = text.split(":", 1)
    except ValueError:
        description = text
        # try to use the annotation from the signature
        try:  # noqa: WPS505
            # TODO: handle Iterator and Generator types
            annotation = docstring.parent.returns  # type: ignore
        except AttributeError:
            annotation = None
    else:
        annotation = type_.lstrip()
        description = text.lstrip()

    # there was no type in the docstring and no return annotation in the signature
    if annotation is None:
        _warn(docstring, index, "No receive type/annotation in docstring/signature")

    return (
        DocstringSection(
            DocstringSectionKind.receives,
            DocstringReceive(annotation=annotation, description=description),
        ),
        index,
    )


def _read_examples_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:  # noqa: WPS231
    text, index = _read_block(docstring, offset)

    sub_sections = []
    in_code_example = False
    in_code_block = False
    current_text: list[str] = []
    current_example: list[str] = []

    for line in text.split("\n"):
        if _is_empty_line(line):
            if in_code_example:
                if current_example:
                    sub_sections.append((DocstringSectionKind.examples, "\n".join(current_example)))
                    current_example = []
                in_code_example = False
            else:
                current_text.append(line)

        elif in_code_example:
            current_example.append(line)

        elif line.startswith("```"):
            in_code_block = not in_code_block  # noqa: WPS434
            current_text.append(line)

        elif in_code_block:
            current_text.append(line)

        elif line.startswith(">>>"):
            if current_text:
                sub_sections.append((DocstringSectionKind.text, "\n".join(current_text).rstrip("\n")))
                current_text = []
            in_code_example = True
            current_example.append(line)

        else:
            current_text.append(line)

    if current_text:
        sub_sections.append((DocstringSectionKind.text, "\n".join(current_text).rstrip("\n")))
    elif current_example:
        sub_sections.append((DocstringSectionKind.examples, "\n".join(current_example)))

    if sub_sections:
        return DocstringSection(DocstringSectionKind.examples, sub_sections), index

    _warn(docstring, index, f"Empty examples section at line {offset}")
    return None, index


def _read_deprecated_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    text, index = _read_block(docstring, offset)

    # early exit if there is no text in the yield section
    if not text:
        _warn(docstring, index, f"Empty deprecated section at line {offset}")
        return None, index

    # check the presence of a name and description, separated by a semi-colon
    try:
        version, text = text.split(":", 1)
    except ValueError:
        _warn(docstring, index, f"Could not parse version, text at line {offset}")
        return None, index

    version = version.lstrip()
    description = text.lstrip()

    return (
        DocstringSection(DocstringSectionKind.deprecated, (version, description)),
        index,
    )


def _is_empty_line(line) -> bool:
    return not line.strip()


_section_reader = {
    DocstringSectionKind.parameters: _read_parameters_section,
    DocstringSectionKind.other_parameters: _read_other_parameters_section,
    DocstringSectionKind.raises: _read_raises_section,
    DocstringSectionKind.warns: _read_warns_section,
    DocstringSectionKind.examples: _read_examples_section,
    DocstringSectionKind.attributes: _read_attributes_section,
    DocstringSectionKind.returns: _read_returns_section,
    DocstringSectionKind.yields: _read_yields_section,
    DocstringSectionKind.receives: _read_receives_section,
    DocstringSectionKind.deprecated: _read_deprecated_section,
}


def parse(  # noqa: WPS231
    docstring: Docstring,
    **options: Any,
) -> list[DocstringSection]:
    """Parse a docstring.

    This function iterates on lines of a docstring to build sections.
    It then returns this list of sections.

    Parameters:
        docstring: The docstring to parse.
        **options: Additional parsing options.

    Returns:
        A list of docstring sections.
    """
    sections = []
    current_section = []

    in_code_block = False

    lines = docstring.lines
    index = 0

    while index < len(lines):
        line_lower = lines[index].lower()

        if in_code_block:
            if line_lower.lstrip(" ").startswith("```"):
                in_code_block = False
            current_section.append(lines[index])

        elif line_lower.lstrip(" ").startswith("```"):
            in_code_block = True
            current_section.append(lines[index])

        elif match := _RE_ADMONITION.match(lines[index]):  # noqa: WPS332
            groups = match.groupdict()
            admonition_type = groups["type"].lower()
            if admonition_type in _section_kind:
                if current_section:
                    if any(current_section):
                        sections.append(
                            DocstringSection(
                                DocstringSectionKind.text,
                                "\n".join(current_section).rstrip("\n"),
                                title=groups["title"],
                            )
                        )
                    current_section = []
                reader = _section_reader[_section_kind[admonition_type]]
                section, index = reader(docstring, index + 1)
                if section:
                    sections.append(section)

            else:
                contents, index = _read_block(docstring, index + 1)
                if contents:
                    sections.append(
                        DocstringSection(
                            kind=DocstringSectionKind.admonition,
                            value=DocstringAdmonition(kind=admonition_type, contents=contents),
                            title=groups["title"],
                        )
                    )
                else:
                    index -= 1
                    current_section.append(lines[index])
        else:
            current_section.append(lines[index])

        index += 1

    if current_section:
        sections.append(DocstringSection(DocstringSectionKind.text, "\n".join(current_section).rstrip("\n")))

    return sections
