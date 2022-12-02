"""Tests for the `loader` module."""

import logging
from textwrap import dedent

from griffe.expressions import Name
from griffe.loader import GriffeLoader
from tests.helpers import temporary_pyfile, temporary_pypackage


def test_has_docstrings_does_not_try_to_resolve_alias():
    """Assert that checkins presence of docstrings does not trigger alias resolution."""
    with temporary_pyfile("""from abc import abstractmethod""") as (module_name, path):
        loader = GriffeLoader(search_paths=[path.parent])
        module = loader.load_module(module_name)
        loader.resolve_aliases()
        assert "abstractmethod" in module.members
        assert not module.has_docstrings


def test_recursive_wildcard_expansion():
    """Assert that wildcards are expanded recursively."""
    with temporary_pypackage("package", ["mod_a/mod_b/mod_c.py"]) as tmp_package:
        mod_a_dir = tmp_package.path / "mod_a"
        mod_b_dir = mod_a_dir / "mod_b"
        mod_a = mod_a_dir / "__init__.py"
        mod_b = mod_b_dir / "__init__.py"
        mod_c = mod_b_dir / "mod_c.py"
        mod_c.write_text("CONST_X = 'X'\nCONST_Y = 'Y'")
        mod_b.write_text("from .mod_c import *")
        mod_a.write_text("from .mod_b import *")

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load_module(tmp_package.name)

        assert "CONST_X" in package["mod_a.mod_b.mod_c"].members
        assert "CONST_Y" in package["mod_a.mod_b.mod_c"].members

        assert "CONST_X" not in package.members
        assert "CONST_Y" not in package.members

        loader.expand_wildcards(package)

        assert "CONST_X" in package["mod_a"].members
        assert "CONST_Y" in package["mod_a"].members
        assert "CONST_X" in package["mod_a.mod_b"].members
        assert "CONST_Y" in package["mod_a.mod_b"].members


def test_dont_shortcut_alias_chain_after_expanding_wildcards():
    """Assert public aliases paths are not resolved to canonical paths when expanding wildcards."""
    with temporary_pypackage("package", ["mod_a.py", "mod_b.py", "mod_c.py"]) as tmp_package:
        mod_a = tmp_package.path / "mod_a.py"
        mod_b = tmp_package.path / "mod_b.py"
        mod_c = tmp_package.path / "mod_c.py"

        mod_a.write_text("from package.mod_b import *\nclass Child(Base): ...\n")
        mod_b.write_text("from package.mod_c import Base\n__all__ = ['Base']\n")
        mod_c.write_text("class Base: ...\n")

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load_module(tmp_package.name)
        loader.resolve_aliases()
        child = package["mod_a.Child"]
        assert child.bases
        base = child.bases[0]
        assert isinstance(base, Name)
        assert base.source == "Base"
        assert base.full == "package.mod_b.Base"


def test_dont_overwrite_lower_member_when_expanding_wildcard():
    """Check that we don't overwrite a member defined after the import when expanding a wildcard."""
    with temporary_pypackage("package", ["mod_a.py", "mod_b.py"]) as tmp_package:
        mod_a = tmp_package.path / "mod_a.py"
        mod_b = tmp_package.path / "mod_b.py"

        mod_a.write_text("overwritten = 0\nfrom package.mod_b import *\nnot_overwritten = 0\n")
        mod_b.write_text("overwritten = 1\nnot_overwritten = 1\n")

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load_module(tmp_package.name)
        loader.resolve_aliases()
        assert package["mod_a.overwritten"].value == "1"
        assert package["mod_a.not_overwritten"].value == "0"


def test_load_data_from_stubs():
    """Check that the loader is able to load data from stubs / `*.pyi` files."""
    with temporary_pypackage("package", ["_rust_notify.pyi"]) as tmp_package:
        # code taken from samuelcolvin/watchfiles project
        code = '''
            from typing import List, Literal, Optional, Protocol, Set, Tuple, Union

            __all__ = 'RustNotify', 'WatchfilesRustInternalError'

            class AbstractEvent(Protocol):
                def is_set(self) -> bool: ...

            class RustNotify:
                """
                Interface to the Rust [notify](https://crates.io/crates/notify) crate which does
                the heavy lifting of watching for file changes and grouping them into a single event.
                """

                def __init__(self, watch_paths: List[str], debug: bool) -> None:
                    """
                    Create a new RustNotify instance and start a thread to watch for changes.

                    `FileNotFoundError` is raised if one of the paths does not exist.

                    Args:
                        watch_paths: file system paths to watch for changes, can be directories or files
                        debug: if true, print details about all events to stderr
                    """
        '''
        tmp_package.path.joinpath("_rust_notify.pyi").write_text(dedent(code))
        tmp_package.path.joinpath("__init__.py").write_text(
            "from ._rust_notify import RustNotify\n__all__ = ['RustNotify']"
        )
        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load_module(tmp_package.name)
        loader.resolve_aliases()

        assert "_rust_notify" in package.members
        assert "RustNotify" in package.members
        assert package["RustNotify"].resolved


def test_load_from_both_py_and_pyi_files():
    """Check that the loader is able to merge data loaded from `*.py` and `*.pyi` files."""
    with temporary_pypackage("package", ["mod.py", "mod.pyi"]) as tmp_package:
        tmp_package.path.joinpath("mod.py").write_text(
            dedent(
                """
                CONST = 0

                class Class:
                    class_attr = True

                    def function1(self, arg1):
                        pass

                    def function2(self, arg1=2.2):
                        pass
                """
            )
        )
        tmp_package.path.joinpath("mod.pyi").write_text(
            dedent(
                """
                from typing import Sequence, overload

                CONST: int

                class Class:
                    class_attr: bool

                    @overload
                    def function1(self, arg1: str) -> Sequence[str]: ...
                    @overload
                    def function1(self, arg1: bytes) -> Sequence[bytes]: ...

                    def function2(self, arg1: float) -> float: ...
                """
            )
        )
        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load_module(tmp_package.name)
        loader.resolve_aliases()

        assert "mod" in package.members
        mod = package["mod"]
        assert mod.filepath.suffix == ".py"

        assert "CONST" in mod.members
        const = mod["CONST"]
        assert const.value == "0"
        assert const.annotation.source == "int"

        assert "Class" in mod.members
        class_ = mod["Class"]

        assert "class_attr" in class_.members
        class_attr = class_["class_attr"]
        assert class_attr.value == "True"
        assert class_attr.annotation.source == "bool"

        assert "function1" in class_.members
        function1 = class_["function1"]
        assert len(function1.overloads) == 2

        assert "function2" in class_.members
        function2 = class_["function2"]
        assert function2.returns.source == "float"
        assert function2.parameters["arg1"].annotation.source == "float"
        assert function2.parameters["arg1"].default == "2.2"


def test_overwrite_module_with_attribute():
    """Check we are able to overwrite a module with an attribute."""
    with temporary_pypackage("package", ["mod.py"]) as tmp_package:
        tmp_package.path.joinpath("mod.py").write_text("mod: list = [0, 1, 2]")
        tmp_package.path.joinpath("__init__.py").write_text("from package.mod import *")
        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        loader.load_module(tmp_package.name)
        loader.resolve_aliases()


def test_load_package_from_both_py_and_pyi_files():
    """Check that the loader is able to merge a package loaded from `*.py` and `*.pyi` files.

    This is a special case of the previous test: where the package itself has a top level
    `__init__.pyi` (not so uncommon).
    """
    with temporary_pypackage("package", ["__init__.py", "__init__.pyi"]) as tmp_package:
        tmp_package.path.joinpath("__init__.py").write_text("globals()['f'] = lambda x: str(x)")
        tmp_package.path.joinpath("__init__.pyi").write_text("def f(x: int) -> str: ...")

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load_module(tmp_package.name)
        assert "f" in package.members


def test_load_single_module_from_both_py_and_pyi_files():
    """Check that the loader is able to merge a single-module package loaded from `*.py` and `*.pyi` files.

    This is a special case of the previous test: where  the package is a single module
    distribution that also drops a `.pyi` file in site-packages.
    """
    with temporary_pypackage("just_a_folder", ["mod.py", "mod.pyi"]) as tmp_folder:
        tmp_folder.path.joinpath("__init__.py").unlink()
        tmp_folder.path.joinpath("mod.py").write_text("globals()['f'] = lambda x: str(x)")
        tmp_folder.path.joinpath("mod.pyi").write_text("def f(x: int) -> str: ...")

        loader = GriffeLoader(search_paths=[tmp_folder.path])
        package = loader.load_module("mod")
        assert "f" in package.members


def test_unsupported_item_in_all(caplog):
    """Check that unsupported items in `__all__` log a warning.

    Parameters:
        caplog: Pytest fixture to capture logs.
    """
    item_name = "XXX"
    with temporary_pypackage("package", ["mod.py"]) as tmp_folder:
        tmp_folder.path.joinpath("__init__.py").write_text(f"from .mod import {item_name}\n__all__ = [{item_name}]")
        tmp_folder.path.joinpath("mod.py").write_text(f"class {item_name}: ...")
        loader = GriffeLoader(search_paths=[tmp_folder.tmpdir])
        loader.expand_exports(loader.load_module("package"))
    assert any(item_name in record.message and record.levelname == "WARNING" for record in caplog.records)


def test_skip_modules_with_dots_in_filename(caplog):
    """Check that modules with dots in their filenames are skipped.

    Parameters:
        caplog: Pytest fixture to capture logs.
    """
    caplog.set_level(logging.DEBUG)
    with temporary_pypackage("package", ["gunicorn.conf.py"]) as tmp_folder:
        loader = GriffeLoader(search_paths=[tmp_folder.tmpdir])
        loader.load_module("package")
    assert any("gunicorn.conf.py" in record.message and record.levelname == "DEBUG" for record in caplog.records)


def test_nested_namespace_packages():
    """Load a deeply nested namespace package."""
    with temporary_pypackage("a/b/c/d", ["mod.py"]) as tmp_folder:
        loader = GriffeLoader(search_paths=[tmp_folder.tmpdir])
        a_package = loader.load_module("a")
        assert "b" in a_package.members
        b_package = a_package.members["b"]
        assert "c" in b_package.members
        c_package = b_package.members["c"]
        assert "d" in c_package.members
        d_package = c_package.members["d"]
        assert "mod" in d_package.members


def test_multiple_nested_namespace_packages():
    """Load a deeply nested namespace package appearing in several places."""
    with temporary_pypackage("a/b/c/d", ["mod1.py"], init=False) as tmp_ns1:
        with temporary_pypackage("a/b/c/d", ["mod2.py"], init=False) as tmp_ns2:
            with temporary_pypackage("a/b/c/d", ["mod3.py"], init=False) as tmp_ns3:
                tmp_namespace_pkgs = [tmp_ns.tmpdir for tmp_ns in (tmp_ns1, tmp_ns2, tmp_ns3)]
                loader = GriffeLoader(search_paths=tmp_namespace_pkgs)

                a_package = loader.load_module("a")
                for tmp_ns in tmp_namespace_pkgs:
                    assert tmp_ns.joinpath("a") in a_package.filepath
                assert "b" in a_package.members

                b_package = a_package.members["b"]
                for tmp_ns in tmp_namespace_pkgs:  # noqa: WPS440
                    assert tmp_ns.joinpath("a/b") in b_package.filepath
                assert "c" in b_package.members

                c_package = b_package.members["c"]
                for tmp_ns in tmp_namespace_pkgs:  # noqa: WPS440
                    assert tmp_ns.joinpath("a/b/c") in c_package.filepath
                assert "d" in c_package.members

                d_package = c_package.members["d"]
                for tmp_ns in tmp_namespace_pkgs:  # noqa: WPS440
                    assert tmp_ns.joinpath("a/b/c/d") in d_package.filepath
                assert "mod1" in d_package.members
                assert "mod2" in d_package.members
                assert "mod3" in d_package.members


def test_stop_at_first_package_inside_namespace_package():
    """Stop loading similar paths once we found a non-namespace package."""
    with temporary_pypackage("a/b/c/d", ["mod1.py"], init=True) as tmp_ns1:
        with temporary_pypackage("a/b/c/d", ["mod2.py"], init=True) as tmp_ns2:
            tmp_namespace_pkgs = [tmp_ns.tmpdir for tmp_ns in (tmp_ns1, tmp_ns2)]
            loader = GriffeLoader(search_paths=tmp_namespace_pkgs)

            a_package = loader.load_module("a")
            assert "b" in a_package.members

            b_package = a_package.members["b"]
            assert "c" in b_package.members

            c_package = b_package.members["c"]
            assert "d" in c_package.members

            d_package = c_package.members["d"]
            assert d_package.is_subpackage
            assert d_package.filepath == tmp_ns1.tmpdir.joinpath("a/b/c/d/__init__.py")
            assert "mod1" in d_package.members
            assert "mod2" not in d_package.members


def test_load_builtin_modules():
    """Assert builtin/compiled modules can be loaded."""
    loader = GriffeLoader()
    loader.load_module("_ast")
    loader.load_module("_collections")
    loader.load_module("_json")
    assert "_ast" in loader.modules_collection
    assert "_collections" in loader.modules_collection
    assert "_json" in loader.modules_collection


def test_resolve_aliases_of_builtin_modules():
    """Assert builtin/compiled modules can be loaded."""
    loader = GriffeLoader()
    loader.load_module("io")
    loader.load_module("_io")
    unresolved, _ = loader.resolve_aliases(external=True, implicit=True, max_iterations=1)
    io_unresolved = {un for un in unresolved if un.startswith(("io", "_io"))}
    assert len(io_unresolved) < 5
