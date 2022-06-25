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
