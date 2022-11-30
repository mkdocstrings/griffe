"""Tests for the `merger` module."""

from textwrap import dedent

from griffe.loader import GriffeLoader
from tests.helpers import temporary_pypackage


def test_dont_trigger_alias_resolution_when_merging_stubs():
    """Assert that we don't trigger alias resolution when merging stubs."""
    with temporary_pypackage("package", ["mod.py", "mod.pyi"]) as tmp_package:
        tmp_package.path.joinpath("mod.py").write_text(
            dedent(
                """
                import pathlib

                def f() -> pathlib.Path:
                    return pathlib.Path()
                """
            )
        )
        tmp_package.path.joinpath("mod.pyi").write_text(
            dedent(
                """
                import pathlib

                def f() -> pathlib.Path: ...
                """
            )
        )
        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        loader.load_module(tmp_package.name)


def test_merge_stubs_on_wildcard_imported_objects():
    """Assert that stubs can be merged on wildcard imported objects."""
    with temporary_pypackage("package", ["mod.py", "__init__.pyi"]) as tmp_package:
        tmp_package.path.joinpath("mod.py").write_text(
            dedent(
                """
                class A:
                    def hello(value: int | str) -> int | str:
                        return value
                """
            )
        )
        tmp_package.path.joinpath("__init__.py").write_text("from .mod import *")
        tmp_package.path.joinpath("__init__.pyi").write_text(
            dedent(
                """
                from typing import overload
                class A:
                    @overload
                    def hello(value: int) -> int: ...
                    @overload
                    def hello(value: str) -> str: ...
                """
            )
        )
        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        module = loader.load_module(tmp_package.name)
        assert module["A.hello"].overloads
