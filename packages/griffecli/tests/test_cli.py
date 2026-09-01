# SPDX-License-Identifier: ISC

# Copyright (c) 2021, Timothée Mazzucotelli and contributors

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Tests for the CLI."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

import pytest

from griffe._internal import debug
from griffecli._internal import cli

if TYPE_CHECKING:
    from pathlib import Path


def test_main() -> None:
    """Basic CLI test."""
    if sys.platform == "win32":
        assert cli.main(["dump", "griffe", "-s", "src", "-oNUL"]) == 0
    else:
        assert cli.main(["dump", "griffe", "-s", "src", "-o/dev/null"]) == 0


@pytest.mark.parametrize("flag", ["-P", "--prefer-stubs-docstrings"])
def test_prefer_stubs_docstrings(tmp_path: Path, flag: str) -> None:
    """Prefer docstrings from stubs when requested.

    Parameters:
        tmp_path: Pytest fixture providing a temporary directory.
        flag: Short or long spelling of the CLI flag.
    """
    package_path = tmp_path / "package"
    package_path.mkdir()
    package_path.joinpath("__init__.py").write_text('"""Source."""', encoding="utf8")
    package_path.joinpath("__init__.pyi").write_text('"""Stubs."""', encoding="utf8")
    output_path = tmp_path / "output.json"

    assert cli.main(["dump", str(package_path), flag, "-o", str(output_path)]) == 0

    output = json.loads(output_path.read_text(encoding="utf8"))
    assert output["package"]["docstring"]["value"] == "Stubs."


def test_show_help(capsys: pytest.CaptureFixture) -> None:
    """Show help.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["-h"])
    captured = capsys.readouterr()
    assert "griffe" in captured.out


def test_show_version(capsys: pytest.CaptureFixture) -> None:
    """Show version.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["-V"])
    captured = capsys.readouterr()
    assert debug._get_version() in captured.out


def test_show_debug_info(capsys: pytest.CaptureFixture) -> None:
    """Show debug information.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["--debug-info"])
    captured = capsys.readouterr().out.lower()
    assert "python" in captured
    assert "system" in captured
    assert "environment" in captured
    assert "packages" in captured
