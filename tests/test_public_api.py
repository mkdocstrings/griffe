"""Tests for public API handling."""

from griffe import temporary_visited_module


def test_not_detecting_imported_objects_as_public() -> None:
    """Imported objects not listed in `__all__` must not be considered public."""
    with temporary_visited_module("from abc import ABC\ndef func(): ...") as module:
        assert not module["ABC"].is_public
        assert module["func"].is_public  # control case


def test_detecting_dunder_attributes_as_public() -> None:
    """Dunder attributes (methods, etc.) must be considered public."""
    with temporary_visited_module(
        """
        def __getattr__(name): ...
        class A:
            def __init__(self): ...
        """,
    ) as module:
        assert module["__getattr__"].is_public
        assert module["A.__init__"].is_public
