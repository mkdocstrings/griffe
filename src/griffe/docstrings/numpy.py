"""This module defines functions to parse Numpy-style docstrings into structured data.

Based on https://numpydoc.readthedocs.io/en/latest/format.html,
it seems Numpydoc is a superset of RST.
Since fully parsing RST is a non-goal of this project,
some things are stripped from the Numpydoc specification.

Rejected as non particularly Pythonic or useful as sections:

- See also: this section feels too subjective (specially crafted as a standard for Numpy itself),
    and there are may ways to reference related items in a docstring, depending on the chosen markup.
- Methods: with a good documentation renderer, methods are easily made accessible or hidden.
    Griffe also has a goal of making the merging of inherited methods configurable (on/off).

Rejected as naturally handled by the user-chosen markup:

- Warnings: this is just markup.
- Notes: again, just markup.
- References: again, just markup.

---

The following sections are supported:

- Deprecated (revisited): we expect a title instead of an RST directive.
    Python has support for deprecating things, so it feels natural
    to structure deprecations.
- Parameters: obviously.
- Returns: obviously.
- Yields: obviously.
- Receives: less used than Yields, but very natural/Pythonic as well.
- Other parameters: used here as documentation for keyword parameters.
- Raises: obviously.
- Warns: less used than Raises, but very natural/Pythonic as well.
- Examples: obviously. Special handling for non-code-blocks `>>>`.
- Attributes: obviously.
"""

from __future__ import annotations

import re
from contextlib import suppress
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Pattern

from griffe.docstrings.dataclasses import (
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
    "deprecated": DocstringSectionKind.deprecated,
    "parameters": DocstringSectionKind.parameters,
    "other parameters": DocstringSectionKind.other_parameters,
    "returns": DocstringSectionKind.returns,
    "yields": DocstringSectionKind.yields,
    "receives": DocstringSectionKind.receives,
    "raises": DocstringSectionKind.raises,
    "warns": DocstringSectionKind.warns,
    "examples": DocstringSectionKind.examples,
    "attributes": DocstringSectionKind.attributes,
}


def _is_empty_line(line) -> bool:
    return not line.strip()


def _is_dash_line(line) -> bool:
    return not _is_empty_line(line) and _is_empty_line(line.replace("-", ""))


def _read_block_items(docstring: Docstring, offset: int) -> tuple[list[list[str]], int]:  # noqa: WPS231
    lines = docstring.lines
    if offset >= len(lines):
        return [], offset

    index = offset
    items: list[list[str]] = []

    # skip first empty lines
    while _is_empty_line(lines[index]):
        index += 1

    previous_was_empty = False

    # start processing first item
    current_item = [lines[index]]
    index += 1

    # loop on next lines
    while index < len(lines):
        line = lines[index]

        if line.startswith(4 * " "):
            # continuation line
            current_item.append(line.lstrip())
            previous_was_empty = False

        elif line.startswith(" "):
            # indent between initial and continuation: append but warn
            cont_indent = len(line) - len(line.lstrip())
            current_item.append(line[cont_indent:])
            _warn(
                docstring,
                index,
                f"Confusing indentation for continuation line {index+1} in docstring, "
                f"should be 4 spaces, not {cont_indent}",
            )
            previous_was_empty = False

        elif _is_empty_line(line):
            # empty line: preserve it in the current item
            current_item.append("")
            previous_was_empty = True

        else:
            if previous_was_empty:
                break
            # new item
            items.append(current_item)
            current_item = [line]
            previous_was_empty = False

        index += 1

    if current_item:
        items.append(current_item)

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

    while index < len(lines) and not (_is_empty_line(lines[index]) and _is_dash_line(lines[index + 1])):
        block.append(lines[index])
        index += 1

    return "\n".join(block).rstrip("\n"), index - 1


_RE_OB: str = r"\{"  # opening bracket
_RE_CB: str = r"\}"  # closing bracket
_RE_NAME: str = r"[_a-z][_a-z0-9]*"
_RE_NATURAL_TYPE: str = r"[_a-z0-9 ().'\"-]+"
_RE_RETURNS: Pattern = re.compile(rf"^(?:(?P<name>{_RE_NAME}) : )?(?P<type>{_RE_NATURAL_TYPE})", re.IGNORECASE)
_RE_YIELDS: Pattern = _RE_RETURNS
_RE_RECEIVES: Pattern = _RE_YIELDS
_RE_PARAMETER: Pattern = re.compile(
    rf"""
    (?P<names>{_RE_NAME}(?:,\s{_RE_NAME})*)
    (?:
        \s:\s
        (?:
            (?:{_RE_OB}(?P<choices>.+){_RE_CB})|
            (?:
                (?P<type>{_RE_NATURAL_TYPE})
                (?:,\soptional)?
                (?:
                    ,\sdefault\s*[:=]\s*
                    (?P<default>.+)
                )?
            )
        )
    )?
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _read_parameters(docstring: Docstring, offset: int) -> tuple[list[DocstringParameter], int]:  # noqa: WPS231
    parameters = []
    annotation: str | Name | Expression | None

    items, index = _read_block_items(docstring, offset)

    for item in items:

        match = _RE_PARAMETER.match(item[0])
        if not match:
            _warn(docstring, index, f"Could not parse line '{item[0]}'")
            continue

        names = match.group("names").split(", ")
        annotation = match.group("type")
        choices = match.group("choices")
        if choices:
            choices = choices.split(", ", 1)
            default = choices[0]
        else:
            default = match.group("default")
        if len(item) > 1:
            description = "\n".join(item[1:]).rstrip()
        else:
            description = ""

        if annotation is None:
            # try to use the annotation from the signature
            for name in names:
                with suppress(AttributeError, KeyError):
                    annotation = docstring.parent.parameters[name].annotation  # type: ignore[union-attr]
                    break
            else:
                _warn(docstring, index, f"No types or annotations for parameters {names}")

        if default is None:
            for name in names:
                try:
                    default = docstring.parent.parameters[name].default  # type: ignore[union-attr]
                    break
                except (AttributeError, KeyError):
                    pass

        for name in names:
            parameters.append(DocstringParameter(name, value=default, annotation=annotation, description=description))

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

    _warn(docstring, index, f"Empty other parameters section at line {offset}")
    return None, index


def _read_deprecated_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    # deprecated
    # SINCE_VERSION
    #     TEXT?
    items, index = _read_block_items(docstring, offset)

    if not items:
        _warn(docstring, index, f"Empty deprecated section at line {offset}")
        return None, index

    if len(items) > 1:
        _warn(docstring, index, f"Too many deprecated items at {offset}")

    item = items[0]
    version = item[0]
    text = dedent("\n".join(item[1:]))
    return DocstringSection(DocstringSectionKind.deprecated, (version, text)), index


def _read_returns_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    # returns
    # (NAME : )?TYPE
    #     TEXT?
    items, index = _read_block_items(docstring, offset)

    if not items:
        _warn(docstring, index, f"Empty returns section at line {offset}")
        return None, index

    returns = []
    for item in items:
        match = _RE_RETURNS.match(item[0])
        if not match:
            _warn(docstring, index, f"Could not parse line '{item[0]}'")
            continue

        name, annotation = match.groups()
        text = dedent("\n".join(item[1:]))
        returns.append(DocstringReturn(name=name or "", annotation=annotation, description=text))
    return DocstringSection(DocstringSectionKind.returns, returns), index


def _read_yields_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    # yields
    # (NAME : )?TYPE
    #     TEXT?
    items, index = _read_block_items(docstring, offset)

    if not items:
        _warn(docstring, index, f"Empty yields section at line {offset}")
        return None, index

    yields = []
    for item in items:
        match = _RE_YIELDS.match(item[0])
        if not match:
            _warn(docstring, index, f"Could not parse line '{item[0]}'")
            continue

        name, annotation = match.groups()
        text = dedent("\n".join(item[1:]))
        yields.append(DocstringYield(name=name or "", annotation=annotation, description=text))
    return DocstringSection(DocstringSectionKind.yields, yields), index


def _read_receives_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    # receives
    # (NAME : )?TYPE
    #     TEXT?
    items, index = _read_block_items(docstring, offset)

    if not items:
        _warn(docstring, index, f"Empty receives section at line {offset}")
        return None, index

    receives = []
    for item in items:
        match = _RE_RECEIVES.match(item[0])
        if not match:
            _warn(docstring, index, f"Could not parse line '{item[0]}'")
            continue

        name, annotation = match.groups()
        text = dedent("\n".join(item[1:]))
        receives.append(DocstringReceive(name=name or "", annotation=annotation, description=text))
    return DocstringSection(DocstringSectionKind.receives, receives), index


def _read_raises_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    # raises
    # EXCEPTION
    #     TEXT?
    items, index = _read_block_items(docstring, offset)

    if not items:
        _warn(docstring, index, f"Empty raises section at line {offset}")
        return None, index

    raises = []
    for item in items:
        annotation = item[0]
        text = dedent("\n".join(item[1:]))
        raises.append(DocstringRaise(annotation=annotation, description=text))
    return DocstringSection(DocstringSectionKind.raises, raises), index


def _read_warns_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    # warns
    # WARNING
    #     TEXT?
    items, index = _read_block_items(docstring, offset)

    if not items:
        _warn(docstring, index, f"Empty warns section at line {offset}")
        return None, index

    warns = []
    for item in items:
        annotation = item[0]
        text = dedent("\n".join(item[1:]))
        warns.append(DocstringWarn(annotation=annotation, description=text))
    return DocstringSection(DocstringSectionKind.warns, warns), index


def _read_attributes_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
    # attributes (for classes)
    # NAME( : TYPE)?
    #    TEXT?
    items, index = _read_block_items(docstring, offset)

    if not items:
        _warn(docstring, index, f"Empty attributes section at line {offset}")
        return None, index

    annotation: str | None
    attributes = []
    for item in items:
        name_type = item[0]
        if " : " in name_type:
            name, annotation = name_type.split(" : ", 1)
        else:
            name = name_type
            annotation = None
        text = dedent("\n".join(item[1:]))
        attributes.append(DocstringAttribute(name=name, annotation=annotation, description=text))
    return DocstringSection(DocstringSectionKind.attributes, attributes), index


def _read_examples_section(docstring: Docstring, offset: int) -> tuple[DocstringSection | None, int]:
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


_section_reader = {
    DocstringSectionKind.parameters: _read_parameters_section,
    DocstringSectionKind.other_parameters: _read_other_parameters_section,
    DocstringSectionKind.deprecated: _read_deprecated_section,
    DocstringSectionKind.raises: _read_raises_section,
    DocstringSectionKind.warns: _read_warns_section,
    DocstringSectionKind.examples: _read_examples_section,
    DocstringSectionKind.attributes: _read_attributes_section,
    DocstringSectionKind.returns: _read_returns_section,
    DocstringSectionKind.yields: _read_yields_section,
    DocstringSectionKind.receives: _read_receives_section,
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

        elif line_lower in _section_kind and _is_dash_line(lines[index + 1]):
            if current_section:
                if any(current_section):
                    sections.append(
                        DocstringSection(DocstringSectionKind.text, "\n".join(current_section).rstrip("\n"))
                    )
                current_section = []
            reader = _section_reader[_section_kind[line_lower]]
            section, index = reader(docstring, index + 2)
            if section:
                sections.append(section)

        elif line_lower.lstrip(" ").startswith("```"):
            in_code_block = True
            current_section.append(lines[index])

        else:
            current_section.append(lines[index])

        index += 1

    if current_section:
        sections.append(DocstringSection(DocstringSectionKind.text, "\n".join(current_section).rstrip("\n")))

    return sections
