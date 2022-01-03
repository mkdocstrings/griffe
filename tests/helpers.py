"""General helpers for tests."""

from __future__ import annotations

import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from griffe.agents.inspector import inspect
from griffe.dataclasses import Module
from tests import TESTS_DIR, TMP_DIR


@contextmanager
def temporary_pyfile(code: str) -> Iterator[tuple[str, Path]]:
    """Create a module.py file containing the given code in a temporary directory.

    Parameters:
        code: The code to write to the temporary file.

    Yields:
        module_name: The module name, as to dynamically import it.
        module_path: The module path.
    """
    with tempfile.TemporaryDirectory(dir=TMP_DIR) as tmpdir:
        tmpdirpath = Path(tmpdir).relative_to(TESTS_DIR.parent)
        tmpfile = tmpdirpath / "module.py"
        tmpfile.write_text(code)
        yield ".".join(tmpdirpath.parts) + ".module", tmpfile


@contextmanager
def temporary_inspected_module(code: str) -> Iterator[Module]:
    """Create and inspect a temporary module with the given code.

    Parameters:
        code: The code of the module.

    Yields:
        The inspected module.
    """
    with temporary_pyfile(code) as (name, path):
        yield inspect(name, filepath=path)
