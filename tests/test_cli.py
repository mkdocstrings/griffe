"""Tests for the `cli` module."""

from __future__ import annotations

import sys

import pytest

from griffe import cli


def test_main() -> None:
    """Basic CLI test."""
    if sys.platform == "win32":
        assert cli.main(["dump", "griffe", "-s", "src", "-oNUL"]) == 0
    else:
        assert cli.main(["dump", "griffe", "-s", "src", "-o/dev/null"]) == 0


def test_show_help(capsys: pytest.CaptureFixture) -> None:
    """Show help.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["-h"])
    captured = capsys.readouterr()
    assert "griffe" in captured.out
