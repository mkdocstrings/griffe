"""Test visit mechanisms."""

from textwrap import dedent

import pytest

from griffe.loader import GriffeLoader
from tests.helpers import temporary_pypackage, temporary_visited_module

# import sys
# import hypothesmith as hs
# import libcst
# from hypothesis import given, settings
# @given(hs.from_node(node=libcst.Module))
# @pytest.mark.skipif(sys.version_info >= (3, 11, 0), reason="Too slow on Python 3.11?")
# def test_visit_arbitrary_code(code: str):
#     with temporary_visited_module(code):
#         ...


# TODO: move this in test_nodes once hypothesmith is ready
@pytest.mark.parametrize(
    "expression",
    [
        # operations
        "b + c",
        "b - c",
        "b * c",
        "b / c",
        "b // c",
        "b ** c",
        "b ^ c",
        "b & c",
        "b | c",
        "b @ c",
        "b % c",
        "b >> c",
        "b << c",
        # unary operations
        "+b",
        "-b",
        "~b",
        # comparisons
        "b == c",
        "b >= c",
        "b > c",
        "b <= c",
        "b < c",
        "b != c",
        # boolean logic
        "b and c",
        "b or c",
        "not b",
        # identify
        "b is c",
        "b is not c",
        # membership
        "b in c",
        "b not in c",
    ],
)
def test_building_value_from_nodes(expression):
    """Test building value from AST nodes.

    Parameters:
        expression: An expression (parametrized).
    """
    with temporary_visited_module(f"a = {expression}") as module:
        assert "a" in module.members
        assert module["a"].value == expression


def test_not_defined_at_runtime():
    """Assert that objects not defined at runtime are not added to wildcards expansions."""
    with temporary_pypackage("package", ["module_a.py", "module_b.py", "module_c.py"]) as tmp_package:
        tmp_package.path.joinpath("__init__.py").write_text("from package.module_a import *")
        tmp_package.path.joinpath("module_a.py").write_text(
            dedent(
                """
                import typing
                from typing import TYPE_CHECKING

                from package.module_b import CONST_B
                from package.module_c import CONST_C

                if typing.TYPE_CHECKING:  # always false
                    from package.module_b import TYPE_B
                if TYPE_CHECKING:  # always false
                    from package.module_c import TYPE_C
                """
            )
        )
        tmp_package.path.joinpath("module_b.py").write_text("CONST_B = 'hi'\nTYPE_B = str")
        tmp_package.path.joinpath("module_c.py").write_text("CONST_C = 'ho'\nTYPE_C = str")
        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load_module(tmp_package.name)
        loader.resolve_aliases()
        assert "CONST_B" in package.members
        assert "CONST_C" in package.members
        assert "TYPE_B" not in package.members
        assert "TYPE_C" not in package.members


@pytest.mark.parametrize(
    ("decorator", "label"),
    [
        ("property", "property"),
        ("functools.cache", "cached"),
        ("functools.cached_property", "cached"),
        ("functools.lru_cache", "cached"),
        ("functools.lru_cache(maxsize=8)", "cached"),
        ("cache", "cached"),
        ("cached_property", "cached"),
        ("lru_cache", "cached"),
        ("lru_cache(maxsize=8)", "cached"),
    ],
)
def test_set_labels_using_decorators(decorator, label):
    """Assert decorators are used to set labels on objects.

    Parameters:
        decorator: A parametrized decorator.
        label: The expected, parametrized label.
    """
    code = f"""
        import functools
        from functools import cache, cached_property, lru_cache

        class A:
            @{decorator}
            def f(self):
                return 0
    """
    with temporary_visited_module(code) as module:
        assert label in module["A.f"].labels


def test_handle_property_setter_and_deleter():
    """Assert property setters and deleters are supported."""
    code = """
        class A:
            def __init__(self): self._thing = 0

            @property
            def thing(self): return self._thing

            @thing.setter
            def thing(self, value): self._thing = value

            @thing.deleter
            def thing(self): del self._thing
    """
    with temporary_visited_module(code) as module:
        assert module["A.thing"].has_labels(["property", "writable", "deletable"])
        assert module["A.thing"].setter.is_function
        assert module["A.thing"].deleter.is_function


@pytest.mark.parametrize(
    "decorator",
    [
        "overload",
        "typing.overload",
    ],
)
def test_handle_typing_overaload(decorator):
    """Assert `typing.overload` is supported.

    Parameters:
        decorator: A parametrized overload decorator.
    """
    code = f"""
        import typing
        from typing import overload
        from pathlib import Path

        class A:
            @{decorator}
            def absolute(self, path: str) -> str:
                ...

            @{decorator}
            def absolute(self, path: Path) -> Path:
                ...

            def absolute(self, path: str | Path) -> str | Path:
                ...
    """
    with temporary_visited_module(code) as module:
        overloads = module["A.absolute"].overloads
        assert len(overloads) == 2
        assert overloads[0].parameters["path"].annotation.source == "str"  # noqa: WPS219
        assert overloads[1].parameters["path"].annotation.source == "Path"  # noqa: WPS219
        assert overloads[0].returns.source == "str"
        assert overloads[1].returns.source == "Path"
