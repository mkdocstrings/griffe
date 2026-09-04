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

"""Tests for API-history recording and consolidation."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from griffe import temporary_visited_module, temporary_visited_package, write_api_diff, write_api_diffs

if TYPE_CHECKING:
    from pathlib import Path


def test_write_and_consolidate_api_diffs(tmp_path: Path) -> None:
    """Record atomic diffs and derive current lifecycle state."""
    v1 = """
        def changed(value: int = 1) -> int: ...
        def removed() -> None: ...
    """
    v2 = """
        def changed(value: str = 2) -> int: ...
        def added() -> None: ...
    """
    v3 = """
        def changed(value: str = 3) -> str: ...
        def added() -> None: ...
        def later() -> None: ...
    """
    directory = tmp_path / ".apidiff"

    with (
        temporary_visited_module(v1, module_name="pkg") as pkg_v1,
        temporary_visited_module(v2, module_name="pkg") as pkg_v2,
        temporary_visited_module(v3, module_name="pkg") as pkg_v3,
    ):
        pkg_v2["changed"].deprecated = "Use `replacement` instead."
        pkg_v3["changed"].deprecated = "Use `new_replacement` instead."
        atomic_paths, history_path = write_api_diffs(
            (("1.0", pkg_v1), ("2.0", pkg_v2), ("3.0", pkg_v3)),
            directory=directory,
        )
        first_atomic = atomic_paths[0]

    atomic = json.loads(first_atomic.read_text(encoding="utf8"))
    assert atomic["schema_version"] == 1
    assert atomic["package"] == "pkg"
    assert atomic["old_version"] == "1.0"
    assert atomic["new_version"] == "2.0"
    parameter_change = next(change for change in atomic["changes"] if change["kind"] == "parameter_changed_default")
    assert parameter_change["object_path"] == "pkg.changed"
    assert parameter_change["old_value"] == {
        "annotation": "int",
        "default": "1",
        "kind": "positional or keyword",
        "name": "value",
        "required": False,
        "type": "parameter",
    }
    assert parameter_change["new_value"]["default"] == "2"

    history = json.loads(history_path.read_text(encoding="utf8"))["packages"]["pkg"]
    assert history["latest_version"] == "3.0"
    assert history["versions"] == ["1.0", "2.0", "3.0"]

    symbols = history["symbols"]
    assert symbols["pkg.added"]["added"] == "2.0"
    assert symbols["pkg.added"]["exists"] is True
    assert symbols["pkg.later"]["added"] == "3.0"
    assert symbols["pkg.removed"]["removed"] == "2.0"
    assert symbols["pkg.removed"]["exists"] is False
    assert symbols["pkg.changed"]["added"] is None
    assert symbols["pkg.changed"]["deprecated"] == {
        "message": "Use `new_replacement` instead.",
        "version": "2.0",
    }
    assert [event["version"] for event in symbols["pkg.changed"]["events"]] == [
        "2.0",
        "2.0",
        "2.0",
        "3.0",
        "3.0",
        "3.0",
    ]
    assert history["paths"]["pkg.changed"] == ["pkg.changed"]


def test_public_and_canonical_location_history(tmp_path: Path) -> None:
    """Track public exposure independently from private implementation locations."""
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
        canonical_move, _ = write_api_diff(
            pkg_v2,
            pkg_v3,
            old_version="2.0",
            new_version="3.0",
            directory=directory,
        )
        public_move, _ = write_api_diff(
            pkg_v3,
            pkg_v4,
            old_version="3.0",
            new_version="4.0",
            directory=directory,
        )
        _, history_path = write_api_diff(
            pkg_v4,
            pkg_v5,
            old_version="4.0",
            new_version="5.0",
            directory=directory,
        )

    canonical_changes = json.loads(canonical_move.read_text(encoding="utf8"))["changes"]
    thing_changes = [change for change in canonical_changes if change["object_path"] == "pkg.Thing"]
    assert [change["kind"] for change in thing_changes] == ["parameter_changed_default"]
    assert thing_changes[0]["old_canonical_path"] == "pkg._old.Thing"
    assert thing_changes[0]["new_canonical_path"] == "pkg._new.Thing"

    public_bindings = json.loads(public_move.read_text(encoding="utf8"))["bindings"]
    thing_binding = next(
        binding
        for binding in public_bindings
        if binding["old"] is not None and binding["old"]["public_path"] == "pkg.Thing"
    )
    assert thing_binding["new"]["public_path"] == "pkg.api.Thing"
    assert thing_binding["old"]["canonical_path"] == thing_binding["new"]["canonical_path"]

    history = json.loads(history_path.read_text(encoding="utf8"))["packages"]["pkg"]
    symbol_id = "pkg._old.Thing"
    symbol = history["symbols"][symbol_id]
    assert symbol["added"] == "2.0"
    assert symbol["removed"] == "5.0"
    assert symbol["exists"] is False
    assert symbol["public_locations"] == [
        {"path": "pkg.Thing", "added_in": "2.0", "removed_in": "4.0", "is_alias": True},
        {"path": "pkg.api.Thing", "added_in": "4.0", "removed_in": "5.0", "is_alias": True},
    ]
    assert symbol["canonical_locations"] == [
        {"path": "pkg._old.Thing", "since": "2.0", "until": "3.0"},
        {"path": "pkg._new.Thing", "since": "3.0", "until": "5.0"},
    ]
    assert [event["kind"] for event in symbol["events"]] == [
        "object_added",
        "parameter_changed_default",
        "object_removed",
    ]
    for path in ("pkg.Thing", "pkg.api.Thing", "pkg._old.Thing", "pkg._new.Thing"):
        assert history["paths"][path] == [symbol_id]


def test_reject_forked_history(tmp_path: Path) -> None:
    """Reject histories without one unambiguous latest version."""
    with (
        temporary_visited_module("", module_name="pkg") as pkg_v1,
        temporary_visited_module("a = 1", module_name="pkg") as pkg_v2,
        temporary_visited_module("b = 1", module_name="pkg") as pkg_v3,
    ):
        write_api_diff(pkg_v1, pkg_v2, old_version="1.0", new_version="2.0", directory=tmp_path)

        with pytest.raises(ValueError, match=r"forks at version '1\.0'"):
            write_api_diff(pkg_v1, pkg_v3, old_version="1.0", new_version="3.0", directory=tmp_path)
        assert not tmp_path.joinpath("atomic", "pkg--1.0--3.0.json").exists()


def test_unchanged_bindings_are_not_stored(tmp_path: Path) -> None:
    """Keep zero-change atomic and consolidated files small."""
    with (
        temporary_visited_module("def func(): ...", module_name="pkg") as pkg_v1,
        temporary_visited_module("def func(): ...", module_name="pkg") as pkg_v2,
    ):
        atomic_path, history_path = write_api_diff(
            pkg_v1,
            pkg_v2,
            old_version="1.0",
            new_version="1.1",
            directory=tmp_path,
        )

    atomic = json.loads(atomic_path.read_text(encoding="utf8"))
    assert atomic["bindings"] == []
    assert atomic["changes"] == []
    package = json.loads(history_path.read_text(encoding="utf8"))["packages"]["pkg"]
    assert package["symbols"] == {}
    assert package["paths"] == {}


def test_multiple_legacy_public_locations_use_shortest_path(tmp_path: Path) -> None:
    """Tolerate releases from before the single-public-location convention."""
    v1 = {
        "__init__.py": "from .mod import func\n__all__ = ['func']",
        "mod.py": "def func(value=1): ...",
    }
    v2 = {
        "__init__.py": "from .mod import func\n__all__ = ['func']",
        "mod.py": "def func(value=2): ...",
    }
    with (
        temporary_visited_package("pkg", v1) as pkg_v1,
        temporary_visited_package("pkg", v2) as pkg_v2,
    ):
        atomic_path, history_path = write_api_diff(
            pkg_v1,
            pkg_v2,
            old_version="1.0",
            new_version="2.0",
            directory=tmp_path,
        )

    atomic = json.loads(atomic_path.read_text(encoding="utf8"))
    changes = [change for change in atomic["changes"] if change["kind"] == "parameter_changed_default"]
    assert len(changes) == 1
    assert changes[0]["object_path"] == "pkg.func"

    history = json.loads(history_path.read_text(encoding="utf8"))["packages"]["pkg"]
    assert history["symbols"]["pkg.mod.func"]["public_locations"] == [
        {"path": "pkg.func", "added_in": None, "removed_in": None, "is_alias": True},
    ]
