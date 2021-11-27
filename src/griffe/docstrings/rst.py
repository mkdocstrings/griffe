"""This module defines functions to parse RST-style docstrings into structured data.

Credits to Patrick Lannigan ([@plannigan](https://github.com/plannigan))
who originally added the parser in the [pytkdocs project](https://github.com/mkdocstrings/pytkdocs).
See https://github.com/mkdocstrings/pytkdocs/pull/71.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, FrozenSet

from griffe.docstrings.dataclasses import (
    DocstringAttribute,
    DocstringParameter,
    DocstringRaise,
    DocstringReturn,
    DocstringSection,
    DocstringSectionKind,
)
from griffe.docstrings.utils import warning
from griffe.expressions import Expression, Name

if TYPE_CHECKING:
    from griffe.dataclasses import Docstring

_warn = warning(__name__)

# TODO: Examples: from the documentation, I'm not sure there is a standard format for examples
PARAM_NAMES = frozenset(("param", "parameter", "arg", "argument", "key", "keyword"))
PARAM_TYPE_NAMES = frozenset(("type",))
ATTRIBUTE_NAMES = frozenset(("var", "ivar", "cvar"))
ATTRIBUTE_TYPE_NAMES = frozenset(("vartype",))
RETURN_NAMES = frozenset(("returns", "return"))
RETURN_TYPE_NAMES = frozenset(("rtype",))
EXCEPTION_NAMES = frozenset(("raises", "raise", "except", "exception"))


@dataclass(frozen=True)
class FieldType:
    """Maps directive names to parser functions."""

    names: FrozenSet[str]
    reader: Callable[[Docstring, int, ParsedValues], int]

    def matches(self, line: str) -> bool:
        """Check if a line matches the field type.

        Parameters:
            line: Line to check against

        Returns:
            True if the line matches the field type, False otherwise.
        """
        return any(line.startswith(f":{name}") for name in self.names)


@dataclass
class ParsedDirective:
    """Directive information that has been parsed from a docstring."""

    line: str
    next_index: int
    directive_parts: list[str]
    value: str
    invalid: bool = False


@dataclass
class ParsedValues:
    """Values parsed from the docstring to be used to produce sections."""

    description: list[str] = field(default_factory=list)
    parameters: dict[str, DocstringParameter] = field(default_factory=dict)
    param_types: dict[str, str] = field(default_factory=dict)
    attributes: dict[str, DocstringAttribute] = field(default_factory=dict)
    attribute_types: dict[str, str] = field(default_factory=dict)
    exceptions: list[DocstringRaise] = field(default_factory=list)
    return_value: DocstringReturn | None = None
    return_type: str | None = None


def parse(docstring: Docstring, **options: Any) -> list[DocstringSection]:
    """Parse an RST-styled docstring.

    Parameters:
        docstring: The docstring to parse.
        **options: Additional parsing options.

    Returns:
        A list of docstring sections.
    """
    parsed_values = ParsedValues()

    lines = docstring.lines
    curr_line_index = 0

    while curr_line_index < len(lines):
        line = lines[curr_line_index]
        for field_type in field_types:
            if field_type.matches(line):
                # https://github.com/python/mypy/issues/5485
                curr_line_index = field_type.reader(docstring, curr_line_index, parsed_values)  # type: ignore[misc,operator]
                break
        else:
            parsed_values.description.append(line)

        curr_line_index += 1

    return _parsed_values_to_sections(parsed_values)


def _read_parameter(docstring: Docstring, offset: int, parsed_values: ParsedValues) -> int:
    """
    Parse a parameter value.

    Parameters:
        docstring: The docstring.
        offset: The line number to start at.

    Returns:
        Index at which to continue parsing.
    """
    parsed_directive = _parse_directive(docstring, offset)
    if parsed_directive.invalid:
        return parsed_directive.next_index

    directive_type = None
    if len(parsed_directive.directive_parts) == 2:
        # no type info
        name = parsed_directive.directive_parts[1]
    elif len(parsed_directive.directive_parts) == 3:
        directive_type = parsed_directive.directive_parts[1]
        name = parsed_directive.directive_parts[2]
    else:
        _warn(docstring, 0, f"Failed to parse field directive from '{parsed_directive.line}'")
        return parsed_directive.next_index

    if name in parsed_values.parameters:
        _warn(docstring, 0, f"Duplicate parameter entry for '{name}'")
        return parsed_directive.next_index

    annotation = _determine_param_annotation(docstring, name, directive_type, parsed_values)
    default = _determine_param_default(docstring, name)

    parsed_values.parameters[name] = DocstringParameter(
        name=name,
        annotation=annotation,
        description=parsed_directive.value,
        value=default,
    )

    return parsed_directive.next_index


def _determine_param_default(docstring: Docstring, name: str) -> str | None:
    try:
        return docstring.parent.parameters[name.lstrip()].default  # type: ignore[union-attr]
    except (AttributeError, KeyError):
        return None


def _determine_param_annotation(
    docstring: Docstring, name: str, directive_type: str | None, parsed_values: ParsedValues
) -> Any:
    # Annotation precedence:
    # - in-line directive type
    # - "type" directive type
    # - signature annotation
    # - none
    annotation: str | Name | Expression | None = None

    parsed_param_type = parsed_values.param_types.get(name)
    if parsed_param_type is not None:
        annotation = parsed_param_type

    if directive_type is not None:
        annotation = directive_type

    if directive_type is not None and parsed_param_type is not None:
        _warn(docstring, 0, f"Duplicate parameter information for '{name}'")

    if annotation is None:
        try:
            annotation = docstring.parent.parameters[name.lstrip()].annotation  # type: ignore[union-attr]
        except (AttributeError, KeyError):
            _warn(docstring, 0, f"No matching parameter for '{name}'")

    return annotation


def _read_parameter_type(docstring: Docstring, offset: int, parsed_values: ParsedValues) -> int:
    """
    Parse a parameter type.

    Parameters:
        docstring: The docstring.
        offset: The line number to start at.

    Returns:
        Index at which to continue parsing.
    """
    parsed_directive = _parse_directive(docstring, offset)
    if parsed_directive.invalid:
        return parsed_directive.next_index
    param_type = _consolidate_descriptive_type(parsed_directive.value.strip())

    if len(parsed_directive.directive_parts) == 2:
        param_name = parsed_directive.directive_parts[1]
    else:
        _warn(docstring, 0, f"Failed to get parameter name from '{parsed_directive.line}'")
        return parsed_directive.next_index

    parsed_values.param_types[param_name] = param_type
    param = parsed_values.parameters.get(param_name)
    if param is not None:
        if param.annotation is None:
            param.annotation = param_type
        else:
            _warn(docstring, 0, f"Duplicate parameter information for '{param_name}'")
    return parsed_directive.next_index


def _read_attribute(docstring: Docstring, offset: int, parsed_values: ParsedValues) -> int:
    """
    Parse an attribute value.

    Parameters:
        docstring: The docstring.
        offset: The line number to start at.

    Returns:
        Index at which to continue parsing.
    """
    parsed_directive = _parse_directive(docstring, offset)
    if parsed_directive.invalid:
        return parsed_directive.next_index

    if len(parsed_directive.directive_parts) == 2:
        name = parsed_directive.directive_parts[1]
    else:
        _warn(docstring, 0, f"Failed to parse field directive from '{parsed_directive.line}'")
        return parsed_directive.next_index

    annotation = None

    # Annotation precedence:
    # - "vartype" directive type
    # - none

    parsed_attribute_type = parsed_values.attribute_types.get(name)
    if parsed_attribute_type is not None:
        annotation = parsed_attribute_type

    if name in parsed_values.attributes:
        _warn(docstring, 0, f"Duplicate attribute entry for '{name}'")
    else:
        parsed_values.attributes[name] = DocstringAttribute(
            name=name,
            annotation=annotation,
            description=parsed_directive.value,
        )

    return parsed_directive.next_index


def _read_attribute_type(docstring: Docstring, offset: int, parsed_values: ParsedValues) -> int:
    """
    Parse a parameter type.

    Parameters:
        docstring: The docstring.
        offset: The line number to start at.

    Returns:
        Index at which to continue parsing.
    """
    parsed_directive = _parse_directive(docstring, offset)
    if parsed_directive.invalid:
        return parsed_directive.next_index
    attribute_type = _consolidate_descriptive_type(parsed_directive.value.strip())

    if len(parsed_directive.directive_parts) == 2:
        attribute_name = parsed_directive.directive_parts[1]
    else:
        _warn(docstring, 0, f"Failed to get attribute name from '{parsed_directive.line}'")
        return parsed_directive.next_index

    parsed_values.attribute_types[attribute_name] = attribute_type
    attribute = parsed_values.attributes.get(attribute_name)
    if attribute is not None:
        if attribute.annotation is None:
            attribute.annotation = attribute_type
        else:
            _warn(docstring, 0, f"Duplicate attribute information for '{attribute_name}'")
    return parsed_directive.next_index


def _read_exception(docstring: Docstring, offset: int, parsed_values: ParsedValues) -> int:
    """
    Parse an exception value.

    Parameters:
        docstring: The docstring.
        offset: The line number to start at.

    Returns:
        A tuple containing a `DocstringSection` (or `None`) and the index at which to continue parsing.
    """
    parsed_directive = _parse_directive(docstring, offset)
    if parsed_directive.invalid:
        return parsed_directive.next_index

    if len(parsed_directive.directive_parts) == 2:
        ex_type = parsed_directive.directive_parts[1]
        parsed_values.exceptions.append(DocstringRaise(annotation=ex_type, description=parsed_directive.value))
    else:
        _warn(docstring, 0, f"Failed to parse exception directive from '{parsed_directive.line}'")

    return parsed_directive.next_index


def _read_return(docstring: Docstring, offset: int, parsed_values: ParsedValues) -> int:
    """
    Parse an return value.

    Parameters:
        docstring: The docstring.
        offset: The line number to start at.

    Returns:
        Index at which to continue parsing.
    """
    parsed_directive = _parse_directive(docstring, offset)
    if parsed_directive.invalid:
        return parsed_directive.next_index

    # Annotation precedence:
    # - "rtype" directive type
    # - signature annotation
    # - None
    annotation: str | Name | Expression | None
    if parsed_values.return_type is not None:
        annotation = parsed_values.return_type
    else:
        try:
            annotation = docstring.parent.returns  # type: ignore[union-attr]
        except AttributeError:
            _warn(docstring, 0, f"No return type or annotation at '{parsed_directive.line}'")
            annotation = None

    # TODO: maybe support names
    parsed_values.return_value = DocstringReturn(name="", annotation=annotation, description=parsed_directive.value)

    return parsed_directive.next_index


def _read_return_type(docstring: Docstring, offset: int, parsed_values: ParsedValues) -> int:
    """
    Parse an return type value.

    Parameters:
        docstring: The docstring.
        offset: The line number to start at.

    Returns:
        Index at which to continue parsing.
    """
    parsed_directive = _parse_directive(docstring, offset)
    if parsed_directive.invalid:
        return parsed_directive.next_index

    return_type = _consolidate_descriptive_type(parsed_directive.value.strip())
    parsed_values.return_type = return_type
    return_value = parsed_values.return_value
    if return_value is not None:
        return_value.annotation = return_type

    return parsed_directive.next_index


def _parsed_values_to_sections(parsed_values: ParsedValues) -> list[DocstringSection]:
    text = "\n".join(_strip_blank_lines(parsed_values.description))
    result = [DocstringSection(DocstringSectionKind.text, text)]
    if parsed_values.parameters:
        param_values = list(parsed_values.parameters.values())
        result.append(DocstringSection(DocstringSectionKind.parameters, param_values))
    if parsed_values.attributes:
        attribute_values = list(parsed_values.attributes.values())
        result.append(DocstringSection(DocstringSectionKind.attributes, attribute_values))
    if parsed_values.return_value is not None:
        result.append(DocstringSection(DocstringSectionKind.returns, parsed_values.return_value))
    if parsed_values.exceptions:
        result.append(DocstringSection(DocstringSectionKind.raises, parsed_values.exceptions))
    return result


def _parse_directive(docstring: Docstring, offset: int) -> ParsedDirective:
    line, next_index = _consolidate_continuation_lines(docstring.lines, offset)
    try:
        _, directive, value = line.split(":", 2)
    except ValueError:
        _warn(docstring, 0, f"Failed to get ':directive: value' pair from '{line}'")
        return ParsedDirective(line, next_index, [], "", invalid=True)

    value = value.strip()
    return ParsedDirective(line, next_index, directive.split(" "), value)


def _consolidate_continuation_lines(lines: list[str], offset: int) -> tuple[str, int]:
    """
    Convert a docstring field into a single line if a line continuation exists.

    Parameters:
        lines: The docstring lines.
        offset: The line number to start at.

    Returns:
        A tuple containing the continued lines as a single string and the index at which to continue parsing.
    """
    curr_line_index = offset
    block = [lines[curr_line_index].lstrip()]

    # start processing after first item
    curr_line_index += 1
    while curr_line_index < len(lines) and not lines[curr_line_index].startswith(":"):
        block.append(lines[curr_line_index].lstrip())
        curr_line_index += 1

    return " ".join(block).rstrip("\n"), curr_line_index - 1


def _consolidate_descriptive_type(descriptive_type: str) -> str:
    """Convert type descriptions with "or" into respective type signature.

    "x or y" -> "x | y"

    Parameters:
        descriptive_type: Descriptions of an item's type.

    Returns:
        Type signature for descriptive type.
    """
    return descriptive_type.replace(" or ", " | ")


def _strip_blank_lines(lines: list[str]) -> list[str]:
    """Remove lines with no text or only whitespace characters from the start and end of the list.

    Parameters:
        lines: Lines to be stripped.

    Returns:
        A list with the same contents, with any blank lines at the start or end removed.
    """
    if not lines:
        return lines

    # remove blank lines from the start and end
    content_found = False
    initial_content = 0
    final_content = 0
    for index, line in enumerate(lines):
        if line == "" or line.isspace():
            if not content_found:
                initial_content += 1
        else:
            content_found = True
            final_content = index
    return lines[initial_content : final_content + 1]


field_types = [
    FieldType(PARAM_TYPE_NAMES, _read_parameter_type),
    FieldType(PARAM_NAMES, _read_parameter),
    FieldType(ATTRIBUTE_TYPE_NAMES, _read_attribute_type),
    FieldType(ATTRIBUTE_NAMES, _read_attribute),
    FieldType(EXCEPTION_NAMES, _read_exception),
    FieldType(RETURN_NAMES, _read_return),
    FieldType(RETURN_TYPE_NAMES, _read_return_type),
]
