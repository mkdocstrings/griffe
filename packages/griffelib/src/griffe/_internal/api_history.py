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
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from griffe._internal.diff import find_changes
from griffe._internal.enumerations import ChangeKind
from griffe._internal.models import Alias, Object, Parameter

if TYPE_CHECKING:
    from collections.abc import Iterable

    from griffe._internal.diff import Change


_API_DIFF_SCHEMA_VERSION = 1
"""The version of the API-diff JSON schema."""


def _json_value(value: Any) -> Any:
    """Return a compact, JSON-compatible representation of a change value."""
    if isinstance(value, Parameter):
        return {
            "type": "parameter",
            "name": value.name,
            "annotation": None if value.annotation is None else str(value.annotation),
            "kind": None if value.kind is None else value.kind.value,
            "default": None if value.default is None else str(value.default),
            "required": value.required,
        }
    if isinstance(value, (Object, Alias)):
        return {
            "type": "object",
            "path": value.path,
            "kind": "alias" if value.is_alias else value.kind.value,
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_json_value(item) for item in value), key=str)
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return str(value)


def _display_value(value: Any) -> str:
    if isinstance(value, dict):
        if value.get("type") == "parameter":
            return str(value["name"])
        if value.get("type") == "object":
            return str(value["path"])
    if isinstance(value, list):
        return ", ".join(_display_value(item) for item in value)
    return str(value)


def _parameter_change_summary(change: Change, old_value: Any, new_value: Any) -> str | None:
    parameter = new_value if isinstance(new_value, dict) else old_value
    if not isinstance(parameter, dict) or parameter.get("type") != "parameter":
        return None

    name = parameter["name"]
    if change.kind is ChangeKind.PARAMETER_ADDED:
        if parameter["required"]:
            return f"Required parameter `{name}` was added."
        return f"Parameter `{name}` was added with default `{parameter['default']}`."
    if change.kind is ChangeKind.PARAMETER_REMOVED:
        return f"Parameter `{name}` was removed."
    if change.kind is ChangeKind.PARAMETER_MOVED:
        return f"Parameter `{name}` moved ({change.details})."

    fields = {
        ChangeKind.PARAMETER_CHANGED_DEFAULT: ("default", "default"),
        ChangeKind.PARAMETER_CHANGED_KIND: ("kind", "kind"),
        ChangeKind.PARAMETER_CHANGED_TYPE: ("annotation", "type"),
    }
    if change.kind in fields and isinstance(old_value, dict) and isinstance(new_value, dict):
        field, label = fields[change.kind]
        old = old_value[field]
        new = new_value[field]
        if field == "default":
            old = "required" if old is None else old
            new = "required" if new is None else new
        elif field == "annotation":
            old = "no annotation" if old is None else old
            new = "no annotation" if new is None else new
        return f"Parameter `{name}` {label} changed from `{old}` to `{new}`."
    return None


def _change_summary(change: Change, old_value: Any, new_value: Any) -> str:
    if summary := _parameter_change_summary(change, old_value, new_value):
        return summary
    if old_value is not None and new_value is not None:
        return f"{change.kind.value}: `{_display_value(old_value)}` → `{_display_value(new_value)}`."
    return f"{change.kind.value}."


def _serialize_change(change: Change) -> dict[str, Any]:
    old_value = _json_value(change.old_value)
    new_value = _json_value(change.new_value)
    data: dict[str, Any] = {
        "kind": change.kind.name.lower(),
        "object_path": change.obj.path,
        "flags": sorted(flag.value for flag in change.flags),
        "old_value": old_value,
        "new_value": new_value,
        "summary": _change_summary(change, old_value, new_value),
    }
    if change.details:
        data["details"] = change.details
    return data


def _atomic_diff(
    package: str,
    old_version: str,
    new_version: str,
    changes: Iterable[Change],
) -> dict[str, Any]:
    return {
        "schema_version": _API_DIFF_SCHEMA_VERSION,
        "package": package,
        "old_version": old_version,
        "new_version": new_version,
        "changes": [_serialize_change(change) for change in changes],
    }


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(data, indent=2, sort_keys=True)}\n", encoding="utf8")


def _atomic_filename(package: str, old_version: str, new_version: str) -> str:
    safe = "._-"
    return f"{quote(package, safe=safe)}--{quote(old_version, safe=safe)}--{quote(new_version, safe=safe)}.json"


def _read_atomic_diffs(directory: Path) -> list[dict[str, Any]]:
    records = []
    atomic_directory = directory / "atomic"
    if not atomic_directory.exists():
        return records
    for path in sorted(atomic_directory.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Could not read atomic API diff {path}: {error}") from error
        required = {"package", "old_version", "new_version", "changes"}
        if not isinstance(record, dict) or not required <= record.keys():
            raise ValueError(f"Invalid atomic API diff in {path}")
        if record.get("schema_version") != _API_DIFF_SCHEMA_VERSION:
            raise ValueError(f"Unsupported API diff schema in {path}")
        records.append(record)
    return records


def _ordered_diffs(package: str, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order a package's atomic diffs, rejecting ambiguous histories."""
    outgoing: dict[str, dict[str, Any]] = {}
    incoming: dict[str, dict[str, Any]] = {}
    for record in records:
        old_version = record["old_version"]
        new_version = record["new_version"]
        if old_version in outgoing:
            raise ValueError(f"API history for {package!r} forks at version {old_version!r}")
        if new_version in incoming:
            raise ValueError(f"API history for {package!r} merges at version {new_version!r}")
        outgoing[old_version] = record
        incoming[new_version] = record

    roots = outgoing.keys() - incoming.keys()
    if len(roots) != 1:
        raise ValueError(f"API history for {package!r} is not a single linear chain")

    ordered = []
    version = next(iter(roots))
    seen_versions = set()
    while version in outgoing:
        if version in seen_versions:
            raise ValueError(f"API history for {package!r} contains a cycle")
        seen_versions.add(version)
        record = outgoing[version]
        ordered.append(record)
        version = record["new_version"]

    if len(ordered) != len(records):
        raise ValueError(f"API history for {package!r} is disconnected")
    return ordered


def _new_object_history() -> dict[str, Any]:
    return {
        "added": None,
        "deprecated": None,
        "removed": None,
        "exists": True,
        "events": [],
    }


def _apply_change(objects: dict[str, dict[str, Any]], change: dict[str, Any], record: dict[str, Any]) -> None:
    object_path = change["object_path"]
    history = objects.setdefault(object_path, _new_object_history())
    event = dict(change)
    event["from_version"] = record["old_version"]
    event["version"] = record["new_version"]
    history["events"].append(event)

    kind = change["kind"]
    version = record["new_version"]
    if kind == ChangeKind.OBJECT_ADDED.name.lower():
        history["added"] = version
        history["removed"] = None
        history["exists"] = True
    elif kind == ChangeKind.OBJECT_REMOVED.name.lower():
        history["removed"] = version
        history["exists"] = False
    elif kind == ChangeKind.OBJECT_DEPRECATED.name.lower():
        message = change["new_value"] if isinstance(change["new_value"], str) else None
        history["deprecated"] = {"version": version, "message": message}
    elif kind == ChangeKind.OBJECT_UNDEPRECATED.name.lower():
        history["deprecated"] = None
    elif kind == ChangeKind.OBJECT_CHANGED_DEPRECATION.name.lower():
        deprecated = history["deprecated"] or {"version": version, "message": None}
        deprecated["message"] = change["new_value"] if isinstance(change["new_value"], str) else None
        history["deprecated"] = deprecated


def _consolidated_diff(records: list[dict[str, Any]]) -> dict[str, Any]:
    records_by_package: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        records_by_package.setdefault(record["package"], []).append(record)

    packages: dict[str, Any] = {}
    for package, package_records in sorted(records_by_package.items()):
        ordered = _ordered_diffs(package, package_records)
        objects: dict[str, dict[str, Any]] = {}
        for record in ordered:
            for change in record["changes"]:
                _apply_change(objects, change, record)
        packages[package] = {
            "latest_version": ordered[-1]["new_version"],
            "versions": [ordered[0]["old_version"], *(record["new_version"] for record in ordered)],
            "objects": objects,
        }

    return {
        "schema_version": _API_DIFF_SCHEMA_VERSION,
        "packages": packages,
    }


def consolidate_api_diffs(directory: str | Path = ".apidiff") -> Path:
    """Consolidate atomic API diffs into a single history file.

    Parameters:
        directory: Directory containing the `atomic` subdirectory and receiving `diff.json`.

    Returns:
        The path of the consolidated history file.

    Raises:
        ValueError: If atomic diffs do not form a linear history for each package.
    """
    directory = Path(directory)
    output_path = directory / "diff.json"
    _write_json(output_path, _consolidated_diff(_read_atomic_diffs(directory)))
    return output_path


def write_api_diff(
    old_obj: Object | Alias,
    new_obj: Object | Alias,
    *,
    old_version: str,
    new_version: str,
    directory: str | Path = ".apidiff",
) -> tuple[Path, Path]:
    """Detect, record, and consolidate changes between two API versions.

    Parameters:
        old_obj: The old version of an API object.
        new_obj: The new version of the same API object.
        old_version: Version label for `old_obj`.
        new_version: Version label for `new_obj`.
        directory: Directory in which to write API-diff data.

    Returns:
        The paths of the atomic diff and consolidated history files.

    Raises:
        ValueError: If the objects have different paths or the resulting history is ambiguous.
    """
    if old_obj.path != new_obj.path:
        raise ValueError(
            f"Cannot record API history for objects with different paths: {old_obj.path!r}, {new_obj.path!r}",
        )
    if old_version == new_version:
        raise ValueError("Old and new API versions must be different")

    directory = Path(directory)
    atomic_path = directory / "atomic" / _atomic_filename(new_obj.path, old_version, new_version)
    atomic_diff = _atomic_diff(new_obj.path, old_version, new_version, find_changes(old_obj, new_obj))

    # Validate the prospective complete history before modifying either file.
    existing = [
        record
        for record in _read_atomic_diffs(directory)
        if not (
            record["package"] == new_obj.path
            and record["old_version"] == old_version
            and record["new_version"] == new_version
        )
    ]
    consolidated_diff = _consolidated_diff([*existing, atomic_diff])

    _write_json(atomic_path, atomic_diff)
    history_path = directory / "diff.json"
    _write_json(history_path, consolidated_diff)
    return atomic_path, history_path
