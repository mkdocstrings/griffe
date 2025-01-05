"""Test visit mechanisms."""

from __future__ import annotations

import sys
from textwrap import dedent

import pytest

from _griffe.enumerations import TypeParameterKind
from _griffe.expressions import Expr
from griffe import GriffeLoader, temporary_pypackage, temporary_visited_module, temporary_visited_package


def test_not_defined_at_runtime() -> None:
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
                """,
            ),
        )
        tmp_package.path.joinpath("module_b.py").write_text("CONST_B = 'hi'\nTYPE_B = str")
        tmp_package.path.joinpath("module_c.py").write_text("CONST_C = 'ho'\nTYPE_C = str")
        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load(tmp_package.name)
        loader.resolve_aliases()
        assert "CONST_B" in package.members
        assert "CONST_C" in package.members
        assert "TYPE_B" not in package.members
        assert "TYPE_C" not in package.members


@pytest.mark.parametrize(
    ("decorator", "labels"),
    [
        ("property", ("property",)),
        ("staticmethod", ("staticmethod",)),
        ("classmethod", ("classmethod",)),
        ("functools.cache", ("cached",)),
        ("cache", ("cached",)),
        ("functools.cached_property", ("cached", "property")),
        ("cached_property", ("cached", "property")),
        ("functools.lru_cache", ("cached",)),
        ("functools.lru_cache(maxsize=8)", ("cached",)),
        ("lru_cache", ("cached",)),
        ("lru_cache(maxsize=8)", ("cached",)),
        ("abc.abstractmethod", ("abstractmethod",)),
        ("abstractmethod", ("abstractmethod",)),
        ("dataclasses.dataclass", ("dataclass",)),
        ("dataclass", ("dataclass",)),
    ],
)
def test_set_function_labels_using_decorators(decorator: str, labels: tuple[str, ...]) -> None:
    """Assert decorators are used to set labels on functions.

    Parameters:
        decorator: A parametrized decorator.
        labels: The parametrized tuple of expected labels.
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
        assert module["A.f"].has_labels(*labels)


@pytest.mark.parametrize(
    ("decorator", "labels"),
    [
        ("dataclasses.dataclass", ("dataclass",)),
        ("dataclass", ("dataclass",)),
    ],
)
def test_set_class_labels_using_decorators(decorator: str, labels: tuple[str, ...]) -> None:
    """Assert decorators are used to set labels on classes.

    Parameters:
        decorator: A parametrized decorator.
        labels: The parametrized tuple of expected labels.
    """
    code = f"""
        import dataclasses
        from dataclasses import dataclass

        @{decorator}
        class A: ...
    """
    with temporary_visited_module(code) as module:
        assert module["A"].has_labels(*labels)


def test_handle_property_setter_and_deleter() -> None:
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
        assert module["A.thing"].has_labels("property", "writable", "deletable")
        assert module["A.thing"].setter.is_function
        assert module["A.thing"].deleter.is_function


@pytest.mark.parametrize(
    "decorator",
    [
        "overload",
        "typing.overload",
    ],
)
def test_handle_typing_overaload(decorator: str) -> None:
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
        assert overloads[0].parameters["path"].annotation.name == "str"
        assert overloads[1].parameters["path"].annotation.name == "Path"
        assert overloads[0].returns.name == "str"
        assert overloads[1].returns.name == "Path"


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
def test_parse_complex__all__assignments(statements: str) -> None:
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
        package = loader.load(tmp_package.name)
        loader.resolve_aliases()

        assert package.exports == {"CONST_INIT", "CONST_A", "CONST_B", "CONST_C"}


def test_dont_crash_on_nested_functions_in_init() -> None:
    """Assert we don't crash when visiting a nested function in `__init__` methods."""
    with temporary_visited_module(
        """
        class C:
            def __init__(self):
                def pl(i: int):
                    return i + 1
        """,
    ) as module:
        assert module


def test_get_correct_docstring_starting_line_number() -> None:
    """Assert we get the correct line numbers for docstring."""
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
        """,
    ) as module:
        assert module.docstring.lineno == 2  # type: ignore[union-attr]
        assert module["C"].docstring.lineno == 6
        assert module["C.method"].docstring.lineno == 10


def test_visit_properties_as_attributes() -> None:
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
        """,
    ) as module:
        assert module["C.prop"].is_attribute
        assert "property" in module["C.prop"].labels
        assert module["C.cached_prop"].is_attribute
        assert "cached" in module["C.cached_prop"].labels


def test_forward_docstrings() -> None:
    """Assert docstrings of class attributes are forwarded to instance assignments.

    This is a regression test for https://github.com/mkdocstrings/griffe/issues/128.
    """
    with temporary_visited_module(
        '''
        class C:
            attr: int
            """This is a non-empty docstring."""

            def __init__(self, attr: int) -> None:
                self.attr = attr
        ''',
    ) as module:
        assert module["C.attr"].docstring


def test_classvar_annotations() -> None:
    """Assert class variable and instance variable annotations are correctly parsed and merged."""
    with temporary_visited_module(
        """
        from typing import ClassVar

        class C:
            w: ClassVar[str] = "foo"
            x: ClassVar[int]
            y: str
            z: int = 5

            def __init__(self) -> None:
                self.a: ClassVar[float]
                self.y = ""
                self.b: bytes
        """,
    ) as module:
        assert module["C.w"].annotation.canonical_path == "str"
        assert module["C.w"].labels == {"class-attribute"}
        assert module["C.w"].value == "'foo'"

        assert module["C.x"].annotation.canonical_path == "int"
        assert module["C.x"].labels == {"class-attribute"}

        assert module["C.y"].annotation.canonical_path == "str"
        assert module["C.y"].labels == {"instance-attribute"}
        assert module["C.y"].value == "''"

        assert module["C.z"].annotation.canonical_path == "int"
        assert module["C.z"].labels == {"class-attribute", "instance-attribute"}
        assert module["C.z"].value == "5"

        # This is syntactically valid, but semantically invalid
        assert module["C.a"].annotation.canonical_path == "typing.ClassVar"
        assert module["C.a"].annotation.slice.canonical_path == "float"
        assert module["C.a"].labels == {"instance-attribute"}

        assert module["C.b"].annotation.canonical_path == "bytes"
        assert module["C.b"].labels == {"instance-attribute"}


def test_visiting_if_statement_in_class_for_type_guards() -> None:
    """Don't fail on various if statements when checking for type-guards."""
    with temporary_visited_module(
        """
        class A:
            if something("string1 string2"):
                class B:
                    pass
        """,
    ) as module:
        assert module["A.B"].runtime


def test_visiting_relative_imports_triggering_cyclic_aliases() -> None:
    """Skip specific imports to avoid cyclic aliases."""
    with temporary_visited_package(
        "pkg",
        {
            "__init__.py": "from . import a",
            "a.py": "from . import b",
            "b.py": "",
        },
    ) as pkg:
        assert "a" not in pkg.imports
        assert "b" in pkg["a"].imports
        assert pkg["a"].imports["b"] == "pkg.b"


def test_parse_attributes_in__all__() -> None:
    """Parse attributes in `__all__`."""
    with temporary_visited_package(
        "package",
        {
            "__init__.py": "from package import module\n__all__ = module.__all__",
            "module.py": "def hello(): ...\n__all__ = ['hello']",
        },
    ) as package:
        assert "hello" in package.exports  # type: ignore[operator]


def test_parse_deep_attributes_in__all__() -> None:
    """Parse deep attributes in `__all__`."""
    with temporary_visited_package(
        "package",
        {
            "__init__.py": "from package import subpackage\n__all__ = subpackage.module.__all__",
            "subpackage/__init__.py": "from package.subpackage import module",
            "subpackage/module.py": "def hello(): ...\n__all__ = ['hello']",
        },
    ) as package:
        assert "hello" in package.exports  # type: ignore[operator]


# YORE: EOL 3.12: Remove block.
# YORE: EOL 3.11: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python less than 3.12 does not have PEP 695 generics")
def test_parse_pep695_generics_without_defaults() -> None:
    """Assert PEP 695 generics are correctly inspected."""
    with temporary_visited_module(
        """
        class Class[X: Exception]: pass
        def func[**P, T, *R](arg: T, *args: P.args, **kwargs: P.kwargs) -> tuple[*R]: pass
        type TA[T: (int, str)] = dict[str, T]
        """,
    ) as module:
        class_ = module["Class"]
        assert class_.is_class
        assert class_.type_parameters[0].name == "X"
        assert class_.type_parameters[0].kind == TypeParameterKind.type_var
        assert class_.type_parameters[0].bound.name == "Exception"
        assert not class_.type_parameters[0].constraints
        assert class_.type_parameters[0].default is None

        func = module["func"]
        assert func.is_function
        assert func.type_parameters[0].name == "P"
        assert func.type_parameters[0].kind == TypeParameterKind.param_spec
        assert func.type_parameters[0].bound is None
        assert not func.type_parameters[0].constraints
        assert func.type_parameters[0].default is None
        assert func.type_parameters[1].name == "T"
        assert func.type_parameters[1].kind == TypeParameterKind.type_var
        assert func.type_parameters[1].bound is None
        assert not func.type_parameters[1].constraints
        assert func.type_parameters[1].default is None
        assert func.type_parameters[2].name == "R"
        assert func.type_parameters[2].kind == TypeParameterKind.type_var_tuple
        assert func.type_parameters[2].bound is None
        assert not func.type_parameters[2].constraints
        assert func.type_parameters[2].default is None

        type_alias = module["TA"]
        assert type_alias.is_type_alias
        assert type_alias.type_parameters[0].name == "T"
        assert type_alias.type_parameters[0].kind == TypeParameterKind.type_var
        assert type_alias.type_parameters[0].bound is None
        assert type_alias.type_parameters[0].constraints[0].name == "int"
        assert type_alias.type_parameters[0].constraints[1].name == "str"
        assert type_alias.type_parameters[0].default is None
        assert isinstance(type_alias.value, Expr)
        assert str(type_alias.value) == "dict[str, T]"


# YORE: EOL 3.12: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 13), reason="Python less than 3.13 does not have defaults in PEP 695 generics")  # fmt: skip
def test_parse_pep695_generics() -> None:
    """Assert PEP 695 generics are correctly parsed."""
    with temporary_visited_module(
        """
        class Class[X: Exception = OSError]: pass
        def func[**P, T, *R](arg: T, *args: P.args, **kwargs: P.kwargs) -> tuple[*R]: pass
        type TA[T: (int, str) = str] = dict[str, T]
        """,
    ) as module:
        class_ = module["Class"]
        assert class_.is_class
        assert class_.type_parameters[0].name == "X"
        assert class_.type_parameters[0].kind == TypeParameterKind.type_var
        assert class_.type_parameters[0].bound.name == "Exception"
        assert not class_.type_parameters[0].constraints
        assert class_.type_parameters[0].default.name == "OSError"

        func = module["func"]
        assert func.is_function
        assert func.type_parameters[0].name == "P"
        assert func.type_parameters[0].kind == TypeParameterKind.param_spec
        assert func.type_parameters[0].bound is None
        assert not func.type_parameters[0].constraints
        assert func.type_parameters[0].default is None
        assert func.type_parameters[1].name == "T"
        assert func.type_parameters[1].kind == TypeParameterKind.type_var
        assert func.type_parameters[1].bound is None
        assert not func.type_parameters[1].constraints
        assert func.type_parameters[1].default is None
        assert func.type_parameters[2].name == "R"
        assert func.type_parameters[2].kind == TypeParameterKind.type_var_tuple
        assert func.type_parameters[2].bound is None
        assert not func.type_parameters[2].constraints
        assert func.type_parameters[2].default is None

        type_alias = module["TA"]
        assert type_alias.is_type_alias
        assert type_alias.type_parameters[0].name == "T"
        assert type_alias.type_parameters[0].kind == TypeParameterKind.type_var
        assert type_alias.type_parameters[0].bound is None
        assert type_alias.type_parameters[0].constraints[0].name == "int"
        assert type_alias.type_parameters[0].constraints[1].name == "str"
        assert type_alias.type_parameters[0].default.name == "str"
        assert isinstance(type_alias.value, Expr)
        assert str(type_alias.value) == "dict[str, T]"
