"""Tests for the `encoders` module."""

import json

import pytest

from griffe.dataclasses import Function, Module, Object
from griffe.encoders import JSONEncoder, json_decoder
from griffe.loader import GriffeLoader


def test_minimal_data_is_enough():
    """Test serialization and de-serialization.

    This is an end-to-end test that asserts
    we can load back a serialized tree and
    infer as much data as within the original tree.
    """
    loader = GriffeLoader()
    module = loader.load_module("griffe")
    minimal = json.dumps(module, cls=JSONEncoder, full=False, indent=2)
    full = json.dumps(module, cls=JSONEncoder, full=True, indent=2)
    reloaded = json.loads(minimal, object_hook=json_decoder)
    assert json.dumps(reloaded, cls=JSONEncoder, full=False, indent=2) == minimal
    assert json.dumps(reloaded, cls=JSONEncoder, full=True, indent=2) == full


def test_object_as_from_json():
    """Test serialization and de-serialization convenience methods on Object."""
    loader = GriffeLoader()
    module = loader.load_module("griffe")
    minimal = module.as_json(full=False, indent=2)
    assert minimal == json.dumps(module, cls=JSONEncoder, full=False, indent=2)
    reloaded = Module.from_json(minimal)
    # recasting to json for sake of comparison easier than as_dict()
    assert module.as_json() == reloaded.as_json()

    # also works (but will result in a different type hint)
    assert Object.from_json(minimal)

    # Won't work if the JSON doesn't represent the type requested.
    with pytest.raises(TypeError) as err:
        Function.from_json(minimal)
    assert "provided JSON object is not of type" in str(err.value)  # noqa: WPS441
