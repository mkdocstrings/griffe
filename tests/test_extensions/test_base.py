"""Tests for the base extension functionality."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from griffe import (
    Alias,
    Extension,
    GriffeLoader,
    ObjectNode,
    load_extensions,
    temporary_visited_module,
    temporary_visited_package,
)
from griffelib._internal.models import Attribute, Class, Function, Module, Object, TypeAlias

if TYPE_CHECKING:
    import ast

    from griffe import Attribute, Class, Function, Module, Object, ObjectNode, TypeAlias


class AnalysisEventsTest(Extension):  # noqa: D101
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D107
        super().__init__()
        self.records: list[str] = []
        self.args = args
        self.kwargs = kwargs

    def on_attribute_instance(self, *, node: ast.AST | ObjectNode, attr: Attribute, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_attribute_instance")

    def on_attribute_node(self, *, node: ast.AST | ObjectNode, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_attribute_node")

    def on_class_instance(self, *, node: ast.AST | ObjectNode, cls: Class, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_class_instance")

    def on_class_members(self, *, node: ast.AST | ObjectNode, cls: Class, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_class_members")

    def on_class_node(self, *, node: ast.AST | ObjectNode, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_class_node")

    def on_function_instance(self, *, node: ast.AST | ObjectNode, func: Function, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_function_instance")

    def on_function_node(self, *, node: ast.AST | ObjectNode, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_function_node")

    def on_instance(self, *, node: ast.AST | ObjectNode, obj: Object, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_instance")

    def on_members(self, *, node: ast.AST | ObjectNode, obj: Object, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_members")

    def on_module_instance(self, *, node: ast.AST | ObjectNode, mod: Module, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_module_instance")

    def on_module_members(self, *, node: ast.AST | ObjectNode, mod: Module, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_module_members")

    def on_module_node(self, *, node: ast.AST | ObjectNode, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_module_node")

    def on_node(self, *, node: ast.AST | ObjectNode, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_node")

    def on_type_alias_instance(self, *, node: ast.AST | ObjectNode, type_alias: TypeAlias, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_type_alias_instance")

    def on_type_alias_node(self, *, node: ast.AST | ObjectNode, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_type_alias_node")

    def on_alias_instance(self, *, node: ast.AST | ObjectNode, alias: Alias, **kwargs: Any) -> None:  # noqa: D102,ARG002
        self.records.append("on_alias_instance")


@pytest.mark.parametrize(
    "extension",
    [
        # With module path.
        "tests.test_extensions.test_base",
        {"tests.test_extensions.test_base": {"option": 0}},
        # With extension path.
        "tests.test_extensions.test_base.AnalysisEventsTest",
        {"tests.test_extensions.test_base.AnalysisEventsTest": {"option": 0}},
        # With filepath.
        "tests/test_extensions/test_base.py",
        {"tests/test_extensions/test_base.py": {"option": 0}},
        # With filepath and extension name.
        "tests/test_extensions/test_base.py:AnalysisEventsTest",
        {"tests/test_extensions/test_base.py:AnalysisEventsTest": {"option": 0}},
        # With instance.
        AnalysisEventsTest(option=0),
        # With class.
        AnalysisEventsTest,
        # With absolute paths (esp. important to test for Windows).
        Path("tests/test_extensions/test_base.py").absolute().as_posix(),
        Path("tests/test_extensions/test_base.py:AnalysisEventsTest").absolute().as_posix(),
    ],
)
def test_loading_extensions(extension: str | dict[str, dict[str, Any]] | Extension | type[Extension]) -> None:
    """Test the extensions loading mechanisms.

    Parameters:
        extension: Extension specification (parametrized).
    """
    extensions = load_extensions(extension)
    loaded: AnalysisEventsTest = extensions._extensions[0]  # type: ignore[assignment]
    # We cannot use isinstance here,
    # because loading from a filepath drops the parent `tests` package,
    # resulting in a different object than the present ExtensionTest.
    assert loaded.__class__.__name__ == "AnalysisEventsTest"
    if isinstance(extension, (dict, AnalysisEventsTest)):
        assert loaded.kwargs == {"option": 0}


# YORE: EOL 3.11: Remove block.
def test_analysis_events_without_type_aliases() -> None:
    """Test analysis events triggering."""
    extension = AnalysisEventsTest()
    with temporary_visited_module(
        """
        import x
        attr = 0
        def func(): ...
        class Class:
            cattr = 1
            def method(self): ...
        """,
        extensions=load_extensions(extension),
    ):
        pass
    events = [
        "on_alias_instance",
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


# YORE: EOL 3.11: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python less than 3.12 does not have PEP 695 type aliases")
def test_analysis_events() -> None:
    """Test analysis events triggering."""
    extension = AnalysisEventsTest()
    with temporary_visited_module(
        """
        import x
        attr = 0
        def func(): ...
        class Class:
            cattr = 1
            def method(self): ...
        type TypeAlias = list[int]
        """,
        extensions=load_extensions(extension),
    ):
        pass
    events = [
        "on_alias_instance",
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
        "on_type_alias_instance",
        "on_type_alias_node",
    ]
    assert set(events) == set(extension.records)


class LoadEventsTest(Extension):  # noqa: D101
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D107
        super().__init__()
        self.records: list[str] = []
        self.args = args
        self.kwargs = kwargs

    def on_alias(self, *, alias: Alias, loader: GriffeLoader, **kwargs: Any) -> None:  # noqa: ARG002,D102
        self.records.append("on_alias")

    def on_attribute(self, *, attr: Attribute, loader: GriffeLoader, **kwargs: Any) -> None:  # noqa: ARG002,D102
        self.records.append("on_attribute")

    def on_class(self, *, cls: Class, loader: GriffeLoader, **kwargs: Any) -> None:  # noqa: ARG002,D102
        self.records.append("on_class")

    def on_function(self, *, func: Function, loader: GriffeLoader, **kwargs: Any) -> None:  # noqa: ARG002,D102
        self.records.append("on_function")

    def on_module(self, *, mod: Module, loader: GriffeLoader, **kwargs: Any) -> None:  # noqa: ARG002,D102
        self.records.append("on_module")

    def on_object(self, *, obj: Object, loader: GriffeLoader, **kwargs: Any) -> None:  # noqa: ARG002,D102
        self.records.append("on_object")

    def on_package(self, *, pkg: Module, loader: GriffeLoader, **kwargs: Any) -> None:  # noqa: ARG002,D102
        self.records.append("on_package")

    def on_type_alias(self, *, type_alias: TypeAlias, loader: GriffeLoader, **kwargs: Any) -> None:  # noqa: ARG002,D102
        self.records.append("on_type_alias")


# YORE: EOL 3.11: Remove block.
def test_load_events_without_type_aliases() -> None:
    """Test load events triggering."""
    extension = LoadEventsTest()
    with temporary_visited_package(
        "pkg",
        {
            "__init__.py": """
                import x
                attr = 0
                def func(): ...
                class Class:
                    cattr = 1
                    def method(self): ...
            """,
        },
        extensions=load_extensions(extension),
    ):
        pass
    events = [
        "on_alias",
        "on_attribute",
        "on_class",
        "on_function",
        "on_module",
        "on_object",
        "on_package",
    ]
    assert set(events) == set(extension.records)


# YORE: EOL 3.11: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python less than 3.12 does not have PEP 695 type aliases")
def test_load_events() -> None:
    """Test load events triggering."""
    extension = LoadEventsTest()
    with temporary_visited_package(
        "pkg",
        {
            "__init__.py": """
                import x
                attr = 0
                def func(): ...
                class Class:
                    cattr = 1
                    def method(self): ...
                type TypeAlias = list[int]
            """,
        },
        extensions=load_extensions(extension),
    ):
        pass
    events = [
        "on_alias",
        "on_attribute",
        "on_class",
        "on_function",
        "on_module",
        "on_object",
        "on_package",
        "on_type_alias",
    ]
    assert set(events) == set(extension.records)
