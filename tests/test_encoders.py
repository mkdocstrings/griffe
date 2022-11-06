"""Tests for the `encoders` module."""

import pytest

from griffe.dataclasses import Function, Module, Object
from griffe.loader import GriffeLoader


def test_minimal_data_is_enough():
    """Test serialization and de-serialization.

    This is an end-to-end test that asserts
    we can load back a serialized tree and
    infer as much data as within the original tree.
    """
    loader = GriffeLoader()
    module = loader.load_module("griffe")
    minimal = module.as_json(full=False)
    full = module.as_json(full=True)
    reloaded = Module.from_json(minimal)
    assert reloaded.as_json(full=False) == minimal
    assert reloaded.as_json(full=True) == full

    # also works (but will result in a different type hint)
    assert Object.from_json(minimal)

    # Won't work if the JSON doesn't represent the type requested.
    with pytest.raises(TypeError) as err:
        Function.from_json(minimal)
    assert "provided JSON object is not of type" in str(err.value)  # noqa: WPS441
