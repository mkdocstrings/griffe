# This module defines functions to parse ReST-style docstrings into structured data.


from __future__ import annotations

from typing import TYPE_CHECKING

from _griffe.docstrings.models import (
    DocstringSection
)
from _griffe.enumerations import DocstringSectionKind

if TYPE_CHECKING:
    from typing import Any

    from _griffe.models import Docstring


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
    "functions": DocstringSectionKind.functions,
    "methods": DocstringSectionKind.functions,
    "classes": DocstringSectionKind.classes,
    "modules": DocstringSectionKind.modules,
}


def parse_rest(
    docstring: Docstring,
    *,
    ignore_init_summary: bool = False,
    trim_doctest_flags: bool = True,
    warn_unknown_params: bool = True,
    warnings: bool = True,
    **options: Any,
) -> list[DocstringSection]:
    """Parse a ReST-style docstring.

    This function iterates on lines of a docstring to build sections.
    It then returns this list of sections.

    Parameters:
        docstring: The docstring to parse.
        ignore_init_summary: Whether to ignore the summary in `__init__` methods' docstrings.
        trim_doctest_flags: Whether to remove doctest flags from Python example blocks.
        warn_unknown_params: Warn about documented parameters not appearing in the signature.
        warnings: Whether to log warnings at all.
        **options: Additional parsing options.

    Returns:
        A list of docstring sections.
    """
    raise NotImplementedError()
