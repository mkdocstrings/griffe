"""Tests for the `dataclasses` module."""

from __future__ import annotations

import sys
from copy import deepcopy
from textwrap import dedent

import pytest

from _griffe.enumerations import TypeParameterKind
from _griffe.models import TypeParameter, TypeParameters
from griffe import (
    Attribute,
    Class,
    Docstring,
    Function,
    GriffeLoader,
    Module,
    NameResolutionError,
    Parameter,
    ParameterKind,
    Parameters,
    module_vtree,
    temporary_inspected_module,
    temporary_pypackage,
    temporary_visited_module,
    temporary_visited_package,
)


def test_submodule_exports() -> None:
    """Check that a module is exported depending on whether it was also imported."""
    root = Module("root")
    sub = Module("sub")
    private = Attribute("_private")
    root["sub"] = sub
    root["_private"] = private

    assert not sub.is_wildcard_exposed
    root.imports["sub"] = "root.sub"
    assert sub.is_wildcard_exposed

    assert not private.is_wildcard_exposed
    root.exports = ["_private"]
    assert private.is_wildcard_exposed


def test_has_docstrings() -> None:
    """Assert the `.has_docstrings` method is recursive."""
    with temporary_visited_module("class A:\n    '''Hello.'''") as module:
        assert module.has_docstrings


def test_has_docstrings_submodules() -> None:
    """Assert the `.has_docstrings` method descends into submodules."""
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

            # These definitions create class variables.
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
            y: float = field(init=True)  # `init=True` has no effect.
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
        assert [p.name for p in point_a.parameters] == ["self", "x", "y", "z"]
        assert list(point_a.members) == ["x", "y", "__init__"]

        point_b = module["PointB"]
        assert [p.name for p in point_b.parameters] == ["self", "r"]
        assert list(point_b.members) == ["x", "y", "z", "__init__"]


def test_visited_module_source() -> None:
    """Check the source property of a module."""
    code = "print('hello')\nprint('world')"
    with temporary_visited_package("package", {"__init__.py": code}) as module:
        assert module.source == code


def test_visited_class_source() -> None:
    """Check the source property of a class."""
    code = """
    class A:
        def __init__(self, x: int):
            self.x = x
    """
    with temporary_visited_package("package", {"__init__.py": code}) as module:
        assert module["A"].source == dedent(code).strip()


def test_visited_object_source_with_missing_line_number() -> None:
    """Check the source property of an object with missing line number."""
    code = """
    class A:
        def __init__(self, x: int):
            self.x = x
    """
    with temporary_visited_package("package", {"__init__.py": code}) as module:
        module["A"].endlineno = None
        assert not module["A"].source
        module["A"].endlineno = 3
        module["A"].lineno = None
        assert not module["A"].source


def test_inspected_module_source() -> None:
    """Check the source property of a module."""
    code = "print('hello')\nprint('world')"
    with temporary_inspected_module(code) as module:
        assert module.source == code


def test_inspected_class_source() -> None:
    """Check the source property of a class."""
    code = """
    class A:
        def __init__(self, x: int):
            self.x = x
    """
    with temporary_inspected_module(code) as module:
        assert module["A"].source == dedent(code).strip()


def test_inspected_object_source_with_missing_line_number() -> None:
    """Check the source property of an object with missing line number."""
    code = """
    class A:
        def __init__(self, x: int):
            self.x = x
    """
    with temporary_inspected_module(code) as module:
        module["A"].endlineno = None
        assert not module["A"].source
        module["A"].endlineno = 3
        module["A"].lineno = None
        assert not module["A"].source


def test_dataclass_parameter_docstrings() -> None:
    """Class parameters should have a docstring attribute."""
    code = """
    from dataclasses import dataclass, InitVar

    @dataclass
    class Base:
        a: int
        "Parameter a"
        b: InitVar[int] = 3
        "Parameter b"

    @dataclass
    class Derived(Base):
        c: float
        d: InitVar[float]
        "Parameter d"
    """

    with temporary_visited_package("package", {"__init__.py": code}) as module:
        base = module["Base"]
        param_self = base.parameters[0]
        param_a = base.parameters[1]
        param_b = base.parameters[2]
        assert param_self.docstring is None
        assert param_a.docstring.value == "Parameter a"
        assert param_b.docstring.value == "Parameter b"

        derived = module["Derived"]
        param_self = derived.parameters[0]
        param_a = derived.parameters[1]
        param_b = derived.parameters[2]
        param_c = derived.parameters[3]
        param_d = derived.parameters[4]
        assert param_self.docstring is None
        assert param_a.docstring.value == "Parameter a"
        assert param_b.docstring.value == "Parameter b"
        assert param_c.docstring is None
        assert param_d.docstring.value == "Parameter d"


def test_attributes_that_have_no_annotations() -> None:
    """Dataclass attributes that have no annotatations are not parameters."""
    code = """
        from dataclasses import dataclass, field

        @dataclass
        class Base:
            a: int
            b: str = field(init=False)
            c = 3  # Class attribute.

        @dataclass
        class Derived(Base):
            a = 1  # No effect on the parameter status of `a`.
            b = "b"  # Inherited non-parameter.
            d: float = 4
    """
    with temporary_visited_package("package", {"__init__.py": code}) as module:
        base_params = [p.name for p in module["Base"].parameters]
        derived_params = [p.name for p in module["Derived"].parameters]
        assert base_params == ["self", "a"]
        assert derived_params == ["self", "a", "d"]


def test_name_resolution() -> None:
    """Name are correctly resolved in the scope of an object."""
    code = """
    module_attribute = 0

    class Class:
        import imported

        class_attribute = 0

        def __init__(self):
            self.instance_attribute = 0

        def method(self):
            local_variable = 0
    """
    with temporary_visited_module(code) as module:
        assert module.resolve("module_attribute") == "module.module_attribute"
        assert module.resolve("Class") == "module.Class"

        assert module["module_attribute"].resolve("Class") == "module.Class"
        with pytest.raises(NameResolutionError):
            module["module_attribute"].resolve("class_attribute")

        assert module["Class"].resolve("module_attribute") == "module.module_attribute"
        assert module["Class"].resolve("imported") == "imported"
        assert module["Class"].resolve("class_attribute") == "module.Class.class_attribute"
        assert module["Class"].resolve("instance_attribute") == "module.Class.instance_attribute"
        assert module["Class"].resolve("method") == "module.Class.method"

        assert module["Class.class_attribute"].resolve("module_attribute") == "module.module_attribute"
        assert module["Class.class_attribute"].resolve("Class") == "module.Class"
        assert module["Class.class_attribute"].resolve("imported") == "imported"
        assert module["Class.class_attribute"].resolve("instance_attribute") == "module.Class.instance_attribute"
        assert module["Class.class_attribute"].resolve("method") == "module.Class.method"

        assert module["Class.instance_attribute"].resolve("module_attribute") == "module.module_attribute"
        assert module["Class.instance_attribute"].resolve("Class") == "module.Class"
        assert module["Class.instance_attribute"].resolve("imported") == "imported"
        assert module["Class.instance_attribute"].resolve("class_attribute") == "module.Class.class_attribute"
        assert module["Class.instance_attribute"].resolve("method") == "module.Class.method"

        assert module["Class.method"].resolve("module_attribute") == "module.module_attribute"
        assert module["Class.method"].resolve("Class") == "module.Class"
        assert module["Class.method"].resolve("imported") == "imported"
        assert module["Class.method"].resolve("class_attribute") == "module.Class.class_attribute"
        assert module["Class.method"].resolve("instance_attribute") == "module.Class.instance_attribute"


def test_set_parameters() -> None:
    """We can set parameters."""
    parameters = Parameters()
    # Does not exist yet.
    parameters["x"] = Parameter(name="x")
    assert "x" in parameters
    # Already exists, by name.
    parameters["x"] = Parameter(name="x")
    assert "x" in parameters
    assert len(parameters) == 1
    # Already exists, by index.
    parameters[0] = Parameter(name="y")
    assert "y" in parameters
    assert len(parameters) == 1


def test_delete_parameters() -> None:
    """We can delete parameters."""
    parameters = Parameters()
    # By name.
    parameters["x"] = Parameter(name="x")
    del parameters["x"]
    assert "x" not in parameters
    assert len(parameters) == 0
    # By index.
    parameters["x"] = Parameter(name="x")
    del parameters[0]
    assert "x" not in parameters
    assert len(parameters) == 0


def test_not_resolving_attribute_value_to_itself() -> None:
    """Attribute values with same name don't resolve to themselves."""
    with temporary_visited_module(
        """
        class A:
            def __init__(self):
                x = "something"
                self.x = x
        """,
    ) as module:
        assert module["A.x"].value.canonical_path == "x"  # Not `module.A.x`.


def test_resolving_never_raises_alias_errors() -> None:
    """Resolving never raises alias errors."""
    with temporary_visited_package(
        "package",
        {
            "__init__.py": """
                from package.mod import pd

                class A:
                    def __init__(self):
                        pass
            """,
            "mod.py": "import pandas as pd",
        },
    ) as module:
        assert module["A.__init__"].resolve("pd") == "package.mod.pd"


def test_building_function_and_class_signatures() -> None:
    """Test the construction of a class/function signature."""
    # Test simple function signatures.
    simple_params = Parameters(
        Parameter("x", annotation="int"),
        Parameter("y", annotation="int", default="0"),
    )
    simple_func = Function("simple_function", parameters=simple_params, returns="int")
    assert simple_func.signature() == "simple_function(x: int, y: int = 0) -> int"

    # Test class signatures.
    init = Function("__init__", parameters=simple_params, returns="None")
    cls = Class("TestClass")
    cls.set_member("__init__", init)
    assert cls.signature() == "TestClass(x: int, y: int = 0)"

    # Create a more complex function with various parameter types.
    params = Parameters(
        Parameter("a", kind=ParameterKind.positional_only),
        Parameter("b", kind=ParameterKind.positional_only, annotation="int", default="0"),
        Parameter("c", kind=ParameterKind.positional_or_keyword),
        Parameter("d", kind=ParameterKind.positional_or_keyword, annotation="str", default="''"),
        Parameter("args", kind=ParameterKind.var_positional),
        Parameter("e", kind=ParameterKind.keyword_only),
        Parameter("f", kind=ParameterKind.keyword_only, annotation="bool", default="False"),
        Parameter("kwargs", kind=ParameterKind.var_keyword),
    )

    func = Function("test_function", parameters=params, returns="None")
    expected = "test_function(a, b: int = 0, /, c, d: str = '', *args, e, f: bool = False, **kwargs) -> None"
    assert func.signature() == expected


def test_set_type_parameters() -> None:
    """We can set type parameters."""
    type_parameters = TypeParameters()
    # Does not exist yet.
    type_parameters["x"] = TypeParameter(name="x", kind=TypeParameterKind.type_var)
    assert "x" in type_parameters
    # Already exists, by name.
    type_parameters["x"] = TypeParameter(name="x", kind=TypeParameterKind.type_var)
    assert "x" in type_parameters
    assert len(type_parameters) == 1
    # Already exists, by name, with different kind.
    type_parameters["x"] = TypeParameter(name="x", kind=TypeParameterKind.param_spec)
    assert "x" in type_parameters
    assert len(type_parameters) == 1
    # Already exists, by index.
    type_parameters[0] = TypeParameter(name="y", kind=TypeParameterKind.type_var)
    assert "y" in type_parameters
    assert len(type_parameters) == 1


def test_delete_type_parameters() -> None:
    """We can delete type parameters."""
    type_parameters = TypeParameters()
    # By name.
    type_parameters["x"] = TypeParameter(name="x", kind=TypeParameterKind.type_var)
    del type_parameters["x"]
    assert "x" not in type_parameters
    assert len(type_parameters) == 0
    # By index.
    type_parameters["x"] = TypeParameter(name="x", kind=TypeParameterKind.type_var)
    del type_parameters[0]
    assert "x" not in type_parameters
    assert len(type_parameters) == 0


# YORE: EOL 3.11: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python less than 3.12 does not have PEP 695 generics")
def test_annotation_resolution() -> None:
    """Names are correctly resolved in the annotation scope of an object."""
    with temporary_visited_module(
        """
        class C[T]:
            class D[T]:
                def func[Y](self, arg1: T, arg2: Y): pass
            def func[Z](arg1: T, arg2: Y): pass
        """,
    ) as module:
        assert module["C.D"].resolve("T") == "module.C.D[T]"

        assert module["C.D.func"].resolve("T") == "module.C.D[T]"
        assert module["C.D.func"].resolve("Y") == "module.C.D.func[Y]"

        assert module["C"].resolve("T") == "module.C[T]"

        assert module["C.func"].resolve("T") == "module.C[T]"
        with pytest.raises(NameResolutionError):
            module["C.func"].resolve("Y")
