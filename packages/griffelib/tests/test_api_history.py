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

from griffe import temporary_visited_module, write_api_diff

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
        first_atomic, _ = write_api_diff(
            pkg_v1,
            pkg_v2,
            old_version="1.0",
            new_version="2.0",
            directory=directory,
        )
        _, history_path = write_api_diff(
            pkg_v2,
            pkg_v3,
            old_version="2.0",
            new_version="3.0",
            directory=directory,
        )

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

    objects = history["objects"]
    assert objects["pkg.added"]["added"] == "2.0"
    assert objects["pkg.added"]["exists"] is True
    assert objects["pkg.later"]["added"] == "3.0"
    assert objects["pkg.removed"]["removed"] == "2.0"
    assert objects["pkg.removed"]["exists"] is False
    assert objects["pkg.changed"]["added"] is None
    assert objects["pkg.changed"]["deprecated"] == {
        "message": "Use `new_replacement` instead.",
        "version": "2.0",
    }
    assert [event["version"] for event in objects["pkg.changed"]["events"]] == [
        "2.0",
        "2.0",
        "2.0",
        "3.0",
        "3.0",
        "3.0",
    ]


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
