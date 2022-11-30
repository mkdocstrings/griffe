"""This module defines functions to parse Google-style docstrings into structured data."""

from __future__ import annotations

import re
from contextlib import suppress
from typing import TYPE_CHECKING, List, Tuple

from griffe.docstrings.dataclasses import (
    DocstringAttribute,
    DocstringParameter,
    DocstringRaise,
    DocstringReceive,
    DocstringReturn,
    DocstringSection,
    DocstringSectionAdmonition,
    DocstringSectionAttributes,
    DocstringSectionDeprecated,
    DocstringSectionExamples,
    DocstringSectionKind,
    DocstringSectionOtherParameters,
    DocstringSectionParameters,
    DocstringSectionRaises,
    DocstringSectionReceives,
    DocstringSectionReturns,
    DocstringSectionText,
    DocstringSectionWarns,
    DocstringSectionYields,
    DocstringWarn,
    DocstringYield,
)
from griffe.docstrings.utils import parse_annotation, warning
from griffe.expressions import Expression, Name

if TYPE_CHECKING:
    from typing import Any, Literal, Pattern  # type: ignore[attr-defined]

    from griffe.dataclasses import Docstring

_warn = warning(__name__)

_section_kind = {
    "args": DocstringSectionKind.parameters,
    "arguments": DocstringSectionKind.parameters,
    "params": DocstringSectionKind.parameters,
    "parameters": DocstringSectionKind.parameters,
    "keyword args": DocstringSectionKind.other_parameters,
    "keyword arguments": DocstringSectionKind.other_parameters,
    "other args": DocstringSectionKind.other_parameters,
    "other parameters": DocstringSectionKind.other_parameters,
    "raises": DocstringSectionKind.raises,
    "exceptions": DocstringSectionKind.raises,
    "returns": DocstringSectionKind.returns,
    "yields": DocstringSectionKind.yields,
    "receives": DocstringSectionKind.receives,
    "examples": DocstringSectionKind.examples,
    "attributes": DocstringSectionKind.attributes,
}

BlockItem = Tuple[int, List[str]]
BlockItems = List[BlockItem]
ItemsBlock = Tuple[BlockItems, int]

_RE_ADMONITION: Pattern = re.compile(r"^(?P<type>[\w][\s\w-]*):(\s+(?P<title>[^\s].*))?$", re.I)
_RE_NAME_ANNOTATION_DESCRIPTION: Pattern = re.compile(r"^(?:(?P<name>\w+)?\s*(?:\((?P<type>.+)\))?:\s*)?(?P<desc>.*)$")
_RE_DOCTEST_BLANKLINE: Pattern = re.compile(r"^\s*<BLANKLINE>\s*$")
_RE_DOCTEST_FLAGS: Pattern = re.compile(r"(\s*#\s*doctest:.+)$")


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
        return "", offset - 1

    new_offset = offset
    block: list[str] = []

    # skip first empty lines
    while _is_empty_line(lines[new_offset]):
        new_offset += 1

    # get initial indent
    indent = len(lines[new_offset]) - len(lines[new_offset].lstrip())

    if indent == 0:
        # first non-empty line was not indented, abort
        return "", offset - 1

    # start processing first item
    block.append(lines[new_offset].lstrip())
    new_offset += 1

    # loop on next lines
    while new_offset < len(lines) and (lines[new_offset].startswith(indent * " ") or _is_empty_line(lines[new_offset])):
        block.append(lines[new_offset][indent:])
        new_offset += 1

    return "\n".join(block).rstrip("\n"), new_offset - 1


def _read_parameters(  # noqa: WPS231
    docstring: Docstring,
    offset: int,
    warn_unknown_params: bool = True,
) -> tuple[list[DocstringParameter], int]:  # noqa: WPS231
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
            annotation = parse_annotation(annotation, docstring)
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

        if warn_unknown_params:
            with suppress(AttributeError):  # for parameters sections in objects without parameters
                params = docstring.parent.parameters  # type: ignore[union-attr]
                if name not in params:
                    message = f"Parameter '{name}' does not appear in the function signature"
                    for starred_name in (f"*{name}", f"**{name}"):
                        if starred_name in params:
                            message += f". Did you mean '{starred_name}'?"
                            break
                    _warn(docstring, line_number, message)

        parameters.append(DocstringParameter(name=name, value=default, annotation=annotation, description=description))

    return parameters, new_offset


def _read_parameters_section(
    docstring: Docstring,
    offset: int,
    **options: Any,
) -> tuple[DocstringSectionParameters | None, int]:
    parameters, new_offset = _read_parameters(docstring, offset)

    if parameters:
        return DocstringSectionParameters(parameters), new_offset

    _warn(docstring, new_offset, f"Empty parameters section at line {offset}")
    return None, new_offset


def _read_other_parameters_section(
    docstring: Docstring,
    offset: int,
    **options: Any,
) -> tuple[DocstringSectionOtherParameters | None, int]:
    parameters, new_offset = _read_parameters(docstring, offset, warn_unknown_params=False)

    if parameters:
        return DocstringSectionOtherParameters(parameters), new_offset

    _warn(docstring, new_offset, f"Empty other parameters section at line {offset}")
    return None, new_offset


def _read_attributes_section(
    docstring: Docstring,
    offset: int,
    **options: Any,
) -> tuple[DocstringSectionAttributes | None, int]:
    attributes = []
    block, new_offset = _read_block_items(docstring, offset)

    annotation: str | Name | Expression | None = None
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
            annotation = parse_annotation(annotation, docstring)
        else:
            name = name_with_type
            with suppress(AttributeError, KeyError):
                annotation = docstring.parent.members[name].annotation  # type: ignore[union-attr]

        attributes.append(DocstringAttribute(name=name, annotation=annotation, description=description))

    if attributes:
        return DocstringSectionAttributes(attributes), new_offset

    _warn(docstring, new_offset, f"Empty attributes section at line {offset}")
    return None, new_offset


def _read_raises_section(
    docstring: Docstring,
    offset: int,
    **options: Any,
) -> tuple[DocstringSectionRaises | None, int]:
    exceptions = []
    block, new_offset = _read_block_items(docstring, offset)

    annotation: str | Name | Expression
    for line_number, exception_lines in block:
        try:
            annotation, description = exception_lines[0].split(": ", 1)
        except ValueError:
            _warn(docstring, line_number, f"Failed to get 'exception: description' pair from '{exception_lines[0]}'")
        else:
            description = "\n".join([description.lstrip(), *exception_lines[1:]]).rstrip("\n")
            # try to compile the annotation to transform it into an expression
            annotation = parse_annotation(annotation, docstring)
            exceptions.append(DocstringRaise(annotation=annotation, description=description))

    if exceptions:
        return DocstringSectionRaises(exceptions), new_offset

    _warn(docstring, new_offset, f"Empty exceptions section at line {offset}")
    return None, new_offset


def _read_warns_section(
    docstring: Docstring,
    offset: int,
    **options: Any,
) -> tuple[DocstringSectionWarns | None, int]:
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
        return DocstringSectionWarns(warns), new_offset

    _warn(docstring, new_offset, f"Empty warns section at line {offset}")
    return None, new_offset


def _read_returns_section(  # noqa: WPS231
    docstring: Docstring,
    offset: int,
    **options: Any,
) -> tuple[DocstringSectionReturns | None, int]:
    returns = []
    block, new_offset = _read_block_items(docstring, offset)

    for index, (line_number, return_lines) in enumerate(block):
        match = _RE_NAME_ANNOTATION_DESCRIPTION.match(return_lines[0])
        if not match:
            _warn(docstring, line_number, f"Failed to get name, annotation or description from '{return_lines[0]}'")
            continue

        name, annotation, description = match.groups()
        description = "\n".join([description.lstrip(), *return_lines[1:]]).rstrip("\n")

        if annotation:
            # try to compile the annotation to transform it into an expression
            annotation = parse_annotation(annotation, docstring)
        else:
            # try to retrieve the annotation from the docstring parent
            with suppress(AttributeError, KeyError, ValueError):
                if docstring.parent.is_function:  # type: ignore[union-attr]
                    annotation = docstring.parent.returns  # type: ignore[union-attr]
                elif docstring.parent.is_attribute:  # type: ignore[union-attr]
                    annotation = docstring.parent.annotation  # type: ignore[union-attr]
                else:
                    raise ValueError
                if len(block) > 1:
                    if annotation.is_tuple:
                        annotation = annotation.tuple_item(index)
                    else:
                        if annotation.is_iterator:
                            return_item = annotation.iterator_item()
                        elif annotation.is_generator:
                            _, _, return_item = annotation.generator_items()
                        else:
                            raise ValueError
                        if isinstance(return_item, Name):
                            annotation = return_item
                        elif return_item.is_tuple:
                            annotation = return_item.tuple_item(index)
                        else:
                            annotation = return_item

            if annotation is None:
                returned_value = repr(name) if name else index + 1
                _warn(docstring, line_number, f"No type or annotation for returned value {returned_value}")

        returns.append(DocstringReturn(name=name or "", annotation=annotation, description=description))

    if returns:
        return DocstringSectionReturns(returns), new_offset

    _warn(docstring, new_offset, f"Empty returns section at line {offset}")
    return None, new_offset


def _read_yields_section(  # noqa: WPS231
    docstring: Docstring,
    offset: int,
    **options: Any,
) -> tuple[DocstringSectionYields | None, int]:
    yields = []
    block, new_offset = _read_block_items(docstring, offset)

    for index, (line_number, yield_lines) in enumerate(block):  # noqa: B007 (will be used later)
        match = _RE_NAME_ANNOTATION_DESCRIPTION.match(yield_lines[0])
        if not match:
            _warn(docstring, line_number, f"Failed to get name, annotation or description from '{yield_lines[0]}'")
            continue

        name, annotation, description = match.groups()
        description = "\n".join([description.lstrip(), *yield_lines[1:]]).rstrip("\n")

        if annotation:
            # try to compile the annotation to transform it into an expression
            annotation = parse_annotation(annotation, docstring)
        else:
            # try to retrieve the annotation from the docstring parent
            with suppress(AttributeError, KeyError, ValueError):
                annotation = docstring.parent.returns  # type: ignore[union-attr]
                if len(block) > 1:
                    if annotation.is_iterator:
                        yield_item = annotation.iterator_item()
                    elif annotation.is_generator:
                        yield_item, _, _ = annotation.generator_items()
                    else:
                        raise ValueError
                    if isinstance(yield_item, Name):
                        annotation = yield_item
                    elif yield_item.is_tuple:
                        annotation = yield_item.tuple_item(index)
                    else:
                        annotation = yield_item

            if annotation is None:
                yielded_value = repr(name) if name else index + 1
                _warn(docstring, line_number, f"No type or annotation for yielded value {yielded_value}")

        yields.append(DocstringYield(name=name or "", annotation=annotation, description=description))

    if yields:
        return DocstringSectionYields(yields), new_offset

    _warn(docstring, new_offset, f"Empty yields section at line {offset}")
    return None, new_offset


def _read_receives_section(  # noqa: WPS231
    docstring: Docstring,
    offset: int,
    **options: Any,
) -> tuple[DocstringSectionReceives | None, int]:
    receives = []
    block, new_offset = _read_block_items(docstring, offset)

    for index, (line_number, receive_lines) in enumerate(block):  # noqa: B007 (will be used later)
        match = _RE_NAME_ANNOTATION_DESCRIPTION.match(receive_lines[0])
        if not match:
            _warn(docstring, line_number, f"Failed to get name, annotation or description from '{receive_lines[0]}'")
            continue

        name, annotation, description = match.groups()
        description = "\n".join([description.lstrip(), *receive_lines[1:]]).rstrip("\n")

        if annotation:
            # try to compile the annotation to transform it into an expression
            annotation = parse_annotation(annotation, docstring)
        else:
            # try to retrieve the annotation from the docstring parent
            with suppress(AttributeError, KeyError):
                annotation = docstring.parent.returns  # type: ignore[union-attr]
                if len(block) > 1 and annotation.is_generator:
                    _, receives_item, _ = annotation.generator_items()
                    if isinstance(receives_item, Name):
                        annotation = receives_item
                    elif receives_item.is_tuple:
                        annotation = receives_item.tuple_item(index)
                    else:
                        annotation = receives_item

        if annotation is None:
            received_value = repr(name) if name else index + 1
            _warn(docstring, line_number, f"No type or annotation for received value {received_value}")

        receives.append(DocstringReceive(name=name or "", annotation=annotation, description=description))

    if receives:
        return DocstringSectionReceives(receives), new_offset

    _warn(docstring, new_offset, f"Empty receives section at line {offset}")
    return None, new_offset


def _read_examples_section(  # noqa: WPS231
    docstring: Docstring,
    offset: int,
    trim_doctest_flags: bool = True,
    **options: Any,
) -> tuple[DocstringSectionExamples | None, int]:
    text, new_offset = _read_block(docstring, offset)

    sub_sections: list[tuple[Literal[DocstringSectionKind.text] | Literal[DocstringSectionKind.examples], str]] = []
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
            if trim_doctest_flags:
                line = _RE_DOCTEST_FLAGS.sub("", line)
                line = _RE_DOCTEST_BLANKLINE.sub("", line)
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

            if trim_doctest_flags:
                line = _RE_DOCTEST_FLAGS.sub("", line)
            current_example.append(line)

        else:
            current_text.append(line)

    if current_text:
        sub_sections.append((DocstringSectionKind.text, "\n".join(current_text).rstrip("\n")))
    elif current_example:
        sub_sections.append((DocstringSectionKind.examples, "\n".join(current_example)))

    if sub_sections:
        return DocstringSectionExamples(sub_sections), new_offset

    _warn(docstring, new_offset, f"Empty examples section at line {offset}")
    return None, new_offset


def _read_deprecated_section(
    docstring: Docstring,
    offset: int,
    **options: Any,
) -> tuple[DocstringSectionDeprecated | None, int]:
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
        DocstringSectionDeprecated(version=version, text=description),
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
    ignore_init_summary: bool = False,
    trim_doctest_flags: bool = True,
    **options: Any,
) -> list[DocstringSection]:
    """Parse a docstring.

    This function iterates on lines of a docstring to build sections.
    It then returns this list of sections.

    Parameters:
        docstring: The docstring to parse.
        ignore_init_summary: Whether to ignore the summary in `__init__` methods' docstrings.
        trim_doctest_flags: Whether to remove doctest flags from Python example blocks.
        **options: Additional parsing options.

    Returns:
        A list of docstring sections.
    """
    sections: list[DocstringSection] = []
    current_section = []

    in_code_block = False
    lines = docstring.lines

    options = {
        "ignore_init_summary": ignore_init_summary,
        "trim_doctest_flags": trim_doctest_flags,
        **options,
    }

    ignore_summary = (
        options["ignore_init_summary"]  # noqa: WPS222
        and docstring.parent is not None
        and docstring.parent.name == "__init__"
        and docstring.parent.is_function
        and docstring.parent.parent is not None
        and docstring.parent.parent.is_class
    )

    if ignore_summary:
        offset = 2
    else:
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
                title = groups["title"]
                admonition_type = groups["type"]
                if admonition_type.lower() in _section_kind:
                    if current_section:
                        if any(current_section):
                            sections.append(DocstringSectionText("\n".join(current_section).rstrip("\n")))
                        current_section = []
                    reader = _section_reader[_section_kind[admonition_type.lower()]]
                    section, offset = reader(docstring, offset + 1, **options)  # type: ignore[operator]
                    if section:
                        section.title = title
                        sections.append(section)

                else:
                    contents, offset = _read_block(docstring, offset + 1)
                    if contents:
                        if current_section:
                            if any(current_section):
                                sections.append(DocstringSectionText("\n".join(current_section).rstrip("\n")))
                            current_section = []
                        if title is None:
                            title = admonition_type
                        admonition_type = admonition_type.lower().replace(" ", "-")
                        sections.append(DocstringSectionAdmonition(kind=admonition_type, text=contents, title=title))
                    else:
                        with suppress(IndexError):
                            current_section.append(lines[offset])
            else:
                current_section.append(lines[offset])

        offset += 1

    if current_section:
        sections.append(DocstringSectionText("\n".join(current_section).rstrip("\n")))

    return sections
