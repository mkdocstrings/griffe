"""Tests for the `extensions` module."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from griffe.extensions import Extension, load_extensions
from griffe.tests import temporary_visited_module

if TYPE_CHECKING:
    import ast

    from griffe.agents.nodes import ObjectNode
    from griffe.dataclasses import Attribute, Class, Function, Module, Object


class ExtensionTest(Extension):  # noqa: D101
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D107
        super().__init__()
        self.records: list[str] = []
        self.args = args
        self.kwargs = kwargs

    def on_attribute_instance(self, *, node: ast.AST | ObjectNode, attr: Attribute) -> None:  # noqa: D102,ARG002
        self.records.append("on_attribute_instance")

    def on_attribute_node(self, *, node: ast.AST | ObjectNode) -> None:  # noqa: D102,ARG002
        self.records.append("on_attribute_node")

    def on_class_instance(self, *, node: ast.AST | ObjectNode, cls: Class) -> None:  # noqa: D102,ARG002
        self.records.append("on_class_instance")

    def on_class_members(self, *, node: ast.AST | ObjectNode, cls: Class) -> None:  # noqa: D102,ARG002
        self.records.append("on_class_members")

    def on_class_node(self, *, node: ast.AST | ObjectNode) -> None:  # noqa: D102,ARG002
        self.records.append("on_class_node")

    def on_function_instance(self, *, node: ast.AST | ObjectNode, func: Function) -> None:  # noqa: D102,ARG002
        self.records.append("on_function_instance")

    def on_function_node(self, *, node: ast.AST | ObjectNode) -> None:  # noqa: D102,ARG002
        self.records.append("on_function_node")

    def on_instance(self, *, node: ast.AST | ObjectNode, obj: Object) -> None:  # noqa: D102,ARG002
        self.records.append("on_instance")

    def on_members(self, *, node: ast.AST | ObjectNode, obj: Object) -> None:  # noqa: D102,ARG002
        self.records.append("on_members")

    def on_module_instance(self, *, node: ast.AST | ObjectNode, mod: Module) -> None:  # noqa: D102,ARG002
        self.records.append("on_module_instance")

    def on_module_members(self, *, node: ast.AST | ObjectNode, mod: Module) -> None:  # noqa: D102,ARG002
        self.records.append("on_module_members")

    def on_module_node(self, *, node: ast.AST | ObjectNode) -> None:  # noqa: D102,ARG002
        self.records.append("on_module_node")

    def on_node(self, *, node: ast.AST | ObjectNode) -> None:  # noqa: D102,ARG002
        self.records.append("on_node")


@pytest.mark.parametrize(
    "extension",
    [
        # with module path
        "tests.test_extensions",
        {"tests.test_extensions": {"option": 0}},
        # with extension path
        "tests.test_extensions.ExtensionTest",
        {"tests.test_extensions.ExtensionTest": {"option": 0}},
        # with filepath
        "tests/test_extensions.py",
        {"tests/test_extensions.py": {"option": 0}},
        # with filepath and extension name
        "tests/test_extensions.py:ExtensionTest",
        {"tests/test_extensions.py:ExtensionTest": {"option": 0}},
        # with instance
        ExtensionTest(option=0),
        # with class
        ExtensionTest,
        # with absolute paths (esp. important to test for Windows)
        Path("tests/test_extensions.py").absolute().as_posix(),
        Path("tests/test_extensions.py:ExtensionTest").absolute().as_posix(),
    ],
)
def test_loading_extensions(extension: str | dict[str, dict[str, Any]] | Extension | type[Extension]) -> None:
    """Test the extensions loading mechanisms.

    Parameters:
        extension: Extension specification (parametrized).
    """
    extensions = load_extensions([extension])
    loaded: ExtensionTest = extensions._extensions[0]  # type: ignore[assignment]
    # We cannot use isinstance here,
    # because loading from a filepath drops the parent `tests` package,
    # resulting in a different object than the present ExtensionTest.
    assert loaded.__class__.__name__ == "ExtensionTest"
    if isinstance(extension, (dict, ExtensionTest)):
        assert loaded.kwargs == {"option": 0}


def test_extension_events() -> None:
    """Test events triggering."""
    extension = ExtensionTest()
    with temporary_visited_module(
        """
        attr = 0
        def func(): ...
        class Class:
            cattr = 1
            def method(self): ...
        """,
        extensions=load_extensions([extension]),
    ):
        pass
    events = [
        "on_attribute_instance",
        "on_attribute_node",
        "on_class_instance",
        "on_class_members",
        "on_class_node",
        "on_function_instance",
        "on_function_node",
        "on_instance",
        "on_members",
        "on_module_instance",
        "on_module_members",
        "on_module_node",
        "on_node",
    ]
    assert set(events) == set(extension.records)
