"""This module defines functions to parse Google-style docstrings into structured data."""

from __future__ import annotations

import re
from ast import PyCF_ONLY_AST
from contextlib import suppress
from typing import TYPE_CHECKING, Any, List, Pattern, Tuple

from griffe.agents.nodes import get_annotation
from griffe.docstrings.dataclasses import (
    DocstringAdmonition,
    DocstringAttribute,
    DocstringParameter,
    DocstringRaise,
    DocstringReceive,
    DocstringReturn,
    DocstringSection,
    DocstringSectionKind,
    DocstringWarn,
    DocstringYield,
)
from griffe.docstrings.utils import warning
from griffe.expressions import Expression, Name

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

BlockItem = Tuple[int, List[str]]
BlockItems = List[BlockItem]
ItemsBlock = Tuple[BlockItems, int]

_RE_ADMONITION: Pattern = re.compile(r"^(?P<type>[\w][\s\w-]*):(\s+(?P<title>.+))?$", re.I)
"""Regular expression to match admonitions, of the form `TYPE: [TITLE]`."""

_RE_NAME_ANNOTATION_DESCRIPTION: Pattern = re.compile(r"^(?:(?P<name>\w+)?\s*(?:\((?P<type>.+)\))?:\s*)?(?P<desc>.*)$")
"""Regular expression to match `name (type): Description` in docstrings sections items."""


def _read_block_items(docstring: Docstring, offset: int) -> ItemsBlock:  # noqa: WPS231
    lines = docstring.lines
    if offset >= len(lines):
        return [], offset

    new_offset = offset
    items: BlockItems = []

    # skip first empty lines
    while _is_empty_line(lines[new_offset]):
        new_offset += 1

    # get initial indent
    indent = len(lines[new_offset]) - len(lines[new_offset].lstrip())

    if indent == 0:
        # first non-empty line was not indented, abort
        return [], new_offset - 1

    # start processing first item
    current_item = (new_offset, [lines[new_offset][indent:]])
    new_offset += 1

    # loop on next lines
    while new_offset < len(lines):
        line = lines[new_offset]

        if line.startswith(indent * 2 * " "):
            # continuation line
            current_item[1].append(line[indent * 2 :])

        elif line.startswith((indent + 1) * " "):
            # indent between initial and continuation: append but warn
            cont_indent = len(line) - len(line.lstrip())
            current_item[1].append(line[cont_indent:])
            _warn(
                docstring,
                new_offset,
                f"Confusing indentation for continuation line {new_offset+1} in docstring, "
                f"should be {indent} * 2 = {indent*2} spaces, not {cont_indent}",
            )

        elif line.startswith(indent * " "):
            # indent equal to initial one: new item
            items.append(current_item)
            current_item = (new_offset, [line[indent:]])

        elif _is_empty_line(line):
            # empty line: preserve it in the current item
            current_item[1].append("")

        else:
            # indent lower than initial one: end of section
            break

        new_offset += 1

    if current_item:
        items.append(current_item)

    return items, new_offset - 1


def _read_block(docstring: Docstring, offset: int) -> tuple[str, int]:
    lines = docstring.lines
    if offset >= len(lines):
        return "", offset

    new_offset = offset
    block: list[str] = []

    # skip first empty lines
    while _is_empty_line(lines[new_offset]):
        new_offset += 1

    # get initial indent
    indent = len(lines[new_offset]) - len(lines[new_offset].lstrip())

    if indent == 0:
        # first non-empty line was not indented, abort
        return "", new_offset - 1

    # start processing first item
    block.append(lines[new_offset].lstrip())
    new_offset += 1

    # loop on next lines
    while new_offset < len(lines) and (lines[new_offset].startswith(indent * " ") or _is_empty_line(lines[new_offset])):
        block.append(lines[new_offset][indent:])
        new_offset += 1

    return "\n".join(block).rstrip("\n"), new_offset - 1


def _read_parameters(docstring: Docstring, offset: int) -> tuple[list[DocstringParameter], int]:  # noqa: WPS231
    parameters = []
    annotation: str | Name | Expression | None

    block, new_offset = _read_block_items(docstring, offset)

    for line_number, param_lines in block:

        # check the presence of a name and description, separated by a semi-colon
        try:
            name_with_type, description = param_lines[0].split(":", 1)
        except ValueError:
            _warn(docstring, line_number, f"Failed to get 'name: description' pair from '{param_lines[0]}'")
            continue

        description = "\n".join([description.lstrip(), *param_lines[1:]]).rstrip("\n")

        # use the type given after the parameter name, if any
        if " " in name_with_type:
            name, annotation = name_with_type.split(" ", 1)
            annotation = annotation.strip("()")
            if annotation.endswith(", optional"):
                annotation = annotation[:-10]
            # try to compile the annotation to transform it into an expression
            with suppress(SyntaxError, AttributeError):
                code = compile(annotation, mode="eval", filename="", flags=PyCF_ONLY_AST, optimize=2)
                annotation = code.body and get_annotation(code.body, parent=docstring.parent)  # type: ignore[arg-type]
        else:
            name = name_with_type
            # try to use the annotation from the signature
            try:
                annotation = docstring.parent.parameters[name].annotation  # type: ignore[union-attr]
            except (AttributeError, KeyError):
                annotation = None

        try:
            default = docstring.parent.parameters[name].default  # type: ignore[union-attr]
        except (AttributeError, KeyError):
            default = None

        if annotation is None:
            _warn(docstring, line_number, f"No type or annotation for parameter '{name}'")

        parameters.append(DocstringParameter(name=name, value=default, annotation=annotation, description=description))

    return parameters, new_offset


def _read_parameters_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    parameters, new_offset = _read_parameters(docstring, offset)

    if parameters:
        return DocstringSection(DocstringSectionKind.parameters, parameters), new_offset

    _warn(docstring, new_offset, f"Empty parameters section at line {offset}")
    return None, new_offset


def _read_other_parameters_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    parameters, new_offset = _read_parameters(docstring, offset)

    if parameters:
        return DocstringSection(DocstringSectionKind.other_parameters, parameters), new_offset

    _warn(docstring, new_offset, f"Empty other parameters section at line {offset}")
    return None, new_offset


def _read_attributes_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:  # noqa: WPS231
    attributes = []
    block, new_offset = _read_block_items(docstring, offset)

    annotation: str | Name | Expression | None
    for line_number, attr_lines in block:
        try:
            name_with_type, description = attr_lines[0].split(":", 1)
        except ValueError:
            _warn(docstring, line_number, f"Failed to get 'name: description' pair from '{attr_lines[0]}'")
            continue

        description = "\n".join([description.lstrip(), *attr_lines[1:]]).rstrip("\n")

        if " " in name_with_type:
            name, annotation = name_with_type.split(" ", 1)
            annotation = annotation.strip("()")
            if annotation.endswith(", optional"):
                annotation = annotation[:-10]
            # try to compile the annotation to transform it into an expression
            with suppress(SyntaxError):
                code = compile(annotation, mode="eval", filename="", flags=PyCF_ONLY_AST, optimize=2)
                annotation = code.body and get_annotation(code.body, parent=docstring.parent)  # type: ignore[arg-type]
        else:
            name = name_with_type
            try:
                annotation = docstring.parent.attributes[name].annotation  # type: ignore[union-attr]
            except (AttributeError, KeyError):
                annotation = None

        attributes.append(DocstringAttribute(name=name, annotation=annotation, description=description))

    if attributes:
        return DocstringSection(DocstringSectionKind.attributes, attributes), new_offset

    _warn(docstring, new_offset, f"Empty attributes section at line {offset}")
    return None, new_offset


def _read_raises_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    exceptions = []
    block, new_offset = _read_block_items(docstring, offset)

    for line_number, exception_lines in block:
        try:
            annotation, description = exception_lines[0].split(": ", 1)
        except ValueError:
            _warn(docstring, line_number, f"Failed to get 'exception: description' pair from '{exception_lines[0]}'")
        else:
            description = "\n".join([description.lstrip(), *exception_lines[1:]]).rstrip("\n")
            exceptions.append(DocstringRaise(annotation=annotation, description=description))

    if exceptions:
        return DocstringSection(DocstringSectionKind.raises, exceptions), new_offset

    _warn(docstring, new_offset, f"Empty exceptions section at line {offset}")
    return None, new_offset


def _read_warns_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    warns = []
    block, new_offset = _read_block_items(docstring, offset)

    for line_number, warning_lines in block:
        try:
            annotation, description = warning_lines[0].split(": ", 1)
        except ValueError:
            _warn(docstring, line_number, f"Failed to get 'warning: description' pair from '{warning_lines[0]}'")
        else:
            description = "\n".join([description.lstrip(), *warning_lines[1:]]).rstrip("\n")
            warns.append(DocstringWarn(annotation=annotation, description=description))

    if warns:
        return DocstringSection(DocstringSectionKind.warns, warns), new_offset

    _warn(docstring, new_offset, f"Empty warns section at line {offset}")
    return None, new_offset


def _read_returns_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:  # noqa: WPS231
    returns = []
    block, new_offset = _read_block_items(docstring, offset)

    for index, (line_number, return_lines) in enumerate(block):
        match = _RE_NAME_ANNOTATION_DESCRIPTION.match(return_lines[0])
        if not match:
            _warn(docstring, line_number, f"Failed to get name, annotation or description from '{return_lines[0]}'")
            continue

        name, annotation, description = match.groups()
        description = "\n".join([description.lstrip(), *return_lines[1:]]).rstrip("\n")

        if annotation and docstring.parent is not None:
            # try to compile the annotation to transform it into an expression
            with suppress(SyntaxError):
                code = compile(annotation, mode="eval", filename="", flags=PyCF_ONLY_AST, optimize=2)
                annotation = code.body and get_annotation(code.body, parent=docstring.parent)  # type: ignore[arg-type]
        else:
            # try to retrieve the annotation from the docstring parent
            with suppress(AttributeError, KeyError):
                annotation = docstring.parent.returns  # type: ignore[union-attr]
                if len(block) > 1:
                    if annotation.is_tuple:
                        annotation = annotation.tuple_item(index)

            if annotation is None:
                returned_value = repr(name) or index
                _warn(docstring, line_number, f"No type or annotation for returned value {returned_value}")

        returns.append(DocstringReturn(name=name or "", annotation=annotation, description=description))

    if returns:
        return DocstringSection(DocstringSectionKind.returns, returns), new_offset

    _warn(docstring, new_offset, f"Empty returns section at line {offset}")
    return None, new_offset


def _read_yields_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:  # noqa: WPS231
    yields = []
    block, new_offset = _read_block_items(docstring, offset)

    for index, (line_number, yield_lines) in enumerate(block):  # noqa: B007 (will be used later)
        match = _RE_NAME_ANNOTATION_DESCRIPTION.match(yield_lines[0])
        if not match:
            _warn(docstring, line_number, f"Failed to get name, annotation or description from '{yield_lines[0]}'")
            continue

        name, annotation, description = match.groups()
        description = "\n".join([description.lstrip(), *yield_lines[1:]]).rstrip("\n")

        if annotation and docstring.parent is not None:
            # try to compile the annotation to transform it into an expression
            with suppress(SyntaxError):
                code = compile(annotation, mode="eval", filename="", flags=PyCF_ONLY_AST, optimize=2)
                annotation = code.body and get_annotation(code.body, parent=docstring.parent)  # type: ignore[arg-type]
        else:
            # try to retrieve the annotation from the docstring parent
            with suppress(AttributeError, KeyError):
                annotation = docstring.parent.returns  # type: ignore[union-attr]
                # TODO: support getting yield part and exploding tuple (in a generator/iterator)
                # if len(block) > 1:
                #     if annotation.is_tuple:
                #         annotation = annotation.tuple_item(index)

            if annotation is None:
                yielded_value = repr(name) or index
                _warn(docstring, line_number, f"No type or annotation for yielded value {yielded_value}")

        yields.append(DocstringYield(name=name or "", annotation=annotation, description=description))

    if yields:
        return DocstringSection(DocstringSectionKind.yields, yields), new_offset

    _warn(docstring, new_offset, f"Empty yields section at line {offset}")
    return None, new_offset


def _read_receives_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:  # noqa: WPS231
    receives = []
    block, new_offset = _read_block_items(docstring, offset)

    for index, (line_number, receive_lines) in enumerate(block):  # noqa: B007 (will be used later)
        match = _RE_NAME_ANNOTATION_DESCRIPTION.match(receive_lines[0])
        if not match:
            _warn(docstring, line_number, f"Failed to get name, annotation or description from '{receive_lines[0]}'")
            continue

        name, annotation, description = match.groups()
        description = "\n".join([description.lstrip(), *receive_lines[1:]]).rstrip("\n")

        if annotation and docstring.parent is not None:
            # try to compile the annotation to transform it into an expression
            with suppress(SyntaxError):
                code = compile(annotation, mode="eval", filename="", flags=PyCF_ONLY_AST, optimize=2)
                annotation = code.body and get_annotation(code.body, parent=docstring.parent)  # type: ignore[arg-type]
        # else:
        # try to retrieve the annotation from the docstring parent
        # TODO: support getting receive part and exploding tuple (in a generator/iterator)
        # with suppress(AttributeError, KeyError):
        #     annotation = docstring.parent.returns  # type: ignore[union-attr]
        #     if len(block) > 1:
        #         if annotation.is_tuple:
        #             annotation = annotation.tuple_item(index)

        if annotation is None:
            received_value = repr(name) or index
            _warn(docstring, line_number, f"No type or annotation for received value {received_value}")

        receives.append(DocstringReceive(name=name or "", annotation=annotation, description=description))

    if receives:
        return DocstringSection(DocstringSectionKind.receives, receives), new_offset

    _warn(docstring, new_offset, f"Empty receives section at line {offset}")
    return None, new_offset


def _read_examples_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:  # noqa: WPS231
    text, new_offset = _read_block(docstring, offset)

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
        return DocstringSection(DocstringSectionKind.examples, sub_sections), new_offset

    _warn(docstring, new_offset, f"Empty examples section at line {offset}")
    return None, new_offset


def _read_deprecated_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    text, new_offset = _read_block(docstring, offset)

    # early exit if there is no text in the yield section
    if not text:
        _warn(docstring, new_offset, f"Empty deprecated section at line {offset}")
        return None, new_offset

    # check the presence of a name and description, separated by a semi-colon
    try:
        version, text = text.split(":", 1)
    except ValueError:
        _warn(docstring, new_offset, f"Could not parse version, text at line {offset}")
        return None, new_offset

    version = version.lstrip()
    description = text.lstrip()

    return (
        DocstringSection(DocstringSectionKind.deprecated, (version, description)),
        new_offset,
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
    offset = 0

    while offset < len(lines):
        line_lower = lines[offset].lower()

        if in_code_block:
            if line_lower.lstrip(" ").startswith("```"):
                in_code_block = False
            current_section.append(lines[offset])

        elif line_lower.lstrip(" ").startswith("```"):
            in_code_block = True
            current_section.append(lines[offset])

        else:
            # TODO: once Python 3.7 is dropped, use walrus operator
            match = _RE_ADMONITION.match(lines[offset])
            if match:
                groups = match.groupdict()
                admonition_type = groups["type"].lower()
                if admonition_type in _section_kind:
                    if current_section:
                        if any(current_section):
                            sections.append(
                                DocstringSection(
                                    DocstringSectionKind.text,
                                    "\n".join(current_section).rstrip("\n"),
                                )
                            )
                        current_section = []
                    reader = _section_reader[_section_kind[admonition_type]]
                    section, offset = reader(docstring, offset + 1)
                    if section:
                        section.title = groups["title"]
                        sections.append(section)

                else:
                    contents, offset = _read_block(docstring, offset + 1)
                    if contents:
                        sections.append(
                            DocstringSection(
                                kind=DocstringSectionKind.admonition,
                                value=DocstringAdmonition(kind=admonition_type, contents=contents),
                                title=groups["title"],
                            )
                        )
                    else:
                        with suppress(IndexError):
                            current_section.append(lines[offset])
            else:
                current_section.append(lines[offset])

        offset += 1

    if current_section:
        sections.append(DocstringSection(DocstringSectionKind.text, "\n".join(current_section).rstrip("\n")))

    return sections
