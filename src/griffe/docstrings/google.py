"""This module defines functions and classes to parse Google-style docstrings into structured data."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Pattern

from griffe.docstrings.dataclasses import (
    DocstringArgument,
    DocstringAttribute,
    DocstringException,
    DocstringReturn,
    DocstringSection,
    DocstringSectionKind,
    DocstringYield,
)
from griffe.logger import get_logger

if TYPE_CHECKING:
    from griffe.dataclasses import Docstring

logger = get_logger(__name__)


section_kind = {
    "args:": DocstringSectionKind.arguments,
    "arguments:": DocstringSectionKind.arguments,
    "params:": DocstringSectionKind.arguments,
    "parameters:": DocstringSectionKind.arguments,
    "keyword args:": DocstringSectionKind.keyword_arguments,
    "keyword arguments:": DocstringSectionKind.keyword_arguments,
    "raises:": DocstringSectionKind.raises,
    "exceptions:": DocstringSectionKind.raises,
    "returns:": DocstringSectionKind.returns,
    "yields:": DocstringSectionKind.yields,
    "examples:": DocstringSectionKind.examples,
    "attributes:": DocstringSectionKind.attributes,
}

RE_GOOGLE_STYLE_ADMONITION: Pattern = re.compile(r"^(?P<indent>\s*)(?P<type>[\w-]+):((?:\s+)(?P<title>.+))?$")
"""Regular expressions to match lines starting admonitions, of the form `TYPE: [TITLE]`."""


def read_block_items(lines: list[str], start_index: int) -> tuple[list[str], int]:  # noqa: WPS231
    """
    Parse an indented block as a list of items.

    The first indentation level is used as a reference to determine if the next lines are new items
    or continuation lines.

    Arguments:
        lines: The block lines.
        start_index: The line number to start at.

    Returns:
        A tuple containing the list of concatenated lines and the index at which to continue parsing.
    """
    if start_index >= len(lines):
        return [], start_index

    index = start_index
    items: list[str] = []

    # skip first empty lines
    while is_empty_line(lines[index]):
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
            # indent between initial and continuation: append but add error
            cont_indent = len(line) - len(line.lstrip())
            current_item.append(line[cont_indent:])
            logger.warning(
                f"Confusing indentation for continuation line {index+1} in docstring, "
                f"should be {indent} * 2 = {indent*2} spaces, not {cont_indent}"
            )

        elif line.startswith(indent * " "):
            # indent equal to initial one: new item
            items.append("\n".join(current_item))
            current_item = [line[indent:]]

        elif is_empty_line(line):
            # empty line: preserve it in the current item
            current_item.append("")

        else:
            # indent lower than initial one: end of section
            break

        index += 1

    if current_item:
        items.append("\n".join(current_item).rstrip("\n"))

    return items, index - 1


def read_block(lines: list[str], start_index: int) -> tuple[str, int]:
    """
    Parse an indented block.

    Arguments:
        lines: The block lines.
        start_index: The line number to start at.

    Returns:
        A tuple containing the list of lines and the index at which to continue parsing.
    """
    if start_index >= len(lines):
        return "", start_index

    index = start_index
    block: list[str] = []

    # skip first empty lines
    while is_empty_line(lines[index]):
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
    while index < len(lines) and (lines[index].startswith(indent * " ") or is_empty_line(lines[index])):
        block.append(lines[index][indent:])
        index += 1

    return "\n".join(block).rstrip("\n"), index - 1


def read_arguments(lines: list[str], start_index: int) -> tuple[list[DocstringArgument], int]:  # noqa: WPS231
    """
    Parse an "Arguments" or "Keyword Arguments" section.

    Arguments:
        lines: The parameters block lines.
        start_index: The line number to start at.

    Returns:
        A tuple containing a list of docstring arguments and the index at which to continue parsing.
    """
    parameters = []
    type_: Any
    block, index = read_block_items(lines, start_index)

    for param_line in block:

        # Check that there is an annotation in the docstring
        try:
            name_with_type, description = param_line.split(":", 1)
        except ValueError:
            logger.warning(f"Failed to get 'name: description' pair from '{param_line}'")
            continue

        # Setting defaults
        default = None
        annotation = None
        # Can only get description from docstring - keep if no type was given
        description = description.lstrip()

        # If we have managed to find a type in the docstring use this
        if " " in name_with_type:
            name, type_ = name_with_type.split(" ", 1)
            annotation = type_.strip("()")
            if annotation.endswith(", optional"):  # type: ignore
                annotation = annotation[:-10]  # type: ignore
        # Otherwise try to use the signature as `annotation` would still be empty
        else:
            name = name_with_type

        # Check in the signature to get extra details
        # logger.warning(f"No type annotation for parameter '{name}'")
        # If signature_param.X are empty it doesnt matter as defaults are empty anyway

        parameters.append(DocstringArgument(name=name, value=default, annotation=annotation, description=description))

    return parameters, index


def read_arguments_section(lines: list[str], start_index: int) -> tuple[DocstringSection | None, int]:
    """
    Parse an "Arguments" section.

    Arguments:
        lines: The parameters block lines.
        start_index: The line number to start at.

    Returns:
        A tuple containing a `Section` (or `None`) and the index at which to continue parsing.
    """
    parameters, index = read_arguments(lines, start_index)

    if parameters:
        return DocstringSection(DocstringSectionKind.arguments, parameters), index

    logger.warning(f"Empty parameters section at line {start_index}")
    return None, index


def read_keyword_arguments_section(lines: list[str], start_index: int) -> tuple[DocstringSection | None, int]:
    """
    Parse a "Keyword Arguments" section.

    Arguments:
        lines: The parameters block lines.
        start_index: The line number to start at.

    Returns:
        A tuple containing a `Section` (or `None`) and the index at which to continue parsing.
    """
    parameters, index = read_arguments(lines, start_index)

    if parameters:
        return DocstringSection(DocstringSectionKind.keyword_arguments, parameters), index

    logger.warning(f"Empty keyword arguments section at line {start_index}")
    return None, index


def read_attributes_section(lines: list[str], start_index: int) -> tuple[DocstringSection | None, int]:
    """
    Parse an "Attributes" section.

    Arguments:
        lines: The parameters block lines.
        start_index: The line number to start at.

    Returns:
        A tuple containing a `Section` (or `None`) and the index at which to continue parsing.
    """
    attributes = []
    block, index = read_block_items(lines, start_index)

    annotation: str | None
    for attr_line in block:
        try:
            name_with_type, description = attr_line.split(":", 1)
        except ValueError:
            logger.warning(f"Failed to get 'name: description' pair from '{attr_line}'")
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

    logger.warning(f"Empty attributes section at line {start_index}")
    return None, index


def read_raises_section(lines: list[str], start_index: int) -> tuple[DocstringSection | None, int]:
    """
    Parse a "Raises" section.

    Arguments:
        lines: The exceptions block lines.
        start_index: The line number to start at.

    Returns:
        A tuple containing a `Section` (or `None`) and the index at which to continue parsing.
    """
    exceptions = []
    block, index = read_block_items(lines, start_index)

    for exception_line in block:
        try:
            annotation, description = exception_line.split(": ", 1)
        except ValueError:
            logger.warning(f"Failed to get 'exception: description' pair from '{exception_line}'")
        else:
            exceptions.append(DocstringException(annotation, description.lstrip(" ")))

    if exceptions:
        return DocstringSection(DocstringSectionKind.raises, exceptions), index

    logger.warning(f"Empty exceptions section at line {start_index}")
    return None, index


def read_returns_section(lines: list[str], start_index: int) -> tuple[DocstringSection | None, int]:
    """
    Parse an "Returns" section.

    Arguments:
        lines: The return block lines.
        start_index: The line number to start at.

    Returns:
        A tuple containing a `Section` (or `None`) and the index at which to continue parsing.
    """
    text, index = read_block(lines, start_index)

    # Early exit if there is no text in the return section
    if not text:
        logger.warning(f"Empty return section at line {start_index}")
        return None, index

    # First try to get the annotation and description from the docstring
    try:
        type_, text = text.split(":", 1)
    except ValueError:
        description = text
        annotation = None
    else:
        annotation = type_.lstrip()
        description = text.lstrip()

    # There was no type in the docstring and no annotation
    if annotation is None:
        logger.warning("No return type/annotation in docstring/signature")

    return DocstringSection(DocstringSectionKind.returns, DocstringReturn(annotation, description)), index


def read_yields_section(lines: list[str], start_index: int) -> tuple[DocstringSection | None, int]:
    """
    Parse a "Yields" section.

    Arguments:
        lines: The return block lines.
        start_index: The line number to start at.

    Returns:
        A tuple containing a `Section` (or `None`) and the index at which to continue parsing.
    """
    text, index = read_block(lines, start_index)

    # Early exit if there is no text in the yield section
    if not text:
        logger.warning(f"Empty yield section at line {start_index}")
        return None, index

    # First try to get the annotation and description from the docstring
    try:
        type_, text = text.split(":", 1)
    except ValueError:
        description = text
        annotation = None
    else:
        annotation = type_.lstrip()
        description = text.lstrip()

    # There was no type in the docstring and no annotation
    if annotation is None:
        logger.warning("No yield type/annotation in docstring/signature")

    return DocstringSection(DocstringSectionKind.yields, DocstringYield(annotation, description)), index


def read_examples_section(lines: list[str], start_index: int) -> tuple[DocstringSection | None, int]:  # noqa: WPS231
    """
    Parse an "examples" section.

    Arguments:
        lines: The examples block lines.
        start_index: The line number to start at.

    Returns:
        A tuple containing a `Section` (or `None`) and the index at which to continue parsing.
    """
    text, index = read_block(lines, start_index)

    sub_sections = []
    in_code_example = False
    in_code_block = False
    current_text: list[str] = []
    current_example: list[str] = []

    for line in text.split("\n"):
        if is_empty_line(line):
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

    logger.warning(f"Empty examples section at line {start_index}")
    return None, index


def is_empty_line(line) -> bool:
    """
    Tell if a line is empty.

    Arguments:
        line: The line to check.

    Returns:
        True if the line is empty or composed of blanks only, False otherwise.
    """
    return not line.strip()


section_reader = {
    DocstringSectionKind.arguments: read_arguments_section,
    DocstringSectionKind.keyword_arguments: read_keyword_arguments_section,
    DocstringSectionKind.raises: read_raises_section,
    DocstringSectionKind.examples: read_examples_section,
    DocstringSectionKind.attributes: read_attributes_section,
    DocstringSectionKind.returns: read_returns_section,
    DocstringSectionKind.yields: read_yields_section,
}


def parse(  # noqa: WPS231
    docstring: Docstring,
    replace_admonitions: bool = True,
) -> list[DocstringSection]:
    """Parse a docstring.

    This function iterates on lines of a docstring to build sections.
    It then returns this list of sections.

    Arguments:
        docstring: The docstring to parse.
        replace_admonitions: Whether to replace unknown-titled sections
            with their Markdown admonition equivalent.

    Returns:
        The list of parsed sections.
    """
    sections = []
    current_section = []

    in_code_block = False

    lines = docstring.value.split("\n")
    index = 0

    while index < len(lines):
        line_lower = lines[index].lower()

        if in_code_block:
            if line_lower.lstrip(" ").startswith("```"):
                in_code_block = False
            current_section.append(lines[index])

        elif line_lower in section_kind:
            if current_section:
                if any(current_section):
                    sections.append(
                        DocstringSection(DocstringSectionKind.text, "\n".join(current_section).rstrip("\n"))
                    )
                current_section = []
            reader = section_reader[section_kind[line_lower]]
            section, index = reader(lines, index + 1)
            if section:
                sections.append(section)

        elif line_lower.lstrip(" ").startswith("```"):
            in_code_block = True
            current_section.append(lines[index])

        else:
            if replace_admonitions and not in_code_block and index + 1 < len(lines):
                if match := RE_GOOGLE_STYLE_ADMONITION.match(lines[index]):  # noqa: WPS332
                    groups = match.groupdict()
                    indent = groups["indent"]
                    if lines[index + 1].startswith(indent + " " * 4):
                        lines[index] = f"{indent}!!! {groups['type'].lower()}"
                        if groups["title"]:
                            lines[index] += f' "{groups["title"]}"'
            current_section.append(lines[index])

        index += 1

    if current_section:
        sections.append(DocstringSection(DocstringSectionKind.text, "\n".join(current_section).rstrip("\n")))

    return sections
