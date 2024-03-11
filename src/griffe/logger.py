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
from typing import Any, Callable, ClassVar


class LogLevel(Enum):
    """Enumeration of available log levels."""

    trace: str = "trace"
    debug: str = "debug"
    info: str = "info"
    success: str = "success"
    warning: str = "warning"
    error: str = "error"
    critical: str = "critical"


class _Log:
    _formatter = string.Formatter()

    def __init__(self, message: str, level: str | LogLevel = "debug") -> None:
        self._message = message
        self._level = level if isinstance(level, str) else level.value

    @staticmethod
    def _fields(format_string: str) -> list[str]:
        return [part[1] for part in _Log._formatter.parse(format_string) if part[1] is not None]

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        current_fields = _Log._fields(self._message)
        new_fields = _Log._fields(message)
        if new_fields != current_fields:
            raise ValueError(
                f"New message fields {new_fields!r} are not equal to current message fields {current_fields!r}",
            )
        self._message = message

    @property
    def level(self) -> str:
        return self._level

    @level.setter
    def level(self, level: str | LogLevel) -> None:
        self._level = level if isinstance(level, str) else level.value

    def __call__(self, logger: _Logger, *args: Any, **kwargs: Any) -> Any:
        getattr(logger, self._level)(self._message.format(*args, **kwargs))


class _Logger:
    _default_logger: Any = logging.getLogger
    _instances: ClassVar[dict[str, _Logger]] = {}

    could_not_unwrap = _Log("Could not unwrap {name}: {error!r}", level=LogLevel.debug)
    empty_package_name = _Log("Empty package name, continuing", level=LogLevel.debug)
    loading_package = _Log("Loading package {package}", level=LogLevel.info)
    could_not_find_package = _Log("Could not find package {package}: {error}", level=LogLevel.error)
    finished_loading = _Log("Finished loading packages", level=LogLevel.info)
    starting_alias_resolution = _Log("Starting alias resolution", level=LogLevel.info)
    unresolved_aliases = _Log(
        "{len(unresolved)} aliases were still unresolved after {iterations} iterations",
        level=LogLevel.info,
    )
    all_resolved = _Log("All aliases were resolved after {iterations} iterations", level=LogLevel.info)

    def __init__(self, name: str) -> None:
        # Default logger that can be patched by third-party.
        self._logger = self.__class__._default_logger(name)
        # Register instance.
        self._instances[name] = self

    def __getattr__(self, name: str) -> Any:
        # Forward everything to the logger.
        return getattr(self._logger, name)

    @classmethod
    def _patch_loggers(cls, get_logger_func: Callable) -> None:
        # Patch current instances.
        for name, instance in cls._instances.items():
            instance._logger = get_logger_func(name)
        # Future instances will be patched as well.
        cls._default_logger = get_logger_func


def get_logger(name: str) -> _Logger:
    """Create and return a new logger instance.

    Parameters:
        name: The logger name.

    Returns:
        The logger.
    """
    return _Logger(name)


def patch_loggers(get_logger_func: Callable[[str], Any]) -> None:
    """Patch loggers.

    Parameters:
        get_logger_func: A function accepting a name as parameter and returning a logger.
    """
    _Logger._patch_loggers(get_logger_func)


__all__ = ["get_logger", "LogLevel", "patch_loggers"]
