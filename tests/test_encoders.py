"""Tests for the `encoders` module."""

import json

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
