"""This module contains logging utilities.

We provide the [`patch_loggers`][griffe.logger.patch_loggers]
function so dependant libraries can patch loggers as they see fit.

For example, to fit in the MkDocs logging configuration
and prefix each log message with the module name:

```python
import logging
from griffe.logger import patch_loggers


class LoggerAdapter(logging.LoggerAdapter):
    def __init__(self, prefix, logger):
        super().__init__(logger, {})
        self.prefix = prefix

    def process(self, msg, kwargs):
        return f"{self.prefix}: {msg}", kwargs


def get_logger(name):
    logger = logging.getLogger(f"mkdocs.plugins.{name}")
    return LoggerAdapter(name, logger)


patch_loggers(get_logger)
```
"""

from __future__ import annotations

import logging
import string
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Any, Callable, ClassVar, Protocol


def _add_logging_level(name: str, number: int, method: str | None = None) -> None:
    if not method:
        method = name.lower()

    if hasattr(logging, name):
        raise AttributeError(f"{name} already defined in logging module")
    if hasattr(logging, method):
        raise AttributeError(f"{method} already defined in logging module")
    if hasattr(logging.getLoggerClass(), method):
        raise AttributeError(f"{method} already defined in logger class")

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs) -> None:  # noqa: ANN001,ANN002,ANN003,N802
        if self.isEnabledFor(number):
            self._log(number, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs) -> None:  # noqa: ANN001,ANN002,ANN003,N802
        logging.log(number, message, *args, **kwargs)

    logging.addLevelName(number, name)
    setattr(logging, name, number)
    setattr(logging.getLoggerClass(), method, logForLevel)
    setattr(logging, method, logToRoot)


_add_logging_level("TRACE", logging.DEBUG - 5)
_add_logging_level("SUCCESS", logging.INFO + 5)


class LogLevel(Enum):
    """Enumeration of available log levels."""

    trace: str = "trace"
    debug: str = "debug"
    info: str = "info"
    success: str = "success"
    warning: str = "warning"
    error: str = "error"
    critical: str = "critical"

    @property
    def number(self) -> int:
        """Number corresponding to this log level."""
        return getattr(logging, self.value.upper())


class LoggerLike(Protocol):
    def log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> None: ...


class LogMessage:
    _formatter = string.Formatter()

    def __init__(self, code: str, message: str, level: LogLevel, max_level: LogLevel) -> None:
        self._code = code
        self._message = message
        self._level = level
        self._max_level = max_level

    @staticmethod
    def _fields(format_string: str) -> list[str]:
        return [part[1] for part in LogMessage._formatter.parse(format_string) if part[1] is not None]

    @property
    def code(self) -> str:
        return self._code

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        current_fields = LogMessage._fields(self._message)
        new_fields = LogMessage._fields(message)
        if new_fields != current_fields:
            raise ValueError(
                f"New message fields {new_fields!r} are not equal to current message fields {current_fields!r}",
            )
        self._message = message

    @property
    def level(self) -> LogLevel:
        return self._level

    @level.setter
    def level(self, level: str | LogLevel) -> None:
        level = LogLevel(level)
        if level.number > self._max_level.number:
            raise ValueError(
                f"Cannot set level {level.value} ({level.number}), "
                f"max-level is {self._max_level.value} ({self._max_level.number})",
            )
        self._level = LogLevel(level)

    def __call__(
        self, logger: LoggerLike, *args: Any, filepath: str | Path = "", lineno: int | str = "", **kwargs: Any
    ) -> Any:
        formatted = self._message.format(*args, **kwargs)
        logger.log(
            self._level.number,
            f"{filepath}:{lineno}: {formatted} [{self._code} {self._level.value}]",
            stacklevel=2,
        )


class Logger:
    _default_logger: Callable[[str | None], LoggerLike] = logging.getLogger
    _instances: ClassVar[dict[str, Logger]] = {}
    messages: ClassVar[dict[str, LogMessage]] = {}

    def __init__(self, name: str) -> None:
        # Default logger that can be patched by third-party.
        self._logger = self.__class__._default_logger(name)
        # Register instance.
        self._instances[name] = self

    def __getattr__(self, name: str) -> Any:
        try:
            # Forward everything to the logger.
            return partial(self._logger.log, LogLevel(name).number, stacklevel=1)
        except ValueError:
            return partial(self.messages[name], self._logger)

    @classmethod
    def add_message(
        cls,
        name: str,
        message: str,
        level: str | LogLevel = "debug",
        max_level: str | LogLevel | None = None,
    ) -> None:
        log_message = LogMessage(
            code=name.replace("_", "-"),
            message=message,
            level=LogLevel(level),
            max_level=LogLevel(max_level) if max_level else LogLevel.critical,
        )
        cls.messages[name] = log_message

    @classmethod
    def _patch_loggers(cls, get_logger_func: Callable) -> None:
        # Patch current instances.
        for name, instance in cls._instances.items():
            instance._logger = get_logger_func(name)
        # Future instances will be patched as well.
        cls._default_logger = get_logger_func


Logger.add_message("could_not_unwrap", "Could not unwrap {name}: {error!r}", level=LogLevel.debug)
Logger.add_message("empty_package_name", "Empty package name, continuing", level=LogLevel.debug)
Logger.add_message("loading_package", "Loading package {package}", level=LogLevel.info, max_level=LogLevel.info)
Logger.add_message("could_not_find_package", "Could not find package {package}: {error}", level=LogLevel.error)
Logger.add_message("finished_loading", "Finished loading packages", level=LogLevel.info, max_level=LogLevel.success)
Logger.add_message(
    "starting_alias_resolution",
    "Starting alias resolution",
    level=LogLevel.info,
    max_level=LogLevel.info,
)
Logger.add_message(
    "unresolved_aliases",
    "{unresolved} aliases were still unresolved after {iterations} iterations",
    level=LogLevel.info,
)
Logger.add_message(
    "all_resolved",
    "All aliases were resolved after {iterations} iterations",
    level=LogLevel.info,
    max_level=LogLevel.success,
)
Logger.add_message(
    "loading_path",
    "Loading path",
    level=LogLevel.debug,
    max_level=LogLevel.info,
)
Logger.add_message("found", "Found {objspec}: loading", level=LogLevel.debug, max_level=LogLevel.info)
Logger.add_message("cannot_compute_mro", "{error}", level=LogLevel.debug)
Logger.add_message(
    "cannot_resolve_base_class",
    "Base class {base_path} is not loaded, or not static, it cannot be resolved",
    level=LogLevel.debug,
)
Logger.add_message(
    "skip_alias", "API check: {old_obj_path} | {new_obj_path}: skip alias with unknown target", level=LogLevel.debug
)
Logger.add_message("skip_private_object", "API check: {obj_path}: skip private object", level=LogLevel.debug)
Logger.add_message("checking", "API check: {obj_path}", level=LogLevel.debug)
Logger.add_message(
    "failed_to_parse_node",
    "Tried and failed to parse {node.value!r} as Python code, "
    "falling back to using it as a string literal "
    "(postponed annotations might help: https://peps.python.org/pep-0563/)",
    level=LogLevel.debug,
)
Logger.add_message("skip_module", "Skip {module_path}, another module took precedence", level=LogLevel.debug)
Logger.add_message("builtin_module", "{module} is a builtin module", level=LogLevel.debug)
Logger.add_message("inspecting_module", "Inspecting {module}", level=LogLevel.debug)
Logger.add_message("could_not_find_module", "Could not find {module}", level=LogLevel.debug)
Logger.add_message("trying_inspection", "Trying inspection on {module}", level=LogLevel.debug)
Logger.add_message(
    "finished_iteration",
    "Iteration {iteration} finished, {resolved} aliases resolved, still {unresolved} to go",
    level=LogLevel.debug,
)
Logger.add_message(
    "cannot_expand", "Cannot expand '{path}', try pre-loading corresponding package", level=LogLevel.debug
)
Logger.add_message(
    "unsupported_all_item",
    "Unsupported item in {module_path}.__all__: {item} (use strings only)",
    level=LogLevel.warning,
)
Logger.add_message(
    "could_not_expand_wildcard_error",
    "Could not expand wildcard import {name} in {path}: {error}",
    level=LogLevel.debug,
)
Logger.add_message(
    "could_not_expand_wildcard_missing",
    "Could not expand wildcard import {name} in {path}: {target} not found in modules collection",
    level=LogLevel.debug,
)
Logger.add_message("failed_to_resolve_alias", "Failed to resolve alias {path} -> {target}", level=LogLevel.debug)
Logger.add_message("could_not_follow_alias", "Could not follow alias {path}: {error}", level=LogLevel.debug)
Logger.add_message("cyclic_alias_error", "{error}", level=LogLevel.debug)
Logger.add_message("alias_resolved", "Alias {path} was resolved to {final_path}", level=LogLevel.debug)
Logger.add_message("skip_module_with_dots", "Skip {module}, dots in filenames are not supported", level=LogLevel.debug)
Logger.add_message("missing_init_module", "{error}. Missing __init__ module?", level=LogLevel.debug)
Logger.add_message(
    "submodule_shadowing_member",
    "Submodule '{path}' is shadowing the member at the same path. "
    "We recommend renaming the member or the submodule (for example prefixing it with `_`), "
    "see https://mkdocstrings.github.io/griffe/best_practices/#avoid-member-submodule-name-shadowing.",
    level=LogLevel.debug,
)
Logger.add_message("cannot_merge_stubs", "Cannot merge stubs for {path}: kind {kind1} != {kind2}", level=LogLevel.debug)
Logger.add_message("trying_to_merge_stubs", "Trying to merge {filepath1} and {filepath2}", level=LogLevel.debug)


def get_logger(name: str) -> Logger:
    """Create and return a new logger instance.

    Parameters:
        name: The logger name.

    Returns:
        The logger.
    """
    return Logger(name)


def patch_loggers(get_logger_func: Callable[[str], Any]) -> None:
    """Patch loggers.

    Parameters:
        get_logger_func: A function accepting a name as parameter and returning a logger.
    """
    Logger._patch_loggers(get_logger_func)


__all__ = ["get_logger", "LogLevel", "patch_loggers"]
