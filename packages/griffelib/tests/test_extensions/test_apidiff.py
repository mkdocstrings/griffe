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

"""Tests for the built-in API-diff extension."""

from __future__ import annotations

from typing import TYPE_CHECKING

from griffe import (
    DocstringSectionKind,
    load_extensions,
    temporary_visited_module,
    temporary_visited_package,
    write_api_diff,
)

if TYPE_CHECKING:
    from pathlib import Path

    from griffe import Object


def _admonitions(obj: Object) -> dict[str, str]:
    assert obj.docstring is not None
    return {
        section.title or "": section.value.description
        for section in obj.docstring.parsed
        if section.kind is DocstringSectionKind.admonition
    }


def test_inject_api_history_admonitions(tmp_path: Path) -> None:
    """Inject lifecycle and change callouts, including removals on surviving parents."""
    old_code = """
        def changed(value=1):
            '''Existing docs.'''

        def removed(): ...

        class Container:
            def removed_method(self): ...
    """
    new_code = """
        def changed(value=2):
            '''Existing docs.'''

        def added(): ...

        class Container:
            '''Container docs.'''
    """
    directory = tmp_path / ".apidiff"
    with (
        temporary_visited_module(old_code, module_name="pkg") as old_package,
        temporary_visited_module(new_code, module_name="pkg") as new_package,
    ):
        new_package["changed"].deprecated = "Use `replacement` instead."
        write_api_diff(
            old_package,
            new_package,
            old_version="1.0",
            new_version="2.0",
            directory=directory,
        )

    extensions = load_extensions({"apidiff": {"path": directory / "diff.json"}})
    with temporary_visited_package(
        "pkg",
        {"__init__.py": new_code},
        extensions=extensions,
        docstring_parser="google",
    ) as package:
        changed = _admonitions(package["changed"])
        added = _admonitions(package["added"])
        container = _admonitions(package["Container"])
        package_admonitions = _admonitions(package)

    assert changed["Deprecated in version 2.0"] == "Use `replacement` instead."
    assert changed["Changed in version 2.0"] == "Parameter `value` default changed from `1` to `2`."
    assert added == {"Added in version 2.0": ""}
    assert container["Removed in version 2.0"] == "- `pkg.Container.removed_method`"
    assert package_admonitions["Removed in version 2.0"] == "- `pkg.removed`"


def test_missing_api_history_is_a_noop(tmp_path: Path) -> None:
    """Allow enabling the extension before a history has been generated."""
    extensions = load_extensions({"apidiff": {"path": tmp_path / "missing.json"}})
    with temporary_visited_package("pkg", {"__init__.py": "def func(): ..."}, extensions=extensions) as package:
        assert package["func"].docstring is None


def test_admonitions_remain_chronological(tmp_path: Path) -> None:
    """Keep lifecycle callouts interleaved chronologically with ordinary changes."""
    directory = tmp_path / ".apidiff"
    with (
        temporary_visited_module("def func(value=1): ...", module_name="pkg") as pkg_v1,
        temporary_visited_module("def func(value=2): ...", module_name="pkg") as pkg_v2,
        temporary_visited_module("def func(value=2): ...", module_name="pkg") as pkg_v3,
    ):
        pkg_v3["func"].deprecated = "Use `replacement` instead."
        write_api_diff(pkg_v1, pkg_v2, old_version="1.0", new_version="2.0", directory=directory)
        write_api_diff(pkg_v2, pkg_v3, old_version="2.0", new_version="3.0", directory=directory)

    extensions = load_extensions({"apidiff": {"path": directory / "diff.json"}})
    with temporary_visited_package(
        "pkg",
        {"__init__.py": "def func(value=2): ..."},
        extensions=extensions,
    ) as package:
        sections = [
            section for section in package["func"].docstring.parsed if section.kind is DocstringSectionKind.admonition
        ]

    assert [(section.title, section.value.annotation) for section in sections] == [
        ("Changed in version 2.0", "warning"),
        ("Deprecated in version 3.0", "warning"),
    ]


def test_lifecycle_admonitions_without_details_have_no_body(tmp_path: Path) -> None:
    """Leave lifecycle admonition bodies empty when their titles say everything."""
    code_with_both = "def deprecated(): ...\n\ndef readded(): ..."
    code_without_readded = "def deprecated(): ..."
    directory = tmp_path / ".apidiff"
    with (
        temporary_visited_module(code_with_both, module_name="pkg") as pkg_v1,
        temporary_visited_module(code_without_readded, module_name="pkg") as pkg_v2,
        temporary_visited_module(code_with_both, module_name="pkg") as pkg_v3,
    ):
        pkg_v2["deprecated"].deprecated = True
        write_api_diff(pkg_v1, pkg_v2, old_version="1.0", new_version="2.0", directory=directory)
        write_api_diff(pkg_v2, pkg_v3, old_version="2.0", new_version="3.0", directory=directory)

    extensions = load_extensions({"apidiff": {"path": directory / "diff.json"}})
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code_with_both},
        extensions=extensions,
    ) as package:
        deprecated = _admonitions(package["deprecated"])
        readded = _admonitions(package["readded"])

    assert deprecated == {
        "Deprecated in version 2.0": "",
        "No longer deprecated in version 3.0": "",
    }
    assert readded == {
        "Removed in version 2.0": "",
        "Added in version 3.0": "",
    }


def test_alias_history_follows_targets_across_locations(tmp_path: Path) -> None:
    """Inject one public history through old and new aliases and canonical targets."""
    v1 = {
        "__init__.py": "__all__ = []",
        "_old.py": "def Thing(value=1): ...",
    }
    v2 = {
        "__init__.py": "from ._old import Thing\n__all__ = ['Thing']",
        "_old.py": "def Thing(value=1): ...",
    }
    v3 = {
        "__init__.py": "from ._new import Thing\n__all__ = ['Thing']",
        "_new.py": "def Thing(value=2): ...",
    }
    v4 = {
        "__init__.py": "from . import api\n__all__ = ['api']",
        "api.py": "from ._new import Thing\n__all__ = ['Thing']",
        "_new.py": "def Thing(value=2): ...",
    }
    v5 = {
        "__init__.py": "from . import api\n__all__ = ['api']",
        "api.py": "__all__ = []",
        "_new.py": "def Thing(value=2): ...",
    }
    directory = tmp_path / ".apidiff"

    with (
        temporary_visited_package("pkg", v1) as pkg_v1,
        temporary_visited_package("pkg", v2) as pkg_v2,
        temporary_visited_package("pkg", v3) as pkg_v3,
        temporary_visited_package("pkg", v4) as pkg_v4,
        temporary_visited_package("pkg", v5) as pkg_v5,
    ):
        write_api_diff(pkg_v1, pkg_v2, old_version="1.0", new_version="2.0", directory=directory)
        write_api_diff(pkg_v2, pkg_v3, old_version="2.0", new_version="3.0", directory=directory)
        write_api_diff(pkg_v3, pkg_v4, old_version="3.0", new_version="4.0", directory=directory)
        write_api_diff(pkg_v4, pkg_v5, old_version="4.0", new_version="5.0", directory=directory)

    extensions = load_extensions({"apidiff": {"path": directory / "diff.json"}})
    with temporary_visited_package("pkg", v4, extensions=extensions) as package:
        thing = _admonitions(package["api.Thing"])

    assert thing == {
        "Added in version 2.0": (
            "`Thing` was publicly exposed as `pkg.Thing` in version 2.0 and `pkg.api.Thing` in version 4.0."
        ),
        "Changed in version 3.0": "Parameter `value` default changed from `1` to `2`.",
        "Removed in version 5.0": (
            "`Thing` was removed from `pkg.Thing` in version 4.0 and `pkg.api.Thing` in version 5.0."
        ),
    }

    extensions = load_extensions({"apidiff": {"path": directory / "diff.json"}})
    with temporary_visited_package("pkg", v5, extensions=extensions) as package:
        private_thing = _admonitions(package["_new.Thing"])
        api = _admonitions(package["api"])

    assert private_thing == thing
    assert api["Removed in version 5.0"] == "- `pkg.api.Thing`"
