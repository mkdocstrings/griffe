"""Test inspection mechanisms."""

from __future__ import annotations

import sys

import pytest

from _griffe.enumerations import TypeParameterKind
from _griffe.expressions import Expr
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


# YORE: EOL 3.12: Remove block.
# YORE: EOL 3.11: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python less than 3.12 does not have PEP 695 generics")
def test_inspecting_pep695_generics_without_defaults() -> None:
    """Assert PEP 695 generics are correctly inspected."""
    with temporary_inspected_module(
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
def test_inspecting_pep695_generics() -> None:
    """Assert PEP 695 generics are correctly inspected."""
    with temporary_inspected_module(
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
