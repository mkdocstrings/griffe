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
    ("decorator", "labels"),
    [
        ("property", {"property"}),
        ("staticmethod", {"staticmethod"}),
        ("classmethod", {"classmethod"}),
        ("functools.cache", {"cached"}),
        ("cache", {"cached"}),
        ("functools.cached_property", {"cached", "property"}),
        ("cached_property", {"cached", "property"}),
        ("functools.lru_cache", {"cached"}),
        ("functools.lru_cache(maxsize=8)", {"cached"}),
        ("lru_cache", {"cached"}),
        ("lru_cache(maxsize=8)", {"cached"}),
        ("abc.abstractmethod", {"abstractmethod"}),
        ("abstractmethod", {"abstractmethod"}),
        ("dataclasses.dataclass", {"dataclass"}),
        ("dataclass", {"dataclass"}),
    ],
)
def test_set_function_labels_using_decorators(decorator, labels):
    """Assert decorators are used to set labels on functions.

    Parameters:
        decorator: A parametrized decorator.
        labels: The parametrized set of expected labels.
    """
    code = f"""
        import abc
        import dataclasses
        import functools
        from abc import abstractmethod
        from dataclasses import dataclass
        from functools import cache, cached_property, lru_cache

        class A:
            @{decorator}
            def f(self):
                return 0
    """
    with temporary_visited_module(code) as module:
        assert module["A.f"].has_labels(labels)


@pytest.mark.parametrize(
    ("decorator", "labels"),
    [
        ("dataclasses.dataclass", {"dataclass"}),
        ("dataclass", {"dataclass"}),
    ],
)
def test_set_class_labels_using_decorators(decorator, labels):
    """Assert decorators are used to set labels on classes.

    Parameters:
        decorator: A parametrized decorator.
        labels: The parametrized set of expected labels.
    """
    code = f"""
        import dataclasses
        from dataclasses import dataclass

        @{decorator}
        class A: ...
    """
    with temporary_visited_module(code) as module:
        assert module["A"].has_labels(labels)


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


@pytest.mark.parametrize(
    "statements",
    [
        """__all__ = moda_all + modb_all + modc_all + ["CONST_INIT"]""",
        """__all__ = ["CONST_INIT", *moda_all, *modb_all, *modc_all]""",
        """
        __all__ = ["CONST_INIT"]
        __all__ += moda_all + modb_all + modc_all
        """,
        """
        __all__ = moda_all + modb_all + modc_all
        __all__ += ["CONST_INIT"]
        """,
        """
        __all__ = ["CONST_INIT"]
        __all__ += moda_all
        __all__ += modb_all + modc_all
        """,
    ],
)
def test_parse_complex__all__assignments(statements):
    """Check our ability to expand exports based on `__all__` [augmented] assignments.

    Parameters:
        statements: Parametrized text containing `__all__` [augmented] assignments.
    """
    with temporary_pypackage("package", ["moda.py", "modb.py", "modc.py"]) as tmp_package:
        tmp_package.path.joinpath("moda.py").write_text("CONST_A = 1\n\n__all__ = ['CONST_A']")
        tmp_package.path.joinpath("modb.py").write_text("CONST_B = 1\n\n__all__ = ['CONST_B']")
        tmp_package.path.joinpath("modc.py").write_text("CONST_C = 2\n\n__all__ = ['CONST_C']")
        code = """
            from package.moda import *
            from package.moda import __all__ as moda_all
            from package.modb import *
            from package.modb import __all__ as modb_all
            from package.modc import *
            from package.modc import __all__ as modc_all

            CONST_INIT = 0
        """
        tmp_package.path.joinpath("__init__.py").write_text(dedent(code) + dedent(statements))

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load_module(tmp_package.name)
        loader.resolve_aliases()

        assert package.exports == {"CONST_INIT", "CONST_A", "CONST_B", "CONST_C"}


def test_dont_crash_on_nested_functions_in_init():
    """Assert we don't crash when visiting a nested function in `__init__` methods."""
    with temporary_visited_module(
        """
        class C:
            def __init__(self):
                def pl(i: int):
                    return i + 1
        """
    ) as module:
        assert module


def test_get_correct_docstring_starting_line_number():
    """Assert we get the correct line numbers for docstring, even on Python 3.7."""
    with temporary_visited_module(
        """
        '''
        Module docstring.
        '''
        class C:
            '''
            Class docstring.
            '''
            def method(self):
                '''
                Method docstring.
                '''
        """
    ) as module:
        assert module.docstring.lineno == 2
        assert module["C"].docstring.lineno == 6
        assert module["C.method"].docstring.lineno == 10


def test_visit_properties_as_attributes():
    """Assert properties are created as attributes and not functions."""
    with temporary_visited_module(
        """
        from functools import cached_property

        class C:
            @property
            def prop(self) -> bool:
                return True
            @cached_property
            def cached_prop(self) -> int:
                return 0
        """
    ) as module:
        assert module["C.prop"].is_attribute
        assert "property" in module["C.prop"].labels
        assert module["C.cached_prop"].is_attribute
        assert "cached" in module["C.cached_prop"].labels
