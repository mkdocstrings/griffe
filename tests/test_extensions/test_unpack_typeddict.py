"""Test the unpack extension."""

from griffe import DocstringSectionKind, load_extensions, temporary_visited_package


def test_typeddict_support() -> None:
    """Test our `TypedDict` support."""
    code = """
        from typing import TypedDict

        class Kwargs(TypedDict):
            a: int
            '''Docstring for a.'''
            b: str
            '''Docstring for b.'''
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("unpack_typeddict"),
    ) as pkg:
        td = pkg["Kwargs"]
    assert "__init__" in td.members
    init = td["__init__"]
    assert len(init.parameters) == 3
    assert "self" in init.parameters
    assert "a" in init.parameters
    assert "b" in init.parameters
    assert str(init.parameters["a"].annotation) == "int"
    assert str(init.parameters["b"].annotation) == "str"
    assert init.parameters["a"].docstring.value == "Docstring for a."
    assert init.parameters["b"].docstring.value == "Docstring for b."
    assert init.returns == "None"


def test_unpack_support() -> None:
    """Test our `Unpack` support."""
    code = """
        from typing import TypedDict, Unpack

        class Kwargs(TypedDict):
            a: int
            '''Docstring for a.'''
            b: str
            '''Docstring for b.'''

        def func(**kwargs: Unpack[Kwargs]) -> None:
            '''A function.

            Parameters:
                **kwargs: The keyword arguments.
            '''
            pass
    """
    with temporary_visited_package(
        "pkg",
        {"__init__.py": code},
        extensions=load_extensions("unpack_typeddict"),
        docstring_parser="google",
    ) as pkg:
        func = pkg["func"]

    assert len(func.parameters) == 2
    assert "a" in func.parameters
    assert "b" in func.parameters
    assert str(func.parameters["a"].annotation) == "int"
    assert str(func.parameters["b"].annotation) == "str"
    assert func.parameters["a"].docstring.value == "Docstring for a."
    assert func.parameters["b"].docstring.value == "Docstring for b."
    assert func.docstring is not None
    params_section = next(
        section for section in func.docstring.parsed if section.kind is DocstringSectionKind.parameters
    )
    assert len(params_section.value) == 2
    param_a = next(param for param in params_section.value if param.name == "a")
    param_b = next(param for param in params_section.value if param.name == "b")
    assert str(param_a.annotation) == "int"
    assert str(param_b.annotation) == "str"
    assert param_a.description == "Docstring for a."
    assert param_b.description == "Docstring for b."
