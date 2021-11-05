"""This module contains logging utilities.

We provide the [`get_logger`][griffe.logger.get_logger]
function so dependant libraries can patch it as they see fit.

For example, to fit in the MkDocs logging configuration
and prefix each log message with the module name:

```python
import logging
from griffe import logger as griffe_logger

class LoggerAdapter(logging.LoggerAdapter):
    def __init__(self, prefix, logger):
        super().__init__(logger, {})
        self.prefix = prefix

    def process(self, msg, kwargs):
        return f"{self.prefix}: {msg}", kwargs

def get_logger(name):
    logger = logging.getLogger(f"mkdocs.plugins.{name}")
    return LoggerAdapter(name, logger)


griffe_logger.get_logger = get_logger
```
"""  # noqa: P102

import logging


def get_logger(name: str) -> logging.Logger:
    """Create and return a new logger instance.

    Parameters:
        name: The logger name.

    Returns:
        The logger.
    """
    return logging.getLogger(name)
