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

# Our Griffe extensions.

# YORE: Bump 3: Remove file.

from typing import Any

import griffe

_deprecated_objects = {
    "AttributeChangedValueBreakage",
    "BreakageKind.ATTRIBUTE_CHANGED_VALUE",
}


class DeprecationExtension(griffe.Extension):
    def _apply(self, obj: griffe.Object | griffe.Alias) -> None:
        obj.deprecated = True
        if obj.docstring:
            obj.docstring.parsed.append(
                griffe.DocstringSectionAdmonition(
                    kind="danger",
                    title="Deprecated since v2.4.1.",
                    text="Deprecated, and removed in next major version.",
                ),
            )

    def on_package(self, *, pkg: griffe.Module, **kwargs: Any) -> None:  # noqa: ARG002
        """Apply `deprecated=true` on specific objects."""
        if pkg.name == "griffe":
            for obj in _deprecated_objects:
                self._apply(pkg[obj])
