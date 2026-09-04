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
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import quote

from griffe._internal.diff import Change, _object_changes
from griffe._internal.enumerations import ChangeFlag, ChangeKind
from griffe._internal.exceptions import AliasResolutionError, CyclicAliasError
from griffe._internal.logger import logger
from griffe._internal.models import Alias, Object, Parameter

if TYPE_CHECKING:
    from collections.abc import Iterable


_API_DIFF_SCHEMA_VERSION = 1
"""The version of the API-diff JSON schema."""


@dataclass(frozen=True, slots=True)
class _PublicBinding:
    """A public path and the concrete object to which it resolves."""

    public_path: str
    canonical_path: str
    name: str
    kind: str
    deprecated: str | bool | None
    obj: Object | Alias

    def as_dict(self) -> dict[str, Any]:
        return {
            "public_path": self.public_path,
            "canonical_path": self.canonical_path,
            "name": self.name,
            "kind": self.kind,
            "deprecated": self.deprecated,
        }


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


def _serialize_change(
    change: Change,
    *,
    binding: int,
    old_binding: _PublicBinding | None,
    new_binding: _PublicBinding | None,
) -> dict[str, Any]:
    old_value = _json_value(change.old_value)
    new_value = _json_value(change.new_value)
    current_binding = new_binding or old_binding
    if current_binding is None:
        raise ValueError("A change must belong to an old or new public binding")
    data: dict[str, Any] = {
        "kind": change.kind.name.lower(),
        "binding": binding,
        "object_path": current_binding.public_path,
        "canonical_path": current_binding.canonical_path,
        "old_public_path": None if old_binding is None else old_binding.public_path,
        "new_public_path": None if new_binding is None else new_binding.public_path,
        "old_canonical_path": None if old_binding is None else old_binding.canonical_path,
        "new_canonical_path": None if new_binding is None else new_binding.canonical_path,
        "flags": sorted(flag.value for flag in change.flags),
        "old_value": old_value,
        "new_value": new_value,
        "summary": _change_summary(change, old_value, new_value),
    }
    if change.details:
        data["details"] = change.details
    return data


def _effective_deprecation(obj: Object | Alias, target: Object) -> str | bool | None:
    if obj.is_alias and obj.deprecated is not None:
        return obj.deprecated
    return target.deprecated


def _public_bindings(root: Object | Alias) -> dict[str, _PublicBinding]:
    """Collect every name reachable through public modules and classes."""
    bindings: dict[str, _PublicBinding] = {}

    def collect(parent: Object | Alias, ancestors: frozenset[str]) -> None:
        try:
            members = parent.members
        except (AliasResolutionError, CyclicAliasError):
            logger.debug("API history: skip members of unresolved alias %s", parent.path)
            return

        for member in members.values():
            if member.name == "__all__" or not member.is_public:
                continue
            try:
                target = cast("Alias", member).final_target if member.is_alias else cast("Object", member)
            except (AliasResolutionError, CyclicAliasError):
                logger.debug("API history: skip unresolved public alias %s", member.path)
                continue

            binding = _PublicBinding(
                public_path=member.path,
                canonical_path=target.canonical_path,
                name=target.name,
                kind=target.kind.value,
                deprecated=_effective_deprecation(member, target),
                obj=member,
            )
            bindings[binding.public_path] = binding

            if (target.is_module or target.is_class) and target.canonical_path not in ancestors:
                collect(member, ancestors | {target.canonical_path})

    root_target = cast("Alias", root).final_target if root.is_alias else cast("Object", root)
    collect(root, frozenset({root_target.canonical_path}))

    # API histories assume one public location per logical object. Older
    # releases can predate that convention, so prefer their shortest public
    # path rather than recording the same target and changes more than once.
    preferred: dict[str, _PublicBinding] = {}
    for binding in sorted(bindings.values(), key=lambda item: (item.public_path.count("."), item.public_path)):
        if previous := preferred.get(binding.canonical_path):
            logger.debug(
                "API history: %s is also public as %s; use %s",
                binding.canonical_path,
                binding.public_path,
                previous.public_path,
            )
        else:
            preferred[binding.canonical_path] = binding
    return {binding.public_path: binding for binding in preferred.values()}


def _group_paths(bindings: dict[str, _PublicBinding], attribute: str) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for path, binding in bindings.items():
        grouped[getattr(binding, attribute)].append(path)
    return grouped


def _match_bindings(
    old_bindings: dict[str, _PublicBinding],
    new_bindings: dict[str, _PublicBinding],
) -> list[tuple[_PublicBinding | None, _PublicBinding | None]]:
    """Match logical public symbols across two snapshots."""
    matched: list[tuple[_PublicBinding, _PublicBinding]] = []
    unmatched_old = set(old_bindings)
    unmatched_new = set(new_bindings)

    def match(old_path: str, new_path: str) -> None:
        matched.append((old_bindings[old_path], new_bindings[new_path]))
        unmatched_old.remove(old_path)
        unmatched_new.remove(new_path)

    # A stable public path is the strongest public-API identity, even when a
    # private implementation target moved.
    for path in sorted(unmatched_old & unmatched_new):
        match(path, path)

    # A stable target identifies a public name that moved to another namespace.
    old_by_canonical = _group_paths(old_bindings, "canonical_path")
    new_by_canonical = _group_paths(new_bindings, "canonical_path")
    for canonical_path in sorted(old_by_canonical.keys() & new_by_canonical.keys()):
        old_paths = [path for path in old_by_canonical[canonical_path] if path in unmatched_old]
        new_paths = [path for path in new_by_canonical[canonical_path] if path in unmatched_new]
        if len(old_paths) == len(new_paths) == 1:
            match(old_paths[0], new_paths[0])

    # Once a parent was matched, equally named children can be matched without
    # requiring their names to be globally unique.
    while True:
        parent_paths = {old.public_path: new.public_path for old, new in matched}
        found: list[tuple[str, str]] = []
        for old_path in sorted(unmatched_old):
            old_parent, _, old_name = old_path.rpartition(".")
            new_parent = parent_paths.get(old_parent)
            if new_parent is None:
                continue
            new_path = f"{new_parent}.{old_name}"
            if new_path in unmatched_new and old_bindings[old_path].kind == new_bindings[new_path].kind:
                found.append((old_path, new_path))
        if not found:
            break
        for old_path, new_path in found:
            if old_path in unmatched_old and new_path in unmatched_new:
                match(old_path, new_path)

    transitions: list[tuple[_PublicBinding | None, _PublicBinding | None]] = [*matched]
    transitions.extend((old_bindings[path], None) for path in unmatched_old)
    transitions.extend((None, new_bindings[path]) for path in unmatched_new)

    def sort_key(pair: tuple[_PublicBinding | None, _PublicBinding | None]) -> tuple[str, str]:
        current = pair[1] or pair[0]
        if current is None:
            raise ValueError("A transition must contain an old or new public binding")
        return current.public_path, "" if pair[0] is None else pair[0].public_path

    return sorted(transitions, key=sort_key)


def _transition_changes(
    old_binding: _PublicBinding | None,
    new_binding: _PublicBinding | None,
) -> Iterable[Change]:
    if old_binding is None:
        if new_binding is None:
            raise ValueError("A transition must contain an old or new public binding")
        yield Change(kind=ChangeKind.OBJECT_ADDED, obj=new_binding.obj, new_value=new_binding.obj)
        if new_binding.deprecated:
            yield Change(
                kind=ChangeKind.OBJECT_DEPRECATED,
                obj=new_binding.obj,
                new_value=new_binding.deprecated,
                flags=frozenset({ChangeFlag.DEPRECATION}),
            )
    elif new_binding is None:
        yield Change(
            kind=ChangeKind.OBJECT_REMOVED,
            obj=old_binding.obj,
            old_value=old_binding.obj,
            flags=frozenset({ChangeFlag.BREAKING}),
        )
    else:
        yield from _object_changes(old_binding.obj, new_binding.obj)


def _atomic_diff(
    package: str,
    old_version: str,
    new_version: str,
    old_obj: Object | Alias,
    new_obj: Object | Alias,
) -> dict[str, Any]:
    transitions = _match_bindings(_public_bindings(old_obj), _public_bindings(new_obj))
    bindings = []
    changes = []
    for old_binding, new_binding in transitions:
        transition_changes = list(_transition_changes(old_binding, new_binding))
        location_changed = (
            old_binding is None
            or new_binding is None
            or old_binding.public_path != new_binding.public_path
            or old_binding.canonical_path != new_binding.canonical_path
        )
        if not location_changed and not transition_changes:
            continue
        binding_index = len(bindings)
        bindings.append(
            {
                "old": None if old_binding is None else old_binding.as_dict(),
                "new": None if new_binding is None else new_binding.as_dict(),
            },
        )
        changes.extend(
            _serialize_change(
                change,
                binding=binding_index,
                old_binding=old_binding,
                new_binding=new_binding,
            )
            for change in transition_changes
        )
    return {
        "schema_version": _API_DIFF_SCHEMA_VERSION,
        "package": package,
        "old_version": old_version,
        "new_version": new_version,
        "bindings": bindings,
        "changes": changes,
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
        required = {"package", "old_version", "new_version", "bindings", "changes"}
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


def _new_symbol_history(binding: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": binding["name"],
        "kind": binding["kind"],
        "added": None,
        "deprecated": None,
        "removed": None,
        "exists": True,
        "public_path": None,
        "canonical_path": None,
        "public_locations": [],
        "canonical_locations": [],
        "events": [],
    }


def _new_symbol_id(binding: dict[str, Any], symbols: dict[str, dict[str, Any]]) -> str:
    base = binding["canonical_path"]
    if base not in symbols:
        return base
    index = 2
    while f"{base}#{index}" in symbols:
        index += 1
    return f"{base}#{index}"


def _deprecation_state(binding: dict[str, Any], version: str | None) -> dict[str, Any] | None:
    deprecated = binding.get("deprecated")
    if not deprecated:
        return None
    return {
        "version": version,
        "message": deprecated if isinstance(deprecated, str) else None,
    }


def _open_public_location(history: dict[str, Any], binding: dict[str, Any], version: str | None) -> None:
    history["public_locations"].append(
        {
            "path": binding["public_path"],
            "added_in": version,
            "removed_in": None,
            "is_alias": binding["public_path"] != binding["canonical_path"],
        },
    )


def _close_public_location(history: dict[str, Any], path: str, version: str) -> None:
    for location in reversed(history["public_locations"]):
        if location["path"] == path and location["removed_in"] is None:
            location["removed_in"] = version
            return


def _open_canonical_location(history: dict[str, Any], path: str, version: str | None) -> None:
    history["canonical_locations"].append({"path": path, "since": version, "until": None})


def _close_canonical_location(history: dict[str, Any], path: str, version: str) -> None:
    for location in reversed(history["canonical_locations"]):
        if location["path"] == path and location["until"] is None:
            location["until"] = version
            return


def _activate_symbol(history: dict[str, Any], binding: dict[str, Any], version: str | None) -> None:
    _open_public_location(history, binding, version)
    _open_canonical_location(history, binding["canonical_path"], version)
    history["name"] = binding["name"]
    history["kind"] = binding["kind"]
    history["public_path"] = binding["public_path"]
    history["canonical_path"] = binding["canonical_path"]
    history["deprecated"] = _deprecation_state(binding, version)
    history["removed"] = None
    history["exists"] = True


def _move_symbol(
    history: dict[str, Any],
    old_binding: dict[str, Any],
    new_binding: dict[str, Any],
    version: str,
) -> None:
    if old_binding["public_path"] != new_binding["public_path"]:
        _close_public_location(history, old_binding["public_path"], version)
        _open_public_location(history, new_binding, version)
    elif history["public_locations"]:
        history["public_locations"][-1]["is_alias"] |= new_binding["public_path"] != new_binding["canonical_path"]

    if old_binding["canonical_path"] != new_binding["canonical_path"]:
        _close_canonical_location(history, old_binding["canonical_path"], version)
        _open_canonical_location(history, new_binding["canonical_path"], version)

    history["name"] = new_binding["name"]
    history["kind"] = new_binding["kind"]
    history["public_path"] = new_binding["public_path"]
    history["canonical_path"] = new_binding["canonical_path"]
    history["exists"] = True


def _remove_symbol(history: dict[str, Any], binding: dict[str, Any], version: str) -> None:
    _close_public_location(history, binding["public_path"], version)
    _close_canonical_location(history, binding["canonical_path"], version)
    history["public_path"] = None
    history["canonical_path"] = None
    history["removed"] = version
    history["exists"] = False


def _apply_event(history: dict[str, Any], change: dict[str, Any], record: dict[str, Any]) -> None:
    event = {key: value for key, value in change.items() if key != "binding"}
    event["from_version"] = record["old_version"]
    event["version"] = record["new_version"]
    history["events"].append(event)

    kind = change["kind"]
    version = record["new_version"]
    if kind == ChangeKind.OBJECT_DEPRECATED.name.lower():
        message = change["new_value"] if isinstance(change["new_value"], str) else None
        history["deprecated"] = {"version": version, "message": message}
    elif kind == ChangeKind.OBJECT_UNDEPRECATED.name.lower():
        history["deprecated"] = None
    elif kind == ChangeKind.OBJECT_CHANGED_DEPRECATION.name.lower():
        deprecated = history["deprecated"] or {"version": version, "message": None}
        deprecated["message"] = change["new_value"] if isinstance(change["new_value"], str) else None
        history["deprecated"] = deprecated


def _find_inactive_symbol(binding: dict[str, Any], symbols: dict[str, dict[str, Any]]) -> str | None:
    canonical_matches = [
        symbol_id
        for symbol_id, history in symbols.items()
        if not history["exists"]
        and history["kind"] == binding["kind"]
        and any(location["path"] == binding["canonical_path"] for location in history["canonical_locations"])
    ]
    if len(canonical_matches) == 1:
        return canonical_matches[0]
    public_matches = [
        symbol_id
        for symbol_id, history in symbols.items()
        if not history["exists"]
        and history["kind"] == binding["kind"]
        and any(location["path"] == binding["public_path"] for location in history["public_locations"])
    ]
    return public_matches[0] if len(public_matches) == 1 else None


def _binding_values(binding: dict[str, Any]) -> tuple[Any, ...]:
    fields = ("public_path", "canonical_path", "name", "kind", "deprecated")
    return tuple(binding[field] for field in fields)


def _active_symbol(
    package: str,
    version: str,
    binding: dict[str, Any],
    symbols: dict[str, dict[str, Any]],
    state: dict[str, tuple[str, dict[str, Any]]],
) -> tuple[str, dict[str, Any]]:
    active = state.get(binding["public_path"])
    if active is not None:
        symbol_id, previous_binding = active
        if _binding_values(previous_binding) != _binding_values(binding):
            raise ValueError(f"Atomic API diffs for {package!r} disagree about snapshot {version!r}")
        return symbol_id, symbols[symbol_id]

    symbol_id = _new_symbol_id(binding, symbols)
    history = symbols.setdefault(symbol_id, _new_symbol_history(binding))
    _activate_symbol(history, binding, None)
    state[binding["public_path"]] = (symbol_id, binding)
    return symbol_id, history


def _consolidate_package(package: str, ordered: list[dict[str, Any]]) -> dict[str, Any]:
    symbols: dict[str, dict[str, Any]] = {}
    state: dict[str, tuple[str, dict[str, Any]]] = {}

    for record in ordered:
        changes_by_binding: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for change in record["changes"]:
            changes_by_binding[change["binding"]].append(change)

        version = record["new_version"]
        old_state = state
        new_state = dict(state)
        for index, transition in enumerate(record["bindings"]):
            old_binding = transition["old"]
            new_binding = transition["new"]
            if old_binding is not None:
                symbol_id, history = _active_symbol(
                    package,
                    record["old_version"],
                    old_binding,
                    symbols,
                    old_state,
                )
                if (current := new_state.get(old_binding["public_path"])) is not None and current[0] == symbol_id:
                    del new_state[old_binding["public_path"]]
                if new_binding is None:
                    _remove_symbol(history, old_binding, version)
                else:
                    _move_symbol(history, old_binding, new_binding, version)
                    new_state[new_binding["public_path"]] = (symbol_id, new_binding)
            else:
                if new_binding is None:
                    raise ValueError("A transition must contain an old or new public binding")
                symbol_id = _find_inactive_symbol(new_binding, symbols) or _new_symbol_id(new_binding, symbols)
                history = symbols.setdefault(symbol_id, _new_symbol_history(new_binding))
                _activate_symbol(history, new_binding, version)
                if history["added"] is None:
                    history["added"] = version
                new_state[new_binding["public_path"]] = (symbol_id, new_binding)

            for change in changes_by_binding[index]:
                _apply_event(history, change, record)
        state = new_state

    paths: dict[str, list[str]] = defaultdict(list)
    for symbol_id, history in symbols.items():
        for location in [*history["public_locations"], *history["canonical_locations"]]:
            if symbol_id not in paths[location["path"]]:
                paths[location["path"]].append(symbol_id)

    return {
        "latest_version": ordered[-1]["new_version"],
        "versions": [ordered[0]["old_version"], *(record["new_version"] for record in ordered)],
        "symbols": dict(sorted(symbols.items())),
        "paths": {path: sorted(symbol_ids) for path, symbol_ids in sorted(paths.items())},
    }


def _consolidated_diff(records: list[dict[str, Any]]) -> dict[str, Any]:
    records_by_package: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        records_by_package.setdefault(record["package"], []).append(record)

    packages = {
        package: _consolidate_package(package, _ordered_diffs(package, package_records))
        for package, package_records in sorted(records_by_package.items())
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


def _prepare_api_diff(
    old_obj: Object | Alias,
    new_obj: Object | Alias,
    *,
    old_version: str,
    new_version: str,
    directory: Path,
) -> tuple[Path, dict[str, Any]]:
    if old_obj.path != new_obj.path:
        raise ValueError(
            f"Cannot record API history for objects with different paths: {old_obj.path!r}, {new_obj.path!r}",
        )
    if old_version == new_version:
        raise ValueError("Old and new API versions must be different")

    atomic_path = directory / "atomic" / _atomic_filename(new_obj.path, old_version, new_version)
    atomic_diff = _atomic_diff(new_obj.path, old_version, new_version, old_obj, new_obj)
    return atomic_path, atomic_diff


def write_api_diffs(
    snapshots: Iterable[tuple[str, Object | Alias]],
    *,
    directory: str | Path = ".apidiff",
) -> tuple[list[Path], Path]:
    """Detect, record, and consolidate changes between successive API snapshots.

    All atomic diffs are prepared first, then the prospective complete history is
    consolidated once and written together with the atomic files.

    Parameters:
        snapshots: Chronological `(version, object)` pairs to compare successively.
        directory: Directory in which to write API-diff data.

    Returns:
        The paths of the atomic diffs and consolidated history file.

    Raises:
        ValueError: If fewer than two snapshots are provided, their objects have
            different paths, or the resulting history is ambiguous.
    """
    directory = Path(directory)
    iterator = iter(snapshots)
    try:
        old_version, old_obj = next(iterator)
    except StopIteration:
        raise ValueError("At least two API snapshots are required") from None

    pending: list[tuple[Path, dict[str, Any]]] = []
    for new_version, new_obj in iterator:
        pending.append(
            _prepare_api_diff(
                old_obj,
                new_obj,
                old_version=old_version,
                new_version=new_version,
                directory=directory,
            ),
        )
        old_version, old_obj = new_version, new_obj

    if not pending:
        raise ValueError("At least two API snapshots are required")

    replacements = {(record["package"], record["old_version"], record["new_version"]) for _, record in pending}
    existing = [
        record
        for record in _read_atomic_diffs(directory)
        if (record["package"], record["old_version"], record["new_version"]) not in replacements
    ]
    consolidated_diff = _consolidated_diff([*existing, *(record for _, record in pending)])

    atomic_paths = []
    for atomic_path, atomic_diff in pending:
        _write_json(atomic_path, atomic_diff)
        atomic_paths.append(atomic_path)
    history_path = directory / "diff.json"
    _write_json(history_path, consolidated_diff)
    return atomic_paths, history_path


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
    atomic_paths, history_path = write_api_diffs(
        ((old_version, old_obj), (new_version, new_obj)),
        directory=directory,
    )
    return atomic_paths[0], history_path
