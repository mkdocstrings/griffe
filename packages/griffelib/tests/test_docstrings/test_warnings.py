# SPDX-License-Identifier: ISC
#
# Copyright (c) 2021, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Tests for the docstrings utility functions.

from __future__ import annotations

from griffe import Docstring, Function, Parameter, ParameterKind, Parameters, Parser, parse


def test_can_warn_without_parent_module() -> None:
    """Assert we can parse a docstring even if it does not have a parent module."""
    function = Function(
        "func",
        parameters=Parameters(
            Parameter("param1", annotation=None, kind=ParameterKind.positional_or_keyword),
            Parameter("param2", annotation="int", kind=ParameterKind.keyword_only),
        ),
    )
    text = """
    Hello I'm a docstring!

    Parameters:
        param1: Description.
        param2: Description.
    """
    docstring = Docstring(text, lineno=1, parent=function)
    assert parse(docstring, Parser.google)
