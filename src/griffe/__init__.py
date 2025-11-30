"""Griffe package.

Signatures for entire Python programs.
Extract the structure, the frame, the skeleton of your project,
to generate API documentation or find breaking changes in your API.

This is a backward-compatible package that re-exports all public symbols from
both `griffelib` (the library) and `griffecli` (the CLI).

The entirety of the public API is exposed here, in the top-level `griffe` module.

All messages written to standard output or error are logged using the `logging` module.
Our logger's name is set to `"griffe"` and is public (you can rely on it).
You can obtain the logger from the standard `logging` module: `logging.getLogger("griffe")`.
Actual logging messages are not part of the public API (they might change without notice).

Raised exceptions throughout the package are part of the public API (you can rely on them).
Their actual messages are not part of the public API (they might change without notice).

See the `griffelib` and `griffecli` packages for detailed API documentation.
"""

from griffecli import *
from griffecli import __all__ as __cli_all__
from griffelib import *
from griffelib import __all__ as __lib_all__

__all__ = [*__lib_all__, *__cli_all__]
