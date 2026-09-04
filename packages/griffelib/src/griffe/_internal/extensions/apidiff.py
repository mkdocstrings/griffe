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

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from griffe._internal.api_history import _API_DIFF_SCHEMA_VERSION
from griffe._internal.docstrings.models import DocstringSectionAdmonition
from griffe._internal.enumerations import ChangeFlag, ChangeKind
from griffe._internal.extensions.base import Extension
from griffe._internal.logger import logger
from griffe._internal.models import Docstring

if TYPE_CHECKING:
    from griffe._internal.models import Module, Object


_OBJECT_ADDED = ChangeKind.OBJECT_ADDED.name.lower()
_OBJECT_REMOVED = ChangeKind.OBJECT_REMOVED.name.lower()
_OBJECT_DEPRECATED = ChangeKind.OBJECT_DEPRECATED.name.lower()
_OBJECT_UNDEPRECATED = ChangeKind.OBJECT_UNDEPRECATED.name.lower()


def _append_admonition(obj: Object, *, kind: str, title: str, text: str) -> None:
    if obj.docstring is None:
        obj.docstring = Docstring("", parent=obj)
    obj.docstring.parsed.append(DocstringSectionAdmonition(kind, text, title=title))


def _changed_admonition(version: str, changes: list[dict[str, Any]]) -> tuple[str, str, str]:
    summaries = [change["summary"] for change in changes]
    text = summaries[0] if len(summaries) == 1 else "\n".join(f"- {summary}" for summary in summaries)
    flags = {flag for change in changes for flag in change["flags"]}
    if flags & {ChangeFlag.BREAKING.value, ChangeFlag.DEPRECATION.value, ChangeFlag.WARNING.value}:
        kind = "warning"
    elif ChangeFlag.HINT.value in flags:
        kind = "tip"
    else:
        kind = "note"
    return kind, f"Changed in version {version}", text


def _object_admonitions(events: list[dict[str, Any]]) -> list[tuple[str, str, str]]:
    admonitions = []
    index = 0
    while index < len(events):
        version = events[index]["version"]
        version_events = []
        while index < len(events) and events[index]["version"] == version:
            version_events.append(events[index])
            index += 1

        changed = []
        for event in version_events:
            if event["kind"] == _OBJECT_ADDED:
                admonitions.append(("tip", f"Added in version {version}", "This object was added."))
            elif event["kind"] == _OBJECT_REMOVED:
                admonitions.append(("danger", f"Removed in version {version}", "This object was removed."))
            elif event["kind"] == _OBJECT_DEPRECATED:
                message = event["new_value"] if isinstance(event["new_value"], str) else None
                admonitions.append(
                    ("warning", f"Deprecated in version {version}", message or "This object was deprecated."),
                )
            elif event["kind"] == _OBJECT_UNDEPRECATED:
                admonitions.append(
                    ("info", f"No longer deprecated in version {version}", "This object is no longer deprecated."),
                )
            else:
                changed.append(event)
        if changed:
            admonitions.append(_changed_admonition(version, changed))
    return admonitions


def _object_map(package: Module) -> dict[str, Object]:
    objects: dict[str, Object] = {package.path: package}

    def collect(obj: Object) -> None:
        for member in obj.members.values():
            # Aliases share their target's docstring. Mutating one would incorrectly
            # add its history to every other path exposing that target.
            if member.is_alias:
                continue
            member = cast("Object", member)
            objects[member.path] = member
            collect(member)

    collect(package)
    return objects


def _nearest_parent(path: str, objects: dict[str, Object]) -> Object | None:
    parent_path = path.rpartition(".")[0]
    while parent_path:
        if parent := objects.get(parent_path):
            return parent
        parent_path = parent_path.rpartition(".")[0]
    return None


class ApiDiffExtension(Extension):
    """Inject API-history admonitions into docstrings.

    Parameters:
        path: Path to the consolidated API-diff JSON file.
    """

    def __init__(self, path: str | Path = ".apidiff/diff.json") -> None:
        self.path = Path(path)
        self._data: dict[str, Any] | None = None
        self._pending: dict[int, dict[str, Any]] = {}

    def _load_data(self) -> dict[str, Any]:
        if self._data is not None:
            return self._data
        if not self.path.exists():
            logger.debug("API-diff history not found at %s", self.path)
            return {"packages": {}}
        try:
            data = json.loads(self.path.read_text(encoding="utf8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Could not read API-diff history {self.path}: {error}") from error
        if not isinstance(data, dict) or data.get("schema_version") != _API_DIFF_SCHEMA_VERSION:
            raise ValueError(f"Unsupported API-diff history schema in {self.path}")
        if not isinstance(data.get("packages"), dict):
            raise TypeError(f"Invalid API-diff history in {self.path}")
        self._data = data
        return data

    def on_package(self, *, pkg: Module, **kwargs: Any) -> None:  # noqa: ARG002
        """Select history for the package once it has been loaded."""
        history = self._load_data()["packages"].get(pkg.path)
        if history is not None:
            self._pending[id(pkg)] = history

    def on_module(self, *, mod: Module, **kwargs: Any) -> None:  # noqa: ARG002
        """Inject history after all package-level extension hooks have run."""
        history = self._pending.pop(id(mod), None)
        if history is None:
            return

        objects = _object_map(mod)
        object_histories = history.get("objects", {})

        for path, object_history in object_histories.items():
            if not object_history.get("exists", True):
                continue
            obj = objects.get(path)
            if obj is None:
                continue
            for kind, title, text in _object_admonitions(object_history.get("events", [])):
                _append_admonition(obj, kind=kind, title=title, text=text)

        removed: dict[tuple[str, str], list[str]] = {}
        for path, object_history in object_histories.items():
            if object_history.get("exists", True) or not (version := object_history.get("removed")):
                continue
            if parent := _nearest_parent(path, objects):
                removed.setdefault((parent.path, version), []).append(path)

        version_order = {version: index for index, version in enumerate(history.get("versions", []))}
        for parent_path, version in sorted(
            removed,
            key=lambda item: (version_order.get(item[1], len(version_order)), item),
        ):
            paths = removed[(parent_path, version)]
            text = "\n".join(f"- `{path}`" for path in sorted(paths))
            _append_admonition(
                objects[parent_path],
                kind="danger",
                title=f"Removed in version {version}",
                text=text,
            )
