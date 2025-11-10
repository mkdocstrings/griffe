# Loggers

## **Main API**

## logger

```
logger: Logger = _get()
```

Our global logger, used throughout the library.

Griffe's output and error messages are logging messages.

Griffe provides the patch_loggers function so dependent libraries can patch Griffe loggers as they see fit.

For example, to fit in the MkDocs logging configuration and prefix each log message with the module name:

```
import logging
from griffe import patch_loggers


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

## get_logger

```
get_logger(name: str = 'griffe') -> Logger
```

Create and return a new logger instance.

Parameters:

- ### **`name`**

  (`str`, default: `'griffe'` ) – The logger name.

Returns:

- `Logger` – The logger.

Source code in `src/griffe/_internal/logger.py`

```
def get_logger(name: str = "griffe") -> Logger:
    """Create and return a new logger instance.

    Parameters:
        name: The logger name.

    Returns:
        The logger.
    """
    return Logger._get(name)
```

## Logger

```
Logger(name: str)
```

Methods:

- **`disable`** – Temporarily disable logging.

Source code in `src/griffe/_internal/logger.py`

```
def __init__(self, name: str) -> None:
    # Default logger that can be patched by third-party.
    self._logger = self.__class__._default_logger(name)
```

### disable

```
disable() -> Iterator[None]
```

Temporarily disable logging.

Source code in `src/griffe/_internal/logger.py`

```
@contextmanager
def disable(self) -> Iterator[None]:
    """Temporarily disable logging."""
    old_level = self._logger.level
    self._logger.setLevel(100)
    try:
        yield
    finally:
        self._logger.setLevel(old_level)
```

## LogLevel

Bases: `str`, `Enum`

```
              flowchart TD
              griffe.LogLevel[LogLevel]

              

              click griffe.LogLevel href "" "griffe.LogLevel"
```

Enumeration of available log levels.

Attributes:

- **`critical`** – The CRITICAL log level.
- **`debug`** – The DEBUG log level.
- **`error`** – The ERROR log level.
- **`info`** – The INFO log level.
- **`success`** – The SUCCESS log level.
- **`trace`** – The TRACE log level.
- **`warning`** – The WARNING log level.

### critical

```
critical = 'critical'
```

The CRITICAL log level.

### debug

```
debug = 'debug'
```

The DEBUG log level.

### error

```
error = 'error'
```

The ERROR log level.

### info

```
info = 'info'
```

The INFO log level.

### success

```
success = 'success'
```

The SUCCESS log level.

### trace

```
trace = 'trace'
```

The TRACE log level.

### warning

```
warning = 'warning'
```

The WARNING log level.

## DEFAULT_LOG_LEVEL

```
DEFAULT_LOG_LEVEL = os.getenv(
    "GRIFFE_LOG_LEVEL", "INFO"
).upper()
```

The default log level for the CLI.

This can be overridden by the `GRIFFE_LOG_LEVEL` environment variable.

## **Advanced API**

## patch_loggers

```
patch_loggers(
    get_logger_func: Callable[[str], Any],
) -> None
```

Patch Griffe logger and Griffe extensions' loggers.

Parameters:

- ### **`get_logger_func`**

  (`Callable[[str], Any]`) – A function accepting a name as parameter and returning a logger.

Source code in `src/griffe/_internal/logger.py`

```
def patch_loggers(get_logger_func: Callable[[str], Any]) -> None:
    """Patch Griffe logger and Griffe extensions' loggers.

    Parameters:
        get_logger_func: A function accepting a name as parameter and returning a logger.
    """
    Logger._patch_loggers(get_logger_func)
```
