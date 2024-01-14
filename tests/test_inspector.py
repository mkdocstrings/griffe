"""Test inspection mechanisms."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from griffe.agents.inspector import inspect
from griffe.tests import temporary_inspected_module, temporary_pypackage


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
    with temporary_pypackage("package", ["module.py"]) as tmp_package:
        filepath = Path(tmp_package.path, "module.py")
        filepath.write_text("import missing")
        with pytest.raises(ImportError, match="ModuleNotFoundError: No module named 'missing'"):
            inspect("package.module", filepath=filepath, import_paths=[tmp_package.tmpdir])
    sys.modules.pop("package", None)
    sys.modules.pop("package.module", None)


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
    with temporary_pypackage("package", {"package.py": "a = 0"}) as tmp_package:
        inspect("package.package", filepath=Path(tmp_package.path, "package.py"), import_paths=[tmp_package.tmpdir])
    sys.modules.pop("package", None)
    sys.modules.pop("package.package", None)
