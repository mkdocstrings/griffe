"""Tests for the `encoders` module."""

from __future__ import annotations

import json
import sys

import pytest
from jsonschema import ValidationError, validate

from griffe import Function, GriffeLoader, Module, Object, temporary_visited_module


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


# YORE: EOL 3.12: Remove block.
# YORE: EOL 3.11: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python less than 3.12 does not have PEP 695 generics")
def test_encoding_pep695_generics_without_defaults() -> None:
    """Test serialization and de-serialization of PEP 695 generics without defaults.

    Defaults are only possible from Python 3.13 onwards.
    """
    with temporary_visited_module(
        """
        class Class[X: Exception]: pass
        def func[**P, T, *R](arg: T, *args: P.args, **kwargs: P.kwargs) -> tuple[*R]: pass
        type TA[T: (int, str)] = dict[str, T]
        """,
    ) as module:
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


# YORE: EOL 3.12: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 13), reason="Python less than 3.13 does not have defaults in PEP 695 generics")  # fmt: skip
def test_encoding_pep695_generics() -> None:
    """Test serialization and de-serialization of PEP 695 generics with defaults.

    Defaults are only possible from Python 3.13 onwards.
    """
    with temporary_visited_module(
        """
        class Class[X: Exception = OSError]: pass
        def func[**P, T, *R](arg: T, *args: P.args, **kwargs: P.kwargs) -> tuple[*R]: pass
        type TA[T: (int, str) = str] = dict[str, T]
        """,
    ) as module:
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
    with open("docs/schema.json") as f:  # noqa: PTH123
        schema = json.load(f)
    validate(data, schema)


# YORE: EOL 3.12: Remove block.
# YORE: EOL 3.11: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python less than 3.12 does not have PEP 695 generics")
def test_json_schema_for_pep695_generics_without_defaults() -> None:
    """Assert that serialized PEP 695 generics without defaults match our JSON schema.

    Defaults are only possible from Python 3.13 onwards.
    """
    with temporary_visited_module(
        """
        class Class[X: Exception]: pass
        def func[**P, T, *R](arg: T, *args: P.args, **kwargs: P.kwargs) -> tuple[*R]: pass
        type TA[T: (int, str)] = dict[str, T]
        """,
    ) as module:
        data = json.loads(module.as_json(full=True))
        with open("docs/schema.json") as f:  # noqa: PTH123
            schema = json.load(f)
        validate(data, schema)


# YORE: EOL 3.12: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 13), reason="Python less than 3.13 does not have defaults in PEP 695 generics")  # fmt: skip
def test_json_schema_for_pep695_generics() -> None:
    """Assert that serialized PEP 695 generics with defaults match our JSON schema.

    Defaults are only possible from Python 3.13 onwards.
    """
    with temporary_visited_module(
        """
        class Class[X: Exception = OSError]: pass
        def func[**P, T, *R](arg: T, *args: P.args, **kwargs: P.kwargs) -> tuple[*R]: pass
        type TA[T: (int, str) = str] = dict[str, T]
        """,
    ) as module:
        data = json.loads(module.as_json(full=True))
        with open("docs/schema.json") as f:  # noqa: PTH123
            schema = json.load(f)
        validate(data, schema)
