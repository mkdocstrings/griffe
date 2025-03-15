# This module contains utilities for docstrings parsers.

from __future__ import annotations

from ast import PyCF_ONLY_AST
from contextlib import suppress
from typing import TYPE_CHECKING

from _griffe.enumerations import LogLevel
from _griffe.exceptions import BuiltinModuleError
from _griffe.expressions import safe_get_annotation
from _griffe.logger import logger

if TYPE_CHECKING:
    from _griffe.expressions import Expr
    from _griffe.models import Docstring


def docstring_warning(
    docstring: Docstring,
    offset: int,
    message: str,
    log_level: LogLevel = LogLevel.warning,
) -> None:
    """Log a warning when parsing a docstring.

    This function logs a warning message by prefixing it with the filepath and line number.

    Parameters:
        docstring: The docstring object.
        offset: The offset in the docstring lines.
        message: The message to log.

    Returns:
        A function used to log parsing warnings if `name` was passed, else none.
    """

    def warn(docstring: Docstring, offset: int, message: str, log_level: LogLevel = LogLevel.warning) -> None:
        try:
            prefix = docstring.parent.relative_filepath  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            prefix = "<module>"
        except BuiltinModuleError:
            prefix = f"<module: {docstring.parent.module.name}>"  # type: ignore[union-attr]
        log = getattr(logger, log_level.value)
        log(f"{prefix}:{(docstring.lineno or 0) + offset}: {message}")

    warn(docstring, offset, message, log_level)


def parse_docstring_annotation(
    annotation: str,
    docstring: Docstring,
    log_level: LogLevel = LogLevel.error,
) -> str | Expr:
    """Parse a string into a true name or expression that can be resolved later.

    Parameters:
        annotation: The annotation to parse.
        docstring: The docstring in which the annotation appears.
            The docstring's parent is accessed to bind a resolver to the resulting name/expression.
        log_level: Log level to use to log a message.

    Returns:
        The string unchanged, or a new name or expression.
    """
    with suppress(
        AttributeError,  # docstring has no parent that can be used to resolve names
        SyntaxError,  # annotation contains syntax errors
    ):
        code = compile(annotation, mode="eval", filename="", flags=PyCF_ONLY_AST, optimize=2)
        if code.body:  # type: ignore[attr-defined]
            name_or_expr = safe_get_annotation(
                code.body,  # type: ignore[attr-defined]
                parent=docstring.parent,  # type: ignore[arg-type]
                log_level=log_level,
            )
            return name_or_expr or annotation
    return annotation
