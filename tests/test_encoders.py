"""Tests for the `encoders` module."""

from __future__ import annotations

import json

import pytest
from jsonschema import ValidationError, validate

from griffe.dataclasses import Function, Module, Object
from griffe.loader import GriffeLoader


def test_minimal_data_is_enough() -> None:
    """Test serialization and de-serialization.

    This is an end-to-end test that asserts
    we can load back a serialized tree and
    infer as much data as within the original tree.
    """
    loader = GriffeLoader()
    module = loader.load("griffe")
    minimal = module.as_json(full=False)
    full = module.as_json(full=True)
    reloaded = Module.from_json(minimal)
    assert reloaded.as_json(full=False) == minimal
    assert reloaded.as_json(full=True) == full

    # Also works (but will result in a different type hint).
    assert Object.from_json(minimal)

    # Won't work if the JSON doesn't represent the type requested.
    with pytest.raises(TypeError, match="provided JSON object is not of type"):
        Function.from_json(minimal)


# use this function in test_json_schema to ease schema debugging
def _validate(obj: dict, schema: dict) -> None:
    if "members" in obj:
        for member in obj["members"]:
            _validate(member, schema)

    try:
        validate(obj, schema)
    except ValidationError:
        print(obj["path"])  # noqa: T201
        raise


def test_json_schema() -> None:
    """Assert that our serialized data matches our JSON schema."""
    loader = GriffeLoader()
    module = loader.load("griffe")
    loader.resolve_aliases()
    data = json.loads(module.as_json(full=True))
    with open("docs/schema.json") as f:
        schema = json.load(f)
    validate(data, schema)
