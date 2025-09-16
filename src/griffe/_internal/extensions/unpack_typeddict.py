from __future__ import annotations

from typing import TYPE_CHECKING, Any

from griffe._internal.docstrings.models import DocstringParameter, DocstringSectionParameters
from griffe._internal.enumerations import DocstringSectionKind, ParameterKind
from griffe._internal.expressions import Expr, ExprSubscript
from griffe._internal.extensions.base import Extension
from griffe._internal.models import Class, Docstring, Function, Parameter, Parameters

if TYPE_CHECKING:
    from collections.abc import Iterable


def _update_docstring(func: Function, parameters: Iterable[Parameter], kwparam: Parameter | None = None) -> None:
    if not func.docstring:
        func.docstring = Docstring("", parent=func)
    sections = func.docstring.parsed
    section_gen = (section for section in sections if section.kind is DocstringSectionKind.parameters)
    if kwparam and (params_section := next(section_gen, None)):
        # Remove the `**kwargs` entry.
        param_gen = (i for i, arg in enumerate(params_section.value) if arg.name.lstrip("*") == kwparam.name)
        if (kwarg_pos := next(param_gen, None)) is not None:
            params_section.value.pop(kwarg_pos)
    else:
        # Create a parameters section if none exists.
        params_section = DocstringSectionParameters([])
        func.docstring.parsed.append(params_section)
    # Add entries for all parameters.
    for param in parameters:
        if param.name != "self":
            params_section.value.append(
                DocstringParameter(
                    name=param.name,
                    description=param.docstring.value if param.docstring else "",
                    annotation=param.annotation,
                    value=param.default,
                ),
            )


def _params_from_attrs(attrs: Iterable[Any]) -> Parameters:
    return Parameters(
        Parameter(name="self", kind=ParameterKind.positional_or_keyword),
        *(
            Parameter(
                name=attr.name,
                annotation=attr.annotation,
                kind=ParameterKind.keyword_only,
                default=attr.value,
                docstring=attr.docstring,
            )
            for attr in attrs
        ),
    )


class UnpackTypedDictExtension(Extension):
    """An extension to handle `Unpack[TypeDict]`."""

    def on_class(self, *, cls: Class, **kwargs: Any) -> None:  # noqa: ARG002
        """Add an `__init__` method to `TypedDict` classes if missing."""
        for base in cls.bases:
            if isinstance(base, Expr) and base.canonical_path in {"typing.TypedDict", "typing_extensions.TypedDict"}:
                cls.labels.add("typed-dict")
                break
        else:
            return

        attributes = cls.attributes.values()

        if "__init__" not in cls.members:
            # Build the `__init__` method and add it to the class.
            parameters = _params_from_attrs(attributes)
            init = Function(name="__init__", parameters=parameters, returns="None")
            cls.set_member("__init__", init)
            # Update the `__init__` docstring.
            _update_docstring(init, parameters)

        # Remove attributes from the class, as they are now in the `__init__` method.
        for attr in attributes:
            cls.del_member(attr.name)

    def on_function(self, *, func: Function, **kwargs: Any) -> None:  # noqa: ARG002
        """Expand `**kwargs: Unpack[TypedDict]` in function signatures."""
        # Find any `**kwargs: Unpack[TypedDict]` parameter.
        for parameter in func.parameters:
            if parameter.kind is ParameterKind.var_keyword:
                annotation = parameter.annotation
                if isinstance(annotation, ExprSubscript) and annotation.canonical_path in {
                    "typing.Annotated",
                    "typing_extensions.Annotated",
                }:
                    annotation = annotation.slice.elements[0]  # type: ignore[union-attr]
                if isinstance(annotation, ExprSubscript) and annotation.canonical_path in {
                    "typing.Unpack",
                    "typing_extensions.Unpack",
                }:
                    slice_path = annotation.slice.canonical_path  # type: ignore[union-attr]
                    typed_dict = func.modules_collection[slice_path]
                    break
        else:
            return

        if "__init__" in typed_dict.members:
            # The `__init__` was already generated: use its parameters.
            parameters = typed_dict["__init__"].parameters
        else:
            # Fallback to building parameters from attributes.
            parameters = _params_from_attrs(typed_dict.attributes.values())

        # Update any parameter section in the docstring.
        # We do this before updating the signature so that
        # parsing the docstring doesn't emit warnings.
        _update_docstring(func, parameters, parameter)

        # Update the function parameters.
        del func.parameters[parameter.name]
        for param in parameters:
            if param.name != "self":
                func.parameters[param.name] = Parameter(
                    name=param.name,
                    annotation=param.annotation,
                    kind=ParameterKind.keyword_only,
                    default=param.default,
                    docstring=param.docstring,
                )
