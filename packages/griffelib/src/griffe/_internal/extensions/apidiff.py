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
from griffe._internal.exceptions import AliasResolutionError, CyclicAliasError
from griffe._internal.extensions.base import Extension
from griffe._internal.logger import logger
from griffe._internal.models import Docstring

if TYPE_CHECKING:
    from griffe._internal.models import Alias, Module, Object


_OBJECT_ADDED = ChangeKind.OBJECT_ADDED.name.lower()
_OBJECT_REMOVED = ChangeKind.OBJECT_REMOVED.name.lower()
_OBJECT_DEPRECATED = ChangeKind.OBJECT_DEPRECATED.name.lower()
_OBJECT_UNDEPRECATED = ChangeKind.OBJECT_UNDEPRECATED.name.lower()
_PAIR_SIZE = 2


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


def _join_phrases(phrases: list[str]) -> str:
    if len(phrases) < _PAIR_SIZE:
        return "".join(phrases)
    if len(phrases) == _PAIR_SIZE:
        return " and ".join(phrases)
    return f"{', '.join(phrases[:-1])}, and {phrases[-1]}"


def _has_location_details(history: dict[str, Any]) -> bool:
    locations = history.get("public_locations", [])
    public_paths = {location["path"] for location in locations}
    return len(public_paths) > 1 or any(location.get("is_alias", False) for location in locations)


def _added_body(history: dict[str, Any]) -> str:
    if not _has_location_details(history):
        return ""
    phrases = []
    for location in history.get("public_locations", []):
        version = location.get("added_in")
        if version is None:
            phrases.append(f"`{location['path']}` before the recorded history")
        else:
            phrases.append(f"`{location['path']}` in version {version}")
    return f"`{history['name']}` was publicly exposed as {_join_phrases(phrases)}."


def _removed_body(history: dict[str, Any]) -> str:
    if not _has_location_details(history):
        return ""
    phrases = [
        f"`{location['path']}` in version {location['removed_in']}"
        for location in history.get("public_locations", [])
        if location.get("removed_in") is not None
    ]
    if not phrases:
        return ""
    return f"`{history['name']}` was removed from {_join_phrases(phrases)}."


def _object_admonitions(history: dict[str, Any]) -> list[tuple[str, str, str]]:
    events = history.get("events", [])
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
                admonitions.append(("tip", f"Added in version {version}", _added_body(history)))
            elif event["kind"] == _OBJECT_REMOVED:
                admonitions.append(("danger", f"Removed in version {version}", _removed_body(history)))
            elif event["kind"] == _OBJECT_DEPRECATED:
                message = event["new_value"] if isinstance(event["new_value"], str) else None
                admonitions.append(("warning", f"Deprecated in version {version}", message or ""))
            elif event["kind"] == _OBJECT_UNDEPRECATED:
                admonitions.append(("info", f"No longer deprecated in version {version}", ""))
            else:
                changed.append(event)
        if changed:
            admonitions.append(_changed_admonition(version, changed))
    return admonitions


def _target(member: Object | Alias) -> Object | None:
    try:
        return cast("Alias", member).final_target if member.is_alias else cast("Object", member)
    except (AliasResolutionError, CyclicAliasError):
        return None


def _object_maps(package: Module) -> tuple[dict[str, Object], set[int]]:
    """Map public and canonical paths to final targets, including private targets."""
    objects: dict[str, Object] = {package.path: package}
    public_targets: set[int] = {id(package)}
    visited: set[int] = set()

    def collect_all(obj: Object) -> None:
        if id(obj) in visited:
            return
        visited.add(id(obj))
        objects[obj.canonical_path] = obj
        for member in obj.members.values():
            target = _target(member)
            if target is None:
                continue
            objects[member.path] = target
            objects[target.canonical_path] = target
            if not member.is_alias and (target.is_module or target.is_class):
                collect_all(target)

    def collect_public(parent: Object | Alias, ancestors: frozenset[str]) -> None:
        try:
            members = parent.members
        except (AliasResolutionError, CyclicAliasError):
            return
        for member in members.values():
            if member.name == "__all__" or not member.is_public:
                continue
            target = _target(member)
            if target is None:
                continue
            objects[member.path] = target
            objects[target.canonical_path] = target
            public_targets.add(id(target))
            if (target.is_module or target.is_class) and target.canonical_path not in ancestors:
                collect_public(member, ancestors | {target.canonical_path})

    collect_all(package)
    collect_public(package, frozenset({package.canonical_path}))
    return objects, public_targets


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
        packages = data.get("packages")
        if not isinstance(packages, dict) or any(
            not isinstance(history, dict)
            or not isinstance(history.get("symbols"), dict)
            or not isinstance(history.get("paths"), dict)
            for history in packages.values()
        ):
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

        objects, public_targets = _object_maps(mod)
        symbols = history.get("symbols", {})
        paths = history.get("paths", {})
        symbol_objects: dict[str, Object] = {}
        public_symbols: set[str] = set()
        for path, obj in objects.items():
            for symbol_id in paths.get(path, []):
                symbol_objects.setdefault(symbol_id, obj)
                if id(obj) in public_targets:
                    public_symbols.add(symbol_id)

        for symbol_id, symbol_history in symbols.items():
            if obj := symbol_objects.get(symbol_id):
                for kind, title, text in _object_admonitions(symbol_history):
                    _append_admonition(obj, kind=kind, title=title, text=text)

        removed: dict[tuple[str, str], list[str]] = {}
        for symbol_id, symbol_history in symbols.items():
            if symbol_history.get("exists", True) or symbol_id in public_symbols:
                continue
            version = symbol_history.get("removed")
            if not version:
                continue
            removed_paths = [
                location["path"]
                for location in symbol_history.get("public_locations", [])
                if location.get("removed_in") == version
            ]
            for path in removed_paths:
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
