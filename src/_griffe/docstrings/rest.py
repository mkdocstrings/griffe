# This module defines functions to parse ReST-style docstrings into structured data.


from __future__ import annotations

from typing import TYPE_CHECKING, OrderedDict, TypeVar

import cdd.docstring.parse
import cdd.shared.types

from _griffe.docstrings.models import (
    DocstringSection,
    DocstringSectionText,
    DocstringSectionReturns,
    DocstringNamedElement,
    DocstringReturn,
    DocstringSectionParameters,
    DocstringParameter,
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


T = TypeVar('T', DocstringParameter, DocstringReturn)

def ir_param_to_griffe_param(
    ir_param: OrderedDict[str, cdd.shared.types.ParamVal], cls: type[T]
) -> list[type[T]]:
    """
    Convert an `OrderedDict` of cdd-python's `ParamVal` to a `list` of griffe's `DocstringNamedElement`
    """
    return [
        cls(
            name=name,
            description=param["doc"] if param.get("doc") else "",
            annotation=param["typ"] if param.get("typ") else None,
            value=param["default"] if param.get("default") else None,
        )
        for name, param in ir_param.items()
    ]


def ir_to_griffe(ir: cdd.shared.types.IntermediateRepr) -> None | list[type[DocstringSection]]:
    """
    Convert cdd-python's IR to a list of griffe's `DocstringSection`s
    """
    sections: list[type[DocstringSection]] = [
        DocstringSectionText(ir["doc"]),
        DocstringSectionParameters(
            ir_param_to_griffe_param(ir["params"], DocstringParameter)
        ),
    ]
    if ir["returns"]:
        sections.append(
            DocstringSectionReturns(
                ir_param_to_griffe_param(ir["returns"], DocstringReturn)
            )
        )
    return sections or None


def parse_rest(
    docstring: Docstring,
    *,
    ignore_init_summary: bool = False,
    trim_doctest_flags: bool = True,
    warn_unknown_params: bool = True,
    warnings: bool = True,
    **options: Any,
) -> None | list[DocstringSection]:
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
    ir: cdd.shared.types.IntermediateRepr = cdd.docstring.parse.docstring(
        docstring.value
    )
    return ir_to_griffe(ir)


__all__ = ["parse_rest"]
