"""Tests for public API handling."""

from griffe.tests import temporary_visited_module


def test_not_detecting_imported_objects_as_public() -> None:
    """Imported objects not listed in `__all__` must not be considered public."""
    with temporary_visited_module("from abc import ABC\ndef func(): ...") as module:
        assert not module["ABC"].is_public
        assert module["func"].is_public  # control case
