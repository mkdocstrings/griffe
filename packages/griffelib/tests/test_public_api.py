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

# Tests for public API handling.

from griffe import temporary_visited_module


def test_not_detecting_imported_objects_as_public() -> None:
    """Imported objects not listed in `__all__` must not be considered public."""
    with temporary_visited_module("from abc import ABC\ndef func(): ...") as module:
        assert not module["ABC"].is_public
        assert module["func"].is_public  # Control case.


def test_detecting_dunder_attributes_as_public() -> None:
    """Dunder attributes (methods, etc.) must be considered public."""
    with temporary_visited_module(
        """
        def __getattr__(name): ...
        class A:
            def __init__(self): ...
        """,
    ) as module:
        assert module["__getattr__"].is_public
        assert module["A.__init__"].is_public
