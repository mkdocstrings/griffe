# This module contains utilities for docstrings parsers.

from __future__ import annotations

import warnings
from ast import PyCF_ONLY_AST
from contextlib import suppress
from typing import TYPE_CHECKING, Protocol, overload

from _griffe.enumerations import LogLevel
from _griffe.exceptions import BuiltinModuleError
from _griffe.expressions import safe_get_annotation

# YORE: Bump 1: Replace `get_logger` with `logger` within line.
from _griffe.logger import get_logger

if TYPE_CHECKING:
    from _griffe.expressions import Expr
    from _griffe.models import Docstring


# YORE: Bump 1: Remove block.
class DocstringWarningCallable(Protocol):
    """A callable that logs a warning message."""

    def __call__(self, docstring: Docstring, offset: int, message: str, log_level: LogLevel = ...) -> None:
        """Log a warning message.

        Parameters:
            docstring: The docstring in which the warning occurred.
            offset: The offset in the docstring lines.
            message: The message to log.
            log_level: The log level to use.
        """


# YORE: Bump 1: Remove line.
_sentinel = object()


# YORE: Bump 1: Remove block.
@overload
def docstring_warning(name: str) -> DocstringWarningCallable: ...


# YORE: Bump 1: Remove block.
@overload
def docstring_warning(
    docstring: Docstring,
    offset: int,
    message: str,
    log_level: LogLevel = LogLevel.warning,
) -> None: ...


def docstring_warning(  # type: ignore[misc]
    # YORE: Bump 1: Remove line.
    name: str | None = None,
    # YORE: Bump 1: Replace line with `docstring: Docstring,`.
    docstring: Docstring = _sentinel,  # type: ignore[assignment]
    # YORE: Bump 1: Replace line with `offset: int,`.
    offset: int = _sentinel,  # type: ignore[assignment]
    # YORE: Bump 1: Replace line with `message: str,`.
    message: str = _sentinel,  # type: ignore[assignment]
    log_level: LogLevel = LogLevel.warning,
    # YORE: Bump 1: Replace line with `) -> None:`.
) -> DocstringWarningCallable | None:
    """Log a warning when parsing a docstring.

    This function logs a warning message by prefixing it with the filepath and line number.

    Parameters:
        name: Deprecated. If passed, the function returns a callable, and other arguments are ignored.
        docstring: The docstring object.
        offset: The offset in the docstring lines.
        message: The message to log.

    Returns:
        A function used to log parsing warnings if `name` was passed, else none.
    """
    # YORE: Bump 1: Remove block.
    if name is not None:
        warnings.warn("The `name` parameter is deprecated.", DeprecationWarning, stacklevel=1)
        logger = get_logger(name)
    else:
        if docstring is _sentinel or offset is _sentinel or message is _sentinel:
            raise ValueError("Missing required arguments docstring/offset/message.")
        logger = get_logger("griffe")

    def warn(docstring: Docstring, offset: int, message: str, log_level: LogLevel = LogLevel.warning) -> None:
        try:
            prefix = docstring.parent.relative_filepath  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            prefix = "<module>"
        except BuiltinModuleError:
            prefix = f"<module: {docstring.parent.module.name}>"  # type: ignore[union-attr]
        log = getattr(logger, log_level.value)
        log(f"{prefix}:{(docstring.lineno or 0)+offset}: {message}")

    if name is not None:
        return warn

    warn(docstring, offset, message, log_level)
    return None


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
                parent=docstring.parent,
                log_level=log_level,
            )
            return name_or_expr or annotation
    return annotation
