"""Tests for the `loader` module."""

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
