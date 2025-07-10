"""Test inspection mechanisms."""

from __future__ import annotations

import sys

import pytest

from griffe import inspect, temporary_inspected_module, temporary_inspected_package, temporary_pypackage
from tests.helpers import clear_sys_modules


def test_annotations_from_builtin_types() -> None:
    """Assert builtin types are correctly transformed to annotations."""
    with temporary_inspected_module("def func(a: int) -> str: pass") as module:
        func = module["func"]
        assert func.parameters[0].name == "a"
        assert func.parameters[0].annotation.name == "int"
        assert func.returns.name == "str"


def test_annotations_from_classes() -> None:
    """Assert custom classes are correctly transformed to annotations."""
    with temporary_inspected_module("class A: pass\ndef func(a: A) -> A: pass") as module:
        func = module["func"]
        assert func.parameters[0].name == "a"
        param = func.parameters[0].annotation
        assert param.name == "A"
        assert param.canonical_path == f"{module.name}.A"
        returns = func.returns
        assert returns.name == "A"
        assert returns.canonical_path == f"{module.name}.A"


# YORE: EOL 3.13: Remove block.
# YORE: EOL 3.9: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 10), reason="Type unions not supported on 3.9")
@pytest.mark.skipif(sys.version_info >= (3, 14), reason="3.14 changes type annotations, see test below")
@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        ("tuple[int, str]", "tuple[int, str]"),
        ("Union[int, str]", "typing.Union[int, str]"),
        ("int | str", "int | str"),
        ("int | Literal[1]", "typing.Union[int, typing.Literal[1]]"),
    ],
)
def test_annotations_from_types_before_314(annotation: str, expected: str) -> None:
    """Assert annotations are correctly converted to string."""
    with temporary_inspected_module(
        f"""
        from typing import Literal, Union
        def func(param: {annotation}): ...
        """,
    ) as module:
        param = module["func"].parameters["param"]
        assert str(param.annotation) == expected


# YORE: EOL 3.13: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 14), reason="3.14 modernizes type unions")
@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        ("tuple[int, str]", "tuple[int, str]"),
        ("Union[int, str]", "int | str"),
        ("int | str", "int | str"),
        ("int | Literal[1]", "int | typing.Literal[1]"),
    ],
)
def test_annotations_from_types(annotation: str, expected: str) -> None:
    """Assert annotations are correctly converted to string."""
    with temporary_inspected_module(
        f"""
        from typing import Literal, Union
        def func(param: {annotation}): ...
        """,
    ) as module:
        param = module["func"].parameters["param"]
        assert str(param.annotation) == expected


def test_class_level_imports() -> None:
    """Assert annotations using class-level imports are resolved."""
    with temporary_inspected_module(
        """
        class A:
            from io import StringIO
            def method(self, p: StringIO):
                pass
        """,
    ) as module:
        method = module["A.method"]
        name = method.parameters["p"].annotation
        assert name.name == "StringIO"
        assert name.canonical_path == "io.StringIO"


def test_missing_dependency() -> None:
    """Assert missing dependencies are handled during dynamic imports."""
    with (
        pytest.raises(ImportError, match="ModuleNotFoundError: No module named 'missing'"),
        temporary_inspected_module("import missing"),
    ):
        pass


def test_inspect_properties_as_attributes() -> None:
    """Assert properties are created as attributes and not functions."""
    with temporary_inspected_module(
        """
        try:
            from functools import cached_property
        except ImportError:
            from cached_property import cached_property

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


def test_inspecting_module_importing_other_module() -> None:
    """Assert aliases to modules are correctly inspected and aliased."""
    with temporary_inspected_module("import itertools as it") as module:
        assert module["it"].is_alias
        assert module["it"].target_path == "itertools"


def test_inspecting_parameters_with_functions_as_default_values() -> None:
    """Assert functions as default parameter values are serialized with their name."""
    with temporary_inspected_module("def func(): ...\ndef other_func(f=func): ...") as module:
        default = module["other_func"].parameters["f"].default
    assert default == "func"


def test_inspecting_package_and_module_with_same_names() -> None:
    """Package and module having same name shouldn't cause issues."""
    with temporary_inspected_package("package", {"package.py": "a = 0"}):
        pass


def test_inspecting_module_with_submodules() -> None:
    """Inspecting a module shouldn't register any of its submodules if they're not imported."""
    with temporary_pypackage("pkg", ["mod.py"]) as tmp_package:
        pkg = inspect("pkg", filepath=tmp_package.path / "__init__.py")
    assert "mod" not in pkg.members
    clear_sys_modules("pkg")


def test_inspecting_module_with_imported_submodules() -> None:
    """When inspecting a package on the disk, direct submodules should be skipped entirely."""
    with temporary_pypackage(
        "pkg",
        {
            "__init__.py": "from pkg import subpkg\nfrom pkg.subpkg import mod",
            "subpkg/__init__.py": "a = 0",
            "subpkg/mod.py": "b = 0",
        },
    ) as tmp_package:
        pkg = inspect("pkg", filepath=tmp_package.path / "__init__.py")
    assert "subpkg" not in pkg.members
    assert "mod" in pkg.members
    assert pkg["mod"].is_alias
    assert pkg["mod"].target_path == "pkg.subpkg.mod"
    clear_sys_modules("pkg")


def test_inspecting_objects_from_private_builtin_stdlib_moduless() -> None:
    """Inspect objects from private built-in modules in the standard library."""
    ast = inspect("ast")
    assert "Assign" in ast.members
    assert not ast["Assign"].is_alias

    ast = inspect("_ast")
    assert "Assign" in ast.members
    assert not ast["Assign"].is_alias


def test_inspecting_partials_as_functions() -> None:
    """Assert partials are correctly inspected as functions."""
    with temporary_inspected_module(
        """
        from functools import partial
        def func(a: int, b: int) -> int: pass
        partial_func = partial(func, 1)
        partial_func.__module__ = __name__
        """,
    ) as module:
        partial_func = module["partial_func"]
        assert partial_func.is_function
        assert partial_func.parameters[0].name == "b"
        assert partial_func.parameters[0].annotation.name == "int"
        assert partial_func.returns.name == "int"


def test_inspecting_class_instance() -> None:
    """Assert class instances are correctly inspected."""
    with temporary_inspected_package(
        "pkg",
        {
            "__init__.py": "",
            "foo.py": "from . import bar\nx = bar.X()",
            "bar.py": "class X: pass",
        },
    ) as tmp_package:
        assert not tmp_package["foo.x"].is_alias


def test_inheriting_self_from_parent_class() -> None:
    """Inspect self only once when inheriting it from parent class."""
    with temporary_inspected_module(
        """
        class A: ...
        class B(A): ...

        A.B = B
        """,
    ) as module:
        assert "B" in module["A"].members
        assert "B" in module["B"].all_members
        # Continue indefinitely.
        assert "B" in module["A.B"].all_members
        assert "B" in module["B.B"].all_members
        assert "B" in module["A.B.B"].all_members
        assert "B" in module["B.B.B"].all_members
        # All resolve to A.B.
        assert module["A.B.B"].final_target is module["A.B"]
        assert module["B.B.B"].final_target is module["A.B"]
        assert module["A.B.B.B"].final_target is module["A.B"]
        assert module["B.B.B.B"].final_target is module["A.B"]
