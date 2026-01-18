"""Tests for our own API exposition."""

from __future__ import annotations

from collections import defaultdict
from fnmatch import fnmatch
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING

import pytest
from mkdocstrings import Inventory

import griffe
import griffecli

if TYPE_CHECKING:
    from collections.abc import Iterator


def _load_module(module: ModuleType) -> griffe.GriffeLoader:
    loader = griffe.GriffeLoader(
        extensions=griffe.load_extensions(
            "griffe_inherited_docstrings",
            "unpack_typeddict",
        ),
    )
    loader.load(module.__name__)
    loader.resolve_aliases()
    return loader


def _get_internal_api(module: ModuleType, loader: griffe.GriffeLoader | None = None) -> griffe.Module:
    if loader is None:
        loader = _load_module(module)
    return loader.modules_collection[module.__name__ + "._internal"]


def _get_public_api(module: ModuleType, loader: griffe.GriffeLoader | None = None) -> griffe.Module:
    if loader is None:
        loader = _load_module(module)
    return loader.modules_collection[module.__name__]


def _yield_public_objects(
    obj: griffe.Module | griffe.Class,
    *,
    modules: bool = False,
    modulelevel: bool = True,
    inherited: bool = False,
    special: bool = False,
) -> Iterator[griffe.Object | griffe.Alias]:
    for member in obj.all_members.values() if inherited else obj.members.values():
        try:
            if member.is_module:
                if member.is_alias:
                    continue
                if member.is_public:
                    if modules:
                        yield member
                    yield from _yield_public_objects(
                        member,  # type: ignore[arg-type]
                        modules=modules,
                        modulelevel=modulelevel,
                        inherited=inherited,
                        special=special,
                    )
            elif member.is_public and (special or not member.is_special):
                yield member
            if member.is_class and not modulelevel:
                yield from _yield_public_objects(
                    member,  # type: ignore[arg-type]
                    modules=modules,
                    modulelevel=False,
                    inherited=inherited,
                    special=special,
                )
        except (griffe.AliasResolutionError, griffe.CyclicAliasError):
            continue


def _get_modulelevel_internal_objects(tested_module: ModuleType) -> list[griffe.Object | griffe.Alias]:
    return list(_yield_public_objects(_get_internal_api(tested_module), modulelevel=True))


def _get_public_objects(tested_module: ModuleType) -> list[griffe.Object | griffe.Alias]:
    return list(_yield_public_objects(_get_public_api(tested_module), modulelevel=False, inherited=True, special=True))


@pytest.fixture(name="inventory", scope="module")
def _fixture_inventory() -> Inventory:
    inventory_file = Path(__file__).parent.parent / "site" / "objects.inv"
    if not inventory_file.exists():
        pytest.skip("The objects inventory is not available.")  # ty: ignore[call-non-callable]
    with inventory_file.open("rb") as file:
        return Inventory.parse_sphinx(file)


def test_alias_proxies() -> None:
    """The Alias class has all the necessary methods and properties."""
    internal_api = _get_internal_api(griffe)
    alias_members = set(internal_api["models.Alias"].all_members.keys())
    for cls in (
        internal_api["models.Module"],
        internal_api["models.Class"],
        internal_api["models.Function"],
        internal_api["models.Attribute"],
    ):
        for name in cls.all_members:
            if not name.startswith("_") or name.startswith("__"):
                assert name in alias_members


@pytest.mark.parametrize("tested_module", [griffe, griffecli])
def test_exposed_objects(tested_module: ModuleType) -> None:
    """All public objects in the internal API are exposed under `griffe`."""
    modulelevel_internal_objects = _get_modulelevel_internal_objects(tested_module)
    not_exposed = [
        obj.path
        for obj in modulelevel_internal_objects
        if obj.name not in tested_module.__all__ or not hasattr(tested_module, obj.name)
    ]
    assert not not_exposed, "Objects not exposed:\n" + "\n".join(sorted(not_exposed))


@pytest.mark.parametrize("tested_module", [griffe, griffecli])
def test_unique_names(tested_module: ModuleType) -> None:
    """All internal objects have unique names."""
    modulelevel_internal_objects = _get_modulelevel_internal_objects(tested_module)
    names_to_paths = defaultdict(list)
    for obj in modulelevel_internal_objects:
        names_to_paths[obj.name].append(obj.path)
    non_unique = [paths for paths in names_to_paths.values() if len(paths) > 1]
    assert not non_unique, "Non-unique names:\n" + "\n".join(str(paths) for paths in non_unique)


@pytest.mark.parametrize("tested_module", [griffe, griffecli])
def test_single_locations(tested_module: ModuleType) -> None:
    """All objects have a single public location."""

    def _public_path(obj: griffe.Object | griffe.Alias) -> bool:
        return obj.is_public and (obj.parent is None or _public_path(obj.parent))

    public_api = _get_public_api(tested_module)
    multiple_locations = {}
    for obj_name in tested_module.__all__:
        obj = public_api[obj_name]
        if obj.aliases and (
            public_aliases := [path for path, alias in obj.aliases.items() if path != obj.path and _public_path(alias)]
        ):
            multiple_locations[obj.path] = public_aliases
    assert not multiple_locations, "Multiple public locations:\n" + "\n".join(
        f"{path}: {aliases}" for path, aliases in multiple_locations.items()
    )


def test_api_matches_inventory(inventory: Inventory, public_objects: list[griffe.Object | griffe.Alias]) -> None:
    """All public objects are added to the inventory."""
    ignore_names = {"__getattr__", "__init__", "__repr__", "__str__", "__post_init__"}
    ignore_paths = {"griffe.DataclassesExtension.*", "griffe.UnpackTypedDictExtension.*"}
    not_in_inventory = [
        f"{obj.relative_filepath}:{obj.lineno}: {obj.path}"
        for obj in public_objects
        if (
            obj.name not in ignore_names
            and not any(fnmatch(obj.path, pat) for pat in ignore_paths)
            and obj.path not in inventory
        )
    ]
    msg = "Objects not in the inventory (try running `make run mkdocs build`):\n{paths}"
    assert not not_in_inventory, msg.format(paths="\n".join(sorted(not_in_inventory)))


@pytest.mark.parametrize("tested_module", [griffe, griffecli])
def test_inventory_matches_api(
    inventory: Inventory,
    public_objects: list[griffe.Object | griffe.Alias],
    tested_module: ModuleType,
) -> None:
    """The inventory doesn't contain any additional Python object."""
    loader = _load_module(tested_module)
    public_api = _get_public_api(tested_module, loader=loader)
    public_objects = _get_public_objects(public_api)
    not_in_api = []
    public_api_paths = {obj.path for obj in public_objects}
    public_api_paths.add(tested_module.__name__)
    for item in inventory.values():
        if item.domain == "py" and "(" not in item.name:
            obj = loader.modules_collection[item.name]
            if obj.path not in public_api_paths and not any(path in public_api_paths for path in obj.aliases):
                not_in_api.append(item.name)
    msg = "Inventory objects not in public API (try running `make run mkdocs build`):\n{paths}"
    assert not not_in_api, msg.format(paths="\n".join(sorted(not_in_api)))


@pytest.mark.parametrize("tested_module", [griffe, griffecli])
def test_no_module_docstrings_in_internal_api(tested_module: ModuleType) -> None:
    """No module docstrings should be written in our internal API.

    The reasoning is that docstrings are addressed to users of the public API,
    but internal modules are not exposed to users, so they should not have docstrings.
    """

    internal_api = _get_internal_api(tested_module)

    def _modules(obj: griffe.Module) -> Iterator[griffe.Module]:
        for member in obj.modules.values():
            yield member
            yield from _modules(member)

    for obj in _modules(internal_api):
        assert not obj.docstring
