"""Tests for class inheritance."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pytest

from griffe.collections import ModulesCollection
from griffe.tests import temporary_inspected_module, temporary_visited_module

if TYPE_CHECKING:
    from griffe.dataclasses import Class


def _mro_paths(cls: Class) -> list[str]:
    return [base.path for base in cls.mro()]


@pytest.mark.parametrize("agent1", [temporary_visited_module, temporary_inspected_module])
@pytest.mark.parametrize("agent2", [temporary_visited_module, temporary_inspected_module])
def test_loading_inherited_members(agent1: Callable, agent2: Callable) -> None:
    """Test basic class inheritance.

    Parameters:
        agent1: A parametrized agent to load a module.
        agent2: A parametrized agent to load a module.
    """
    code1 = """
        class A:
            attr_from_a = 0
            def method_from_a(self): ...

        class B(A):
            attr_from_a = 1
            attr_from_b = 1
            def method_from_b(self): ...
    """
    code2 = """
        from module1 import B

        class C(B):
            attr_from_c = 2
            def method_from_c(self): ...

        class D(C):
            attr_from_a = 3
            attr_from_d = 3
            def method_from_d(self): ...
    """
    inspection_options = {}
    collection = ModulesCollection()

    with agent1(code1, module_name="module1", modules_collection=collection) as module1:
        if agent2 is temporary_inspected_module:
            inspection_options["import_paths"] = [module1.filepath.parent]

        with agent2(code2, module_name="module2", modules_collection=collection, **inspection_options) as module2:
            classa = module1["A"]
            classb = module1["B"]
            classc = module2["C"]
            classd = module2["D"]

            assert classa in classb.resolved_bases
            assert classb in classc.resolved_bases
            assert classc in classd.resolved_bases

            classd_mro = classd.mro()
            assert classa in classd_mro
            assert classb in classd_mro
            assert classc in classd_mro

            inherited_members = classd.inherited_members
            assert "attr_from_a" not in inherited_members  # overwritten
            assert "attr_from_b" in inherited_members
            assert "attr_from_c" in inherited_members
            assert "attr_from_d" not in inherited_members  # own-declared

            assert "method_from_a" in inherited_members
            assert "method_from_b" in inherited_members
            assert "method_from_c" in inherited_members
            assert "method_from_d" not in inherited_members  # own-declared

            assert "attr_from_b" in classd.all_members


@pytest.mark.parametrize("agent", [temporary_visited_module, temporary_inspected_module])
def test_nested_class_inheritance(agent: Callable) -> None:
    """Test nested class inheritance.

    Parameters:
        agent: A parametrized agent to load a module.
    """
    code = """
        class A:
            class B:
                attr_from_b = 0

        class C(A.B):
            attr_from_c = 1
    """
    with agent(code) as module:
        assert "attr_from_b" in module["C"].inherited_members

    code = """
        class OuterA:
            class Inner: ...
        class OuterB(OuterA):
            class Inner(OuterA.Inner): ...
        class OuterC(OuterA):
            class Inner(OuterA.Inner): ...
        class OuterD(OuterC):
            class Inner(OuterC.Inner, OuterB.Inner): ...
    """
    with temporary_visited_module(code) as module:
        assert _mro_paths(module["OuterD.Inner"]) == [
            "module.OuterC.Inner",
            "module.OuterB.Inner",
            "module.OuterA.Inner",
        ]


@pytest.mark.parametrize(
    ("classes", "cls", "expected_mro"),
    [
        (["A", "B(A)"], "B", ["A"]),
        (["A", "B(A)", "C(A)", "D(B, C)"], "D", ["B", "C", "A"]),
        (["A", "B(A)", "C(A)", "D(C, B)"], "D", ["C", "B", "A"]),
        (["A(Z)"], "A", []),
        (["A(str)"], "A", []),
        (["A", "B(A)", "C(B)", "D(C)"], "D", ["C", "B", "A"]),
        (["A", "B(A)", "C(B)", "D(C)", "E(A)", "F(B)", "G(F, E)", "H(G, D)"], "H", ["G", "F", "D", "C", "B", "E", "A"]),
        (["A", "B(A[T])", "C(B[T])"], "C", ["B", "A"]),
    ],
)
def test_computing_mro(classes: list[str], cls: str, expected_mro: list[str]) -> None:
    """Test computing MRO.

    Parameters:
        classes: A list of classes inheriting from each other.
        cls: The class to compute the MRO of.
        expected_mro: The expected computed MRO.
    """
    code = "class " + ": ...\nclass ".join(classes) + ": ..."
    with temporary_visited_module(code) as module:
        assert _mro_paths(module[cls]) == [f"module.{base}" for base in expected_mro]


@pytest.mark.parametrize(
    ("classes", "cls"),
    [
        (["A", "B(A, A)"], "B"),
        (["A(D)", "B", "C(A, B)", "D(C)"], "D"),
    ],
)
def test_uncomputable_mro(classes: list[str], cls: str) -> None:
    """Test uncomputable MRO.

    Parameters:
        classes: A list of classes inheriting from each other.
        cls: The class to compute the MRO of.
    """
    code = "class " + ": ...\nclass ".join(classes) + ": ..."
    with temporary_visited_module(code) as module, pytest.raises(ValueError, match="Cannot compute C3 linearization"):
        _mro_paths(module[cls])


def test_dynamic_base_classes() -> None:
    """Test dynamic base classes."""
    code = """
        from collections import namedtuple
        class A(namedtuple("B", "attrb")):
            attra = 0
    """
    with temporary_visited_module(code) as module:
        assert _mro_paths(module["A"]) == []  # not supported

    with temporary_inspected_module(code) as module:
        assert _mro_paths(module["A"]) == []  # not supported either
