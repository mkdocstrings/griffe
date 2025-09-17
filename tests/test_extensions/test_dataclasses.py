"""Test the dataclasses extension."""

from griffe import ParameterKind, load_extensions, temporary_visited_package


def test_dataclass_support() -> None:
    """Test our `dataclass` support."""
    code = """
        from dataclasses import dataclass

        @dataclass
        class Point:
            x: int
            '''Docstring for x.'''
            y: int
            '''Docstring for y.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    assert "__init__" in point.members
    init = point["__init__"]
    assert len(init.parameters) == 3
    assert "self" in init.parameters
    assert "x" in init.parameters
    assert "y" in init.parameters
    assert str(init.parameters["x"].annotation) == "int"
    assert str(init.parameters["y"].annotation) == "int"
    assert init.parameters["x"].docstring.value == "Docstring for x."
    assert init.parameters["y"].docstring.value == "Docstring for y."
    assert init.returns == "None"


def test_non_init_fields() -> None:
    """Test that non-init fields are not included in the `__init__` method."""
    code = """
        from dataclasses import dataclass, field

        @dataclass
        class Point:
            x: int
            '''Docstring for x.'''
            y: int = field(init=False)
            '''Docstring for y.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    assert "__init__" in point.members
    init = point["__init__"]
    assert len(init.parameters) == 2
    assert "self" in init.parameters
    assert "x" in init.parameters
    assert "y" not in init.parameters


def test_classvar_fields() -> None:
    """Test that `ClassVar` fields are not included in the `__init__` method."""
    code = """
        from dataclasses import dataclass
        from typing import ClassVar

        @dataclass
        class Point:
            x: int
            '''Docstring for x.'''
            y: ClassVar[int]
            '''Docstring for y.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    assert "__init__" in point.members
    init = point["__init__"]
    assert len(init.parameters) == 2
    assert "self" in init.parameters
    assert "x" in init.parameters
    assert "y" not in init.parameters


def test_kw_only_fields() -> None:
    """Test that `kw_only` fields are included as keyword-only parameters in the `__init__` method."""
    code = """
        from dataclasses import dataclass, field

        @dataclass
        class Point:
            x: int
            '''Docstring for x.'''
            y: int = field(kw_only=True)
            '''Docstring for y.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    assert "__init__" in point.members
    init = point["__init__"]
    assert len(init.parameters) == 3
    assert "self" in init.parameters
    assert "x" in init.parameters
    assert "y" in init.parameters
    assert init.parameters["y"].kind is ParameterKind.keyword_only


def test_kw_only_sentinel() -> None:
    """Test that the `KW_ONLY` sentinel works."""
    code = """
        from dataclasses import dataclass, KW_ONLY

        @dataclass
        class Point:
            x: int
            '''Docstring for x.'''
            _: KW_ONLY
            y: int
            '''Docstring for y.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    assert "__init__" in point.members
    init = point["__init__"]
    assert len(init.parameters) == 3
    assert "self" in init.parameters
    assert "x" in init.parameters
    assert "y" in init.parameters
    assert init.parameters["y"].kind is ParameterKind.keyword_only


def test_all_kw_only_fields() -> None:
    """Test that all fields can be made keyword-only."""
    code = """
        from dataclasses import dataclass

        @dataclass(kw_only=True)
        class Point:
            x: int
            '''Docstring for x.'''
            y: int
            '''Docstring for y.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("dataclasses"),
    ) as pkg:
        point = pkg["Point"]
    assert "__init__" in point.members
    init = point["__init__"]
    assert len(init.parameters) == 3
    assert "self" in init.parameters
    assert "x" in init.parameters
    assert "y" in init.parameters
    assert init.parameters["x"].kind is ParameterKind.keyword_only
    assert init.parameters["y"].kind is ParameterKind.keyword_only
