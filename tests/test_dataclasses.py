"""Tests for the `dataclasses` module."""

from __future__ import annotations

from copy import deepcopy
from textwrap import dedent

import pytest

import griffe
from griffe.dataclasses import Docstring, Module
from griffe.loader import GriffeLoader
from griffe.tests import module_vtree, temporary_pypackage, temporary_visited_package


def test_submodule_exports() -> None:
    """Check that a module is exported depending on whether it was also imported."""
    root = Module("root")
    sub = Module("sub")
    root["sub"] = sub

    assert not root.member_is_exported(sub, explicitely=True)
    assert not root.member_is_exported(sub, explicitely=False)

    root.imports["sub"] = "root.sub"
    assert not root.member_is_exported(sub, explicitely=True)
    assert root.member_is_exported(sub, explicitely=False)

    root.exports = {"sub"}
    assert root.member_is_exported(sub, explicitely=True)
    assert root.member_is_exported(sub, explicitely=False)


def test_has_docstrings() -> None:
    """Assert the `.has_docstrings` method is recursive."""
    module = module_vtree("a.b.c.d")
    module["b.c.d"].docstring = Docstring("Hello.")
    assert module.has_docstrings


def test_handle_aliases_chain_in_has_docstrings() -> None:
    """Assert the `.has_docstrings` method can handle aliases chains in members."""
    with temporary_pypackage("package", ["mod_a.py", "mod_b.py"]) as tmp_package:
        mod_a = tmp_package.path / "mod_a.py"
        mod_b = tmp_package.path / "mod_b.py"
        mod_a.write_text("from .mod_b import someobj")
        mod_b.write_text("from somelib import someobj")

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load(tmp_package.name)
        assert not package.has_docstrings
        loader.resolve_aliases(implicit=True)
        assert not package.has_docstrings


def test_has_docstrings_does_not_trigger_alias_resolution() -> None:
    """Assert the `.has_docstrings` method does not trigger alias resolution."""
    with temporary_pypackage("package", ["mod_a.py", "mod_b.py"]) as tmp_package:
        mod_a = tmp_package.path / "mod_a.py"
        mod_b = tmp_package.path / "mod_b.py"
        mod_a.write_text("from .mod_b import someobj")
        mod_b.write_text("from somelib import someobj")

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load(tmp_package.name)
        assert not package.has_docstrings
        assert not package["mod_a.someobj"].resolved


def test_deepcopy() -> None:
    """Assert we can deep-copy object trees."""
    loader = GriffeLoader()
    mod = loader.load("griffe")

    deepcopy(mod)
    deepcopy(mod.as_dict())


def test_alias_proxies() -> None:
    """Assert that the Alias class has all the necessary methods and properties."""
    api = griffe.load("griffe")
    alias_members = set(api["dataclasses.Alias"].all_members.keys())
    for cls in (
        api["dataclasses.Module"],
        api["dataclasses.Class"],
        api["dataclasses.Function"],
        api["dataclasses.Attribute"],
    ):
        for name in cls.all_members:
            if not name.startswith("_") or name.startswith("__"):
                assert name in alias_members


def test_dataclass_properties_and_class_variables() -> None:
    """Don't return properties or class variables as parameters of dataclasses."""
    code = """
        from dataclasses import dataclass
        from functools import cached_property
        from typing import ClassVar

        @dataclass
        class Point:
            x: float
            y: float

            # These definitions create class variables
            r: ClassVar[float]
            s: float = 3
            t: ClassVar[float] = 3

            @property
            def a(self):
                return 0

            @cached_property
            def b(self):
                return 0
    """
    with temporary_visited_package("package", {"__init__.py": code}) as module:
        params = module["Point"].parameters
        assert [p.name for p in params] == ["self", "x", "y", "s"]


@pytest.mark.parametrize(
    "code",
    [
        """
        @dataclass
        class Dataclass:
            x: float
            y: float = field(kw_only=True)

        class Class:
            def __init__(self, x: float, *, y: float): ...
        """,
        """
        @dataclass
        class Dataclass:
            x: float = field(kw_only=True)
            y: float

        class Class:
            def __init__(self, y: float, *, x: float): ...
        """,
        """
        @dataclass
        class Dataclass:
            x: float
            _: KW_ONLY
            y: float

        class Class:
            def __init__(self, x: float, *, y: float): ...
        """,
        """
        @dataclass
        class Dataclass:
            _: KW_ONLY
            x: float
            y: float

        class Class:
            def __init__(self, *, x: float, y: float): ...
        """,
        """
        @dataclass(kw_only=True)
        class Dataclass:
            x: float
            y: float

        class Class:
            def __init__(self, *, x: float, y: float): ...
        """,
    ],
)
def test_dataclass_parameter_kinds(code: str) -> None:
    """Check dataclass and equivalent non-dataclass parameters.

    The parameter kinds for each pair should be the same.

    Parameters:
        code: Python code to visit.
    """
    code = f"from dataclasses import dataclass, field, KW_ONLY\n\n{dedent(code)}"
    with temporary_visited_package("package", {"__init__.py": code}) as module:
        for dataclass_param, regular_param in zip(module["Dataclass"].parameters, module["Class"].parameters):
            assert dataclass_param == regular_param


def test_regular_class_inheriting_dataclass_dont_get_its_own_params() -> None:
    """A regular class inheriting from a dataclass don't have its attributes added to `__init__`."""
    code = """
        from dataclasses import dataclass

        @dataclass
        class Base:
            a: int
            b: str

        @dataclass
        class Derived1(Base):
            c: float

        class Derived2(Base):
            d: float
    """
    with temporary_visited_package("package", {"__init__.py": code}) as module:
        params1 = module["Derived1"].parameters
        params2 = module["Derived2"].parameters
        assert [p.name for p in params1] == ["self", "a", "b", "c"]
        assert [p.name for p in params2] == ["self", "a", "b"]


def test_regular_class_inheriting_dataclass_is_labelled_dataclass() -> None:
    """A regular class inheriting from a dataclass is labelled as a dataclass too."""
    code = """
        from dataclasses import dataclass

        @dataclass
        class Base:
            pass

        class Derived(Base):
            pass
    """
    with temporary_visited_package("package", {"__init__.py": code}) as module:
        obj = module["Derived"]
        assert "dataclass" in obj.labels


def test_fields_with_init_false() -> None:
    """Fields marked with `init=False` are not added to the `__init__` method."""
    code = """
        from dataclasses import dataclass, field

        @dataclass
        class PointA:
            x: float
            y: float
            z: float = field(init=False)

        @dataclass(init=False)
        class PointB:
            x: float
            y: float

        @dataclass(init=False)
        class PointC:
            x: float
            y: float = field(init=True)  # init=True has no effect
    """
    with temporary_visited_package("package", {"__init__.py": code}) as module:
        params_a = module["PointA"].parameters
        params_b = module["PointB"].parameters
        params_c = module["PointC"].parameters

        assert "z" not in params_a
        assert "x" not in params_b
        assert "y" not in params_b
        assert "x" not in params_c
        assert "y" not in params_c


def test_parameters_are_reorderd_to_match_their_kind() -> None:
    """Keyword-only parameters in base class are pushed back to the end of the signature."""
    code = """
        from dataclasses import dataclass

        @dataclass(kw_only=True)
        class Base:
            a: int
            b: str

        @dataclass
        class Reordered(Base):
            b: float
            c: float
    """
    with temporary_visited_package("package", {"__init__.py": code}) as module:
        params_base = module["Base"].parameters
        params_reordered = module["Reordered"].parameters
        assert [p.name for p in params_base] == ["self", "a", "b"]
        assert [p.name for p in params_reordered] == ["self", "b", "c", "a"]
        assert str(params_reordered["b"].annotation) == "float"


def test_parameters_annotated_as_initvar() -> None:
    """Don't return InitVar annotated fields as class members.

    But if __init__ is defined, InitVar has no effect.
    """
    code = """
    from dataclasses import dataclass, InitVar

    @dataclass
    class PointA:
        x: float
        y: float
        z: InitVar[float]

    @dataclass
    class PointB:
        x: float
        y: float
        z: InitVar[float]

        def __init__(self, r: float): ...
    """

    with temporary_visited_package("package", {"__init__.py": code}) as module:
        point_a = module["PointA"]
        assert ["self", "x", "y", "z"] == [p.name for p in point_a.parameters]
        assert ["x", "y", "__init__"] == list(point_a.members)

        point_b = module["PointB"]
        assert ["self", "r"] == [p.name for p in point_b.parameters]
        assert ["x", "y", "z", "__init__"] == list(point_b.members)
