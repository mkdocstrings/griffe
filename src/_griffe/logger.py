# This module contains the logger used throughout Griffe.
# The logger is actually a wrapper around the standard Python logger.
# We wrap it so that it is easier for other downstream libraries to patch it.
# For example, mkdocstrings-python patches the logger to relocate it as a child
# of `mkdocs.plugins` so that it fits in the MkDocs logging configuration.
#
# We use a single, global logger because our public API is exposed in a single module, `griffe`.

# YORE: Bump 1: Replace `patch_loggers` with `patch_logger` within file.
from __future__ import annotations

import logging
import warnings
from contextlib import contextmanager
from typing import Any, Callable, ClassVar, Iterator


class Logger:
    _default_logger: Any = logging.getLogger
    # YORE: Bump 1: Replace line with `_instance: _Logger | None = None`.
    _instances: ClassVar[dict[str, Logger]] = {}

    def __init__(self, name: str) -> None:
        # YORE: Bump 1: Uncomment block.
        # if self._instance:
        #     raise ValueError("Logger is a singleton.")

        # Default logger that can be patched by third-party.
        self._logger = self.__class__._default_logger(name)

    def __getattr__(self, name: str) -> Any:
        # Forward everything to the logger.
        return getattr(self._logger, name)

    @contextmanager
    def disable(self) -> Iterator[None]:
        """Temporarily disable logging."""
        old_level = self._logger.level
        self._logger.setLevel(100)
        try:
            yield
        finally:
            self._logger.setLevel(old_level)

    @classmethod
    def _get(cls, name: str = "griffe") -> Logger:
        # YORE: Bump 1: Replace line with `if not cls._instance:`.
        if name not in cls._instances:
            # YORE: Bump 1: Replace line with `cls._instance = cls(name)`.`
            cls._instances[name] = cls(name)
        # YORE: Bump 1: Replace line with `return cls._instance`.`
        return cls._instances[name]

    @classmethod
    def _patch_logger(cls, get_logger_func: Callable) -> None:
        # YORE: Bump 1: Uncomment block.
        # if not cls._instance:
        #     raise ValueError("Logger is not initialized.")

        # Patch current instance.
        # YORE: Bump 1: Replace block with `cls._instance._logger = get_logger_func(cls._instance._logger.name)`.
        for name, instance in cls._instances.items():
            instance._logger = get_logger_func(name)

        # Future instances will be patched as well.
        cls._default_logger = get_logger_func


# YORE: Bump 1: Uncomment block.
# logger: Logger = Logger._get()
# """Our global logger, used throughout the library.
#
# Griffe's output and error messages are logging messages.
#
# Griffe provides the [`patch_loggers`][griffe.patch_loggers]
# function so dependant libraries can patch Griffe's logger as they see fit.
#
# For example, to fit in the MkDocs logging configuration
# and prefix each log message with the module name:
#
# ```python
# import logging
# from griffe import patch_loggers
#
#
# class LoggerAdapter(logging.LoggerAdapter):
#     def __init__(self, prefix, logger):
#         super().__init__(logger, {})
#         self.prefix = prefix
#
#     def process(self, msg, kwargs):
#         return f"{self.prefix}: {msg}", kwargs
#
#
# def get_logger(name):
#     logger = logging.getLogger(f"mkdocs.plugins.{name}")
#     return LoggerAdapter(name, logger)
#
#
# patch_loggers(get_logger)
# ```
# """


# YORE: Bump 1: Remove block.
def get_logger(name: str) -> Logger:
    # YORE: Bump 1: Replace `Deprecated.` with `Deprecated, use [logger][griffe.logger] directly.`.
    """Deprecated. Create and return a new logger instance.

    Parameters:
        name: The logger name (unused).

    Returns:
        The logger.
    """
    # YORE: Bump 1: Replace `deprecated.` with `deprecated. Use [logger][griffe.logger] directly.`.
    warnings.warn("The `get_logger` function is deprecated.", DeprecationWarning, stacklevel=1)
    return Logger._get(name)


def patch_logger(get_logger_func: Callable[[str], Any]) -> None:
    """Patch Griffe's logger.

    Parameters:
        get_logger_func: A function accepting a name as parameter and returning a logger.
    """
    Logger._patch_logger(get_logger_func)


# YORE: Bump 1: Remove block.
def patch_loggers(get_logger_func: Callable[[str], Any]) -> None:
    """Deprecated, use `patch_logger` instead."""
    warnings.warn(
        "The `patch_loggers` function is deprecated. Use `patch_logger` instead.",
        DeprecationWarning,
        stacklevel=1,
    )
    return patch_logger(get_logger_func)
