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

# This top-level module imports all public names from the CLI package,
# and exposes them as public objects.

"""Griffe CLI package.

The CLI (Command Line Interface) for the griffe library.
This package provides command-line tools for interacting with griffe.

## CLI entrypoints

- [`griffecli.main`][]: Run the main program.
- [`griffecli.check`][]: Check for API breaking changes in two versions of the same package.
- [`griffecli.dump`][]: Load packages data and dump it as JSON.
- [`griffecli.get_parser`][]: Get the argument parser for the CLI.
"""

from __future__ import annotations

from griffecli._internal.cli import DEFAULT_LOG_LEVEL, check, dump, get_parser, main

__all__ = [
    "DEFAULT_LOG_LEVEL",
    "check",
    "dump",
    "get_parser",
    "main",
]
