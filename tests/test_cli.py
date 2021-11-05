"""Tests for the `cli` module."""

import pytest

from griffe import cli


def test_main():
    """Basic CLI test."""
    assert cli.main(["griffe", "-s", "src"]) == 0


def test_show_help(capsys):
    """
    Show help.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["-h"])
    captured = capsys.readouterr()
    assert "griffe" in captured.out
